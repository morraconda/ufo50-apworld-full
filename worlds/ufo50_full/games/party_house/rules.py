"""Party House access logic + CollectionState/world glue.

Every function up to ``_popularity_reachable`` takes only hashable arguments
(``PartyState`` / ``frozenset[str]`` of held guest names / ``str`` scenario / ``int``)
and is a pure function of them -- no ``CollectionState``, no ``world``, no I/O. The
heavier ones are wrapped with ``memoize`` (an unbounded ``lru_cache``, defined below)
so repeat calls with the same arguments -- extremely common during generation, since
many locations across many scenarios share the same underlying resource state -- are
O(1) instead of re-ranking the guest list from scratch.

From ``_PER_ITEM`` on, this module turns a ``(state, world)`` pair into the hashable
``(PartyState, held-guest-names)`` key the pure logic above is written against, and
wires the resulting (already-cached) rules into the AP location graph via
``create_rules``.

Caching is safe here because every memoized function's result depends only on its
arguments, never on when it's called or what CollectionState object it came from --
the same ``(scenario, ps, held)`` always means the same answer. Extraction itself
(``party_state`` / ``guests_held``) is NOT cached: ``CollectionState`` is mutated in
place during a sweep, so caching on it (e.g. by ``id()``) would go stale. It's cheap
enough (a handful of dict lookups) to redo on every call; what's expensive -- the
scenario-by-scenario guest ranking/sorting in ``adjusted_scores`` and everything built
on it -- is exactly what the cache below collapses to O(1) on repeat.
"""
import math
from bisect import bisect_right
from functools import lru_cache
from typing import NamedTuple, TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import add_rule, set_rule

from .items import (GUESTS, SCENARIO_GUESTS, MAX_TROUBLE, SHOP_STOCK, MAX_POPULARITY,
                    MAX_CASH, DAY, START_POPULARITY, START_CASH, item_table)
from .locations import (SCENARIOS, FIXED_SCENARIOS, HOUSE_SPACE_MAX, CLEAR_STAR_GUESTS,
                        GAME_NAME, POPULARITY, HOUSE_SPACE, STAR_GUESTS, CASH,
                        location_table)

if TYPE_CHECKING:
    from ... import UFO50World


def memoize(fn):
    """Unbounded ``lru_cache``. Every decorated function below takes small hashable
    arguments (``PartyState`` / ``frozenset`` / ``str`` / ``int``) and is a pure
    function of them, so one process-wide cache per function is safe and never goes
    stale -- a given argument combination always produces the same result."""
    return lru_cache(maxsize=None)(fn)


class PartyState(NamedTuple):
    max_popularity: int
    max_cash: int
    max_trouble: int
    days: int
    shop_stock: int
    starting_popularity: int
    starting_cash: int

BASE_STATE = PartyState(
    max_popularity=10,
    max_cash=2,
    max_trouble=0,
    days=5,
    shop_stock=1,
    starting_popularity=0,
    starting_cash=0,
)


@memoize
def available_guests(scenario: str, held: frozenset) -> tuple:
    """The held guests (by name) that ``scenario`` actually offers in its shop, in
    ``GUESTS`` order. For Random Scenario (no fixed pool) every held guest can turn
    up, so all of them."""
    pool = SCENARIO_GUESTS.get(scenario)
    if pool is None:
        return tuple(g for g in GUESTS if g.name in held)
    return tuple(g for g in GUESTS if g.name in held and g.name in pool)

RANDOM_SCENARIO = SCENARIOS[-1]
_STAR_SUPPLY_PER_CHECK: dict[tuple[str, str], int] = {
    ("Alien Invitation", "Alien"): 2,
}

def _star_supply(scenario: str, guest, ps: PartyState) -> int:
    """Copies of ``guest`` you could buy in ``scenario``: 1 base plus this scenario's
    per-``+1 Shop Stock`` rate (``ps.shop_stock - 1`` = the number of those items)."""
    per_check = _STAR_SUPPLY_PER_CHECK.get((scenario, guest.name), 1)
    return 1 + per_check * (ps.shop_stock - 1)


# Flag weight per guest. A real flag guest is worth 1, except Unicorn (a 45-pop star)
# at 0.5; Security, Wrestler and Cupid each act as a half flag despite not raising one.
_FLAG_WEIGHT: dict[str, float] = {
    "Unicorn": 0.5,
    "Security": 0.5,
    "Wrestler": 0.5,
    "Cupid": 0.5,
}


def _flag_count(guests) -> float:
    """Weighted flag total over the held guests: 1 per flag guest, overridden by
    ``_FLAG_WEIGHT`` (Unicorn 0.5; Security / Wrestler / Cupid 0.5 without raising a flag)."""
    return sum(_FLAG_WEIGHT.get(g.name, 1.0 if g.is_flag else 0.0) for g in guests)

_STAR_CAP_IGNORED_FLAGS: set[str] = {"Security", "Wrestler"}
def _flag_count_for_trouble_cap(guests) -> float:
    return _flag_count([g for g in guests if g.name not in _STAR_CAP_IGNORED_FLAGS])

_STAR_GUEST_POP_HEADROOM = 10

def star_guests_from_house_space(house_space: int) -> int:
    if house_space >= 34:
        return 8
    elif house_space >= 31:
        return 6
    elif house_space >= 28:
        return 5
    elif house_space >= 25:
        return 4
    elif house_space >= 20:
        return 3
    elif house_space >= 16:
        return 2
    elif house_space >= 11:
        return 1
    else:
        return 0

@memoize
def max_star_guests(scenario: str, ps: PartyState, held: frozenset) -> int:
    all_stars = available_guests(scenario, held)
    flags = _flag_count_for_trouble_cap(all_stars)
    trouble_cap = ps.max_trouble + int(flags) - 1
    available_stars = 0
    for g in all_stars:
        if not g.is_star or g.cost + _STAR_GUEST_POP_HEADROOM > ps.max_popularity:
            continue
        copies = _star_supply(scenario, g, ps)
        if g.is_trouble:
            copies = max(0, min(copies, trouble_cap))
        available_stars += copies
    if scenario == RANDOM_SCENARIO:
        available_stars //= _RANDOM_SCORE_DIVISOR

    house_space = _house_space_for_scenario(scenario, ps, held)
    possible_stars = star_guests_from_house_space(house_space)
    return min(possible_stars, available_stars)

@memoize
def _can_clear(scenario: str, ps: PartyState, held: frozenset) -> bool:
    return max_star_guests(scenario, ps, held) >= CLEAR_STAR_GUESTS

# Days count on a rising, tax-bracket scale: the portion of days in each band is
# worth this rate. Days past 25 are worth 2x. Feeds _base_cash (and so popularity,
# which is defined as twice the cash grind).
_DAY_BRACKETS: tuple[tuple[int, float], ...] = ((5, 0.5), (10, 0.75), (20, 1.0), (25, 1.5))
_DAY_RATE_OVER = 2.0

def _scaled_days(days: int) -> float:
    """``days`` re-weighted through ``_DAY_BRACKETS`` (1-5 @ .5x, 5-10 @ .75x,
    10-20 @ 1x, 20-25 @ 1.5x, 25+ @ 2x)."""
    total = 0.0
    lo = 0
    for hi, rate in _DAY_BRACKETS:
        total += max(0, min(days, hi) - lo) * rate
        lo = hi
    return total + max(0, days - lo) * _DAY_RATE_OVER

# Cash available with only rich pals.
_TROUBLE_CASH_MULTIPLIER = [0.1, 0.5, 1.5, 3, 5]
def _base_cash_calc(max_trouble: int, days: int) -> int:
    return 2 + math.floor(_TROUBLE_CASH_MULTIPLIER[max_trouble] * _scaled_days(days))

# _base_cash depends only on (max_trouble, days), both bounded by the item pool --
# precompute the whole grid once so the sweep never recomputes it.
_MAX_TROUBLE_COUNT = BASE_STATE.max_trouble + item_table[MAX_TROUBLE].quantity
_MAX_DAYS = BASE_STATE.days + item_table[DAY].quantity
_BASE_CASH: dict[tuple[int, int], int] = {}
for _mt in range(_MAX_TROUBLE_COUNT + 1):
    for _d in range(_MAX_DAYS + 1):
        _BASE_CASH[(_mt, _d)] = _base_cash_calc(_mt, _d)


def _base_cash(ps: PartyState) -> int:
    key = (ps.max_trouble, ps.days)
    return _BASE_CASH[key] if key in _BASE_CASH else _base_cash_calc(*key)


# Buying house space: you start at 5, raising it to ``n`` costs ``min(n - 4, 12)``
# (so 6 costs $2, 7 costs $3, ... flat $12 from 16 on), and 34 is the ceiling.
_HOUSE_SPACE_BASE = 5
_HOUSE_SPACE_STEP_CAP = 12

# Cumulative cash to reach each house-space level: _HOUSE_SPACE_COST[n] = cash needed
# to sit at n (indices 0.._HOUSE_SPACE_BASE all 0). Built once; _max_house_space then
# bisects it instead of looping per call.
_HOUSE_SPACE_COST: list[int] = [0] * (_HOUSE_SPACE_BASE + 1)
_cost = 0
for _n in range(_HOUSE_SPACE_BASE + 1, HOUSE_SPACE_MAX + 1):
    _cost += min(_n - 4, _HOUSE_SPACE_STEP_CAP)
    _HOUSE_SPACE_COST.append(_cost)


_SCORE_CATEGORIES = ("cash_score", "pop_score", "util_score")
_SCORE_SLOTS = 8

# (guest name, category) -> per-``max_trouble`` rungs (index = max_trouble directly,
# 0..4). These guests' score in that category scales with the crowd size instead of
# being the static ``Guest`` field.
_MAX_TROUBLE_SCALED_SCORE: dict[tuple[str, str], tuple[int, ...]] = {
    ("Bartender", "cash_score"): (0, 1, 3, 5, 7),
    ("Writer", "pop_score"): (0, 1, 3, 5, 7),
    ("Comedian", "pop_score"): (0, 1, 2, 3, 4),
}


def _guest_score(guest, category: str, ps: PartyState) -> int:
    rungs = _MAX_TROUBLE_SCALED_SCORE.get((guest.name, category))
    if rungs is not None:
        return rungs[min(ps.max_trouble, len(rungs) - 1)]
    return getattr(guest, category)
# Random Scenario can turn up any held guest, so it averages a much wider pool: the
# best 40 slots per category, then the totals divided by 5 back to the /8 scale.
_RANDOM_SCORE_SLOTS = 32
_RANDOM_SCORE_DIVISOR = 4


@memoize
def adjusted_scores(scenario: str, ps: PartyState, held: frozenset) -> tuple:
    """``(cash, pop, util)`` for ``scenario``. Non-star, non-trouble held guests the
    scenario supplies, plus the best-scoring troublemakers (capped at
    ``(max_trouble + 1) + floor(flags) // 2 - 3`` -- the real trouble threshold, since
    ``max_trouble`` is the item count -- ``flags`` half-weighted per ``_flag_count``):
    rank that set by each category; every
    guest fills ``shop_stock`` slots, and the best 8 slots per category go into one pool (so
    with 3 shop stock that's 3 of the top guest, 3 of the second, 2 of the third;
    short lists just leave slots empty -- worth 0). Each pooled slot contributes the
    guest's *entire* score, so a guest taken for its popularity still drags in its
    negative utility. A guest already pooled for an earlier category is skipped, so
    no guest is counted twice. Random Scenario instead pools the best 40 slots per
    category and divides the totals by 5."""
    available = available_guests(scenario, held)
    flags = _flag_count(available)
    guests = [g for g in available if not g.is_star and not g.is_trouble]
    troublemakers = sorted(
        (g for g in available if g.is_trouble),
        key=lambda g: sum(_guest_score(g, c, ps) for c in _SCORE_CATEGORIES),
        reverse=True)
    guests += troublemakers[:max(0, ps.max_trouble + int(flags) // 2 - 2)]
    random = scenario == RANDOM_SCENARIO
    slots = _RANDOM_SCORE_SLOTS if random else _SCORE_SLOTS
    divisor = _RANDOM_SCORE_DIVISOR if random else 1
    pool: list = []
    seen: set = set()
    for cat in _SCORE_CATEGORIES:
        ranked = sorted(guests, key=lambda g, c=cat: _guest_score(g, c, ps), reverse=True)
        taken = 0
        for g in ranked:
            if taken >= slots:
                break
            if g in seen:
                continue
            seen.add(g)
            reps = min(ps.shop_stock, slots - taken)
            pool += [g] * reps
            taken += reps
    return tuple(sum(_guest_score(g, cat, ps) for g in pool) // divisor
                 for cat in _SCORE_CATEGORIES)


@memoize
def cash(scenario: str, ps: PartyState, held: frozenset) -> int:
    cash_score, pop_score, util_score = adjusted_scores(scenario, ps, held)
    base_mult = min(pop_score / 4, cash_score / 5)
    util_penalty = max(util_score / 5, -1) # only matters if util_score is negative
    util_bonus = min(util_score / 10, base_mult * 0.5) # only matters if util_score is positive
    multiplier = base_mult + min(util_penalty, 0) + max(util_bonus, 0)

    base = _base_cash(ps)
    if multiplier < 1:
        return base + ps.starting_cash
    return int(base * multiplier) + ps.starting_cash

@memoize
def _house_space_for_scenario(scenario: str, ps: PartyState, held: frozenset) -> int:
    space = bisect_right(_HOUSE_SPACE_COST, cash(scenario, ps, held))
    cap = min(ps.max_cash + 4, HOUSE_SPACE_MAX)
    if ps.max_cash < 24:
        cap = min(cap, ps.days + 1)
    return min(cap, space)


@memoize
def _max_house_space(ps: PartyState, held: frozenset) -> int:
    return max(_house_space_for_scenario(scenario, ps, held) for scenario in SCENARIOS)


@memoize
def _popularity_reachable(threshold: int, ps: PartyState) -> bool:
    if ps.max_popularity < threshold:
        return False
    return _base_cash(ps) * 2 + ps.starting_popularity >= threshold

# field -> (item name, amount one copy adds).
_PER_ITEM: dict[str, tuple[str, int]] = {
    "max_popularity": (MAX_POPULARITY, 5),
    "max_cash": (MAX_CASH, 2),
    "max_trouble": (MAX_TROUBLE, 1),
    "days": (DAY, 1),
    "shop_stock": (SHOP_STOCK, 1),
    "starting_popularity": (START_POPULARITY, 1),
    "starting_cash": (START_CASH, 1),
}

def party_state(state: "CollectionState", world: "UFO50World") -> PartyState:
    """``BASE_STATE`` plus the resource each received item adds."""
    player = world.player

    def total(field: str) -> int:
        base = getattr(BASE_STATE, field)
        if field not in _PER_ITEM:
            return base
        name, per = _PER_ITEM[field]
        return base + per * state.count(f"{GAME_NAME} - {name}", player)

    return PartyState(**{field: total(field) for field in PartyState._fields})


def guests_held(state: "CollectionState", world: "UFO50World") -> frozenset:
    """Names of the guests whose item the player holds."""
    player = world.player
    return frozenset(g.name for g in GUESTS if state.has(f"{GAME_NAME} - {g.name}", player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Every scenario is open from the start, and so is the global metric region.
    regions["Menu"].connect(regions["The Party"])
    for scenario in SCENARIOS:
        regions["Menu"].connect(regions[scenario])

    def ps(state: "CollectionState") -> PartyState:
        return party_state(state, world)

    def held(state: "CollectionState") -> frozenset:
        return guests_held(state, world)

    _STAR_GUEST_NAMES: frozenset = frozenset(g.name for g in GUESTS if g.is_star)
    @memoize
    def _missing_star_guests(held: frozenset) -> int:
        return len(_STAR_GUEST_NAMES - held)

    for loc_name, info in location_table.items():
        if loc_name in ("Gift", "Gold", "Cherry"):
            continue
        if info.metric == POPULARITY:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold: _popularity_reachable(t, ps(state)))
            continue
        if info.metric == HOUSE_SPACE:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold: _max_house_space(ps(state), held(state)) >= t)
            continue
        if info.metric == CASH:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold:
                     max(cash(s, ps(state), held(state)) for s in SCENARIOS) >= t)
            continue
        if info.metric != STAR_GUESTS:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, s=info.region_name, t=info.threshold:
                 max_star_guests(s, ps(state), held(state)) >= t)

    # Streak 3/4 (Random Scenario) additionally require holding all but one star guest.
    for _streak in (3, 4):
        add_rule(world.get_location(f"{GAME_NAME} - {RANDOM_SCENARIO} - Streak {_streak}"),
                 lambda state: _missing_star_guests(held(state)) <= 1)

    set_rule(world.get_location(f"{GAME_NAME} - Gift"),
             lambda state: any(_can_clear(s, ps(state), held(state)) for s in SCENARIOS))

    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(_can_clear(s, ps(state), held(state)) for s in FIXED_SCENARIOS))

    # Cherry (vanilla: a 5-win streak in Random Scenario) -- a much deeper Random run:
    # every star guest in hand and enough of them seatable there.
    _CHERRY_STAR_GUESTS = 8
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: _missing_star_guests(held(state)) == 0
             and max_star_guests(RANDOM_SCENARIO, ps(state), held(state)) >= _CHERRY_STAR_GUESTS)
