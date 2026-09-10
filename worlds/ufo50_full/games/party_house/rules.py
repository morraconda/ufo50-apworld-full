from bisect import bisect_right
from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .locations import (GAME_NAME, SCENARIOS, FIXED_SCENARIOS, POPULARITY, HOUSE_SPACE,
                        HOUSE_SPACE_MAX, STAR_GUESTS, CASH, CLEAR_STAR_GUESTS, location_table)
from .items import (MAX_TROUBLE, SHOP_STOCK, MAX_POPULARITY, MAX_CASH, DAY,
                    START_POPULARITY, START_CASH, GUESTS, SCENARIO_GUESTS, item_table)

if TYPE_CHECKING:
    from ... import UFO50World


class PartyState(NamedTuple):
    """A run's Party House resources: the starting value plus every received item."""
    max_popularity: int
    max_cash: int
    trouble_threshold: int
    days: int
    shop_stock: int
    starting_popularity: int
    starting_cash: int


# What every run starts with, before any AP item is applied. trouble_threshold 1 =
# busted at 1 trouble; each +1 Max Trouble raises it (mirrors the mod's
# TROUBLE_THRESHOLD = 1 + count).
BASE_STATE = PartyState(
    max_popularity=10,
    max_cash=2,
    trouble_threshold=1,
    days=5,
    shop_stock=1,
    starting_popularity=0,
    starting_cash=0,
)

# field -> (item name, amount one copy adds).
_PER_ITEM: dict[str, tuple[str, int]] = {
    "max_popularity": (MAX_POPULARITY, 5),
    "max_cash": (MAX_CASH, 2),
    "trouble_threshold": (MAX_TROUBLE, 1),
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


def guests_held(state: "CollectionState", world: "UFO50World") -> list:
    """The ``Guest`` entries whose item the player holds."""
    player = world.player
    return [g for g in GUESTS if state.has(f"{GAME_NAME} - {g.name}", player)]


def available_guests(scenario: str, state: "CollectionState", world: "UFO50World") -> list:
    """The held guests that ``scenario`` actually offers in its shop. For Random
    Scenario (no fixed pool) every held guest can turn up, so all of them."""
    held = guests_held(state, world)
    pool = SCENARIO_GUESTS.get(scenario)
    if pool is None:
        return held
    return [g for g in held if g.name in pool]


# ---------------------------------------------------------------------------
# Access model
#
# Popularity, House Space and the per-scenario Star Guests / Clear locations each get
# a rule that compares what the run can ACHIEVE against the value the location wants:
#   Popularity   -- _popularity_reachable
#   House Space  -- _max_house_space (cash -> _house_space, or the star-guest path)
#   Star Guests  -- max_star_guests
#   Clear / goal -- _can_clear (seat the full CLEAR_STAR_GUESTS)
# ---------------------------------------------------------------------------

# Random Scenario is the 6th; with no fixed guest pool every held guest can turn up
# in it, so its raw counts get scaled back down (see _RANDOM_SCORE_DIVISOR).
RANDOM_SCENARIO = SCENARIOS[-1]


# (scenario, guest name) -> extra star-guest copies stocked per "+1 Shop Stock", when
# it differs from the usual 1. Alien Invitation offers only one star guest (Alien), so
# it is hardcoded to 2 per location.
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


# Security and Wrestler count as half flags everywhere except ``max_star_guests``'s
# troublemaker cap, where they do not count at all.
_STAR_CAP_IGNORED_FLAGS: set[str] = {"Security", "Wrestler"}


def _flag_count_for_trouble_cap(guests) -> float:
    return _flag_count([g for g in guests if g.name not in _STAR_CAP_IGNORED_FLAGS])


# A star guest is only buyable with this much popularity headroom over its cost.
_STAR_GUEST_POP_HEADROOM = 10


def max_star_guests(scenario: str, state: "CollectionState",
                    world: "UFO50World") -> int:
    """The most star guests ``scenario`` can seat: for each held star guest it
    supplies whose cost + ``_STAR_GUEST_POP_HEADROOM`` is within ``max_popularity``,
    the copies you can buy (``_star_supply``). A star guest that is also a
    troublemaker is capped at ``trouble_threshold + floor(flags) - 2`` copies, where
    ``flags`` is the half-weighted held flag guests (``_flag_count_for_trouble_cap``:
    like ``_flag_count`` but Security / Wrestler don't count here). Random Scenario's
    total is divided by 5 (it supplies every held guest, so its raw count is far
    larger)."""
    ps = party_state(state, world)
    available = available_guests(scenario, state, world)
    flags = _flag_count_for_trouble_cap(available)
    trouble_cap = ps.trouble_threshold + int(flags) - 2
    total = 0
    for g in available:
        if not g.is_star or g.cost + _STAR_GUEST_POP_HEADROOM > ps.max_popularity:
            continue
        copies = _star_supply(scenario, g, ps)
        if g.is_trouble:
            copies = max(0, min(copies, trouble_cap))
        total += copies
    if scenario == RANDOM_SCENARIO:
        total //= _RANDOM_SCORE_DIVISOR
    return total


def _can_clear(scenario: str, state: "CollectionState", world: "UFO50World") -> bool:
    """Cleared ``scenario`` == able to seat the full ``CLEAR_STAR_GUESTS`` star guests."""
    return max_star_guests(scenario, state, world) >= CLEAR_STAR_GUESTS


# Cherry (vanilla: a 5-win streak in Random Scenario) is much harder than a plain
# clear -- gate it on holding every star guest AND seating the equivalent of this
# many of them in Random Scenario.
_CHERRY_STAR_GUESTS = 8
_STAR_GUEST_ITEMS = [g.name for g in GUESTS if g.is_star]


def _has_all_star_guests(state: "CollectionState", world: "UFO50World") -> bool:
    return all(state.has(f"{GAME_NAME} - {name}", world.player)
               for name in _STAR_GUEST_ITEMS)


# Days count on a rising, tax-bracket scale: the portion of days in each band is
# worth this rate. Days past 25 are worth 2x. Feeds both _base_pop and _base_cash.
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


# Flat floor every run clears regardless of trouble budget / days.
_BASE_POP_FLAT = 3
_BASE_CASH_FLAT = 2


def _base_pop_calc(trouble_threshold: int, days: int) -> int:
    """Popularity a run grinds out with no guests: a flat 3 plus a term linear in the
    trouble budget, days re-weighted by ``_scaled_days``."""
    return _BASE_POP_FLAT + int(2 * (trouble_threshold - 1) * _scaled_days(days))


def _base_cash_calc(trouble_threshold: int, days: int) -> int:
    """Cash a run grinds out with no guests: a flat 2 plus ``(tt - 1)(tt + 2) / 6``
    per scaled day -- that term is 0 at ``tt`` 1, 0.66 at 2, 1.66 at 3, 3 at 4
    (matching a plain ``(tt - 1)`` line), 4.66 at 5."""
    tt = trouble_threshold
    return _BASE_CASH_FLAT + int((tt - 1) * (tt + 2) / 6 * _scaled_days(days))


# _base_pop / _base_cash depend only on (trouble_threshold, days), both bounded by
# the item pool -- precompute the whole grid once so the sweep never recomputes it.
_MAX_TROUBLE_THRESHOLD = BASE_STATE.trouble_threshold + item_table[MAX_TROUBLE].quantity
_MAX_DAYS = BASE_STATE.days + item_table[DAY].quantity
_BASE_POP: dict[tuple[int, int], int] = {}
_BASE_CASH: dict[tuple[int, int], int] = {}
for _tt in range(_MAX_TROUBLE_THRESHOLD + 1):
    for _d in range(_MAX_DAYS + 1):
        _BASE_POP[(_tt, _d)] = _base_pop_calc(_tt, _d)
        _BASE_CASH[(_tt, _d)] = _base_cash_calc(_tt, _d)


def _base_pop(ps: PartyState) -> int:
    key = (ps.trouble_threshold, ps.days)
    return _BASE_POP[key] if key in _BASE_POP else _base_pop_calc(*key)


def _base_cash(ps: PartyState) -> int:
    key = (ps.trouble_threshold, ps.days)
    return _BASE_CASH[key] if key in _BASE_CASH else _base_cash_calc(*key)


# Buying house space: you start at 5, raising it to ``n`` costs ``min(n - 4, 12)``
# (so 6 costs $2, 7 costs $3, ... flat $12 from 16 on), and 34 is the ceiling.
_HOUSE_SPACE_BASE = 5
_HOUSE_SPACE_STEP_CAP = 12

# Cumulative cash to reach each house-space level: _HOUSE_SPACE_COST[n] = cash needed
# to sit at n (indices 0.._HOUSE_SPACE_BASE all 0). Built once; _house_space is then a
# binary search instead of a per-call loop.
_HOUSE_SPACE_COST: list[int] = [0] * (_HOUSE_SPACE_BASE + 1)
_cost = 0
for _n in range(_HOUSE_SPACE_BASE + 1, HOUSE_SPACE_MAX + 1):
    _cost += min(_n - 4, _HOUSE_SPACE_STEP_CAP)
    _HOUSE_SPACE_COST.append(_cost)


def _house_space(cash: int) -> int:
    """The house space ``cash`` can buy, from the base 5 up to ``HOUSE_SPACE_MAX``."""
    return bisect_right(_HOUSE_SPACE_COST, max(cash, 0)) - 1


_SCORE_CATEGORIES = ("cash_score", "pop_score", "util_score")
_SCORE_SLOTS = 8

# (guest name, category) -> per-``trouble_threshold`` rungs (index = tt - 1, clamped
# to 1..5). These guests' score in that category scales with the crowd size instead of
# being the static ``Guest`` field.
_TT_SCALED_SCORE: dict[tuple[str, str], tuple[int, ...]] = {
    ("Bartender", "cash_score"): (0, 1, 3, 5, 7),
    ("Writer", "pop_score"): (0, 1, 3, 5, 7),
    ("Comedian", "pop_score"): (0, 1, 2, 3, 4),
}


def _guest_score(guest, category: str, ps: PartyState) -> int:
    """``getattr(guest, category)``, except for the few (guest, category) pairs whose
    score scales with the run's trouble budget (see ``_TT_SCALED_SCORE``)."""
    rungs = _TT_SCALED_SCORE.get((guest.name, category))
    if rungs is not None:
        return rungs[min(max(ps.trouble_threshold, 1), len(rungs)) - 1]
    return getattr(guest, category)
# Random Scenario can turn up any held guest, so it averages a much wider pool: the
# best 40 slots per category, then the totals divided by 5 back to the /8 scale.
_RANDOM_SCORE_SLOTS = 40
_RANDOM_SCORE_DIVISOR = 5


def adjusted_scores(scenario: str, state: "CollectionState",
                    world: "UFO50World") -> tuple[int, int, int]:
    """``(cash, pop, util)`` for ``scenario``. Non-star, non-trouble held guests the
    scenario supplies, plus the best-scoring troublemakers (capped at
    ``trouble_threshold + floor(flags) // 2 - 3``, ``flags`` half-weighted per
    ``_flag_count``): rank that set by each category; every
    guest fills ``shop_stock`` slots, and the best 8 slots per category go into one pool (so
    with 3 shop stock that's 3 of the top guest, 3 of the second, 2 of the third;
    short lists just leave slots empty -- worth 0). Each pooled slot contributes the
    guest's *entire* score, so a guest taken for its popularity still drags in its
    negative utility. A guest already pooled for an earlier category is skipped, so
    no guest is counted twice. Random Scenario instead pools the best 40 slots per
    category and divides the totals by 5."""
    ps = party_state(state, world)
    available = available_guests(scenario, state, world)
    flags = _flag_count(available)
    guests = [g for g in available if not g.is_star and not g.is_trouble]
    troublemakers = sorted(
        (g for g in available if g.is_trouble),
        key=lambda g: sum(_guest_score(g, c, ps) for c in _SCORE_CATEGORIES),
        reverse=True)
    guests += troublemakers[:max(0, ps.trouble_threshold + int(flags) // 2 - 3)]
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


def cash(scenario: str, state: "CollectionState", world: "UFO50World") -> int:
    """Spendable cash in ``scenario``: ``_base_cash`` scaled by how well the
    scenario's guest pool converts to money --

        base_mult   = min(pop/4, cash/5)
        multiplier  = base_mult - clamp(util/5, 0, 1)
                                + clamp(util/10, 0, base_mult * 0.5)

    on the ``adjusted_scores`` ``(cash, pop, util)`` totals -- only positive utility
    counts, a flat 1 against cash, and the util/10 bonus back is capped at half the
    base multiplier. Never worse than plain ``_base_cash``: a pool that scales below
    the base grind just falls back to it."""
    cash_score, pop_score, util_score = adjusted_scores(scenario, state, world)
    base_mult = min(pop_score / 4, cash_score / 5)
    util_penalty = min(max(util_score / 5, 0), 1)
    util_bonus = min(max(util_score / 10, 0), base_mult * 0.5)
    multiplier = base_mult - util_penalty + util_bonus
    base = _base_cash(party_state(state, world))
    return max(base, int(base * multiplier))


def _star_house_space(scenario: str, state: "CollectionState",
                      world: "UFO50World") -> int:
    """House space that seating star guests unlocks in ``scenario``: nothing for
    zero, 10 for the first, +4 for each one after."""
    stars = max_star_guests(scenario, state, world)
    return 0 if stars <= 0 else 10 + 4 * (stars - 1)


def _cash_cap_house_space(max_cash: int) -> int:
    """The house space ``max_cash`` alone allows: each upgrade to ``n`` costs
    ``min(n - 4, 12)`` and you must be able to hold that much at once, so ``n`` is
    limited to ``max_cash + 4`` -- until the cost caps at 12, past which (``max_cash
    >= 12``) it no longer bites."""
    if max_cash >= _HOUSE_SPACE_STEP_CAP:
        return HOUSE_SPACE_MAX
    return max(_HOUSE_SPACE_BASE, min(HOUSE_SPACE_MAX, max_cash + 4))


# Below this ``max_cash`` you also can't out-buy your day count: roughly one expansion
# a day, so house space is additionally clamped to ``days + 1``.
_HOUSE_SPACE_DAYS_CLAMP_MAX_CASH = 24


def _max_house_space(state: "CollectionState", world: "UFO50World") -> int:
    """The most house space the run can reach, best scenario wins: either what
    ``cash(scenario)`` buys via ``_house_space`` or what its star guests unlock via
    ``_star_house_space``. Every house upgrade is still *bought*, so the whole result
    is capped by what ``max_cash`` lets you hold per upgrade (``_cash_cap_house_space``),
    and below ``_HOUSE_SPACE_DAYS_CLAMP_MAX_CASH`` also by ``days + 1``."""
    ps = party_state(state, world)
    best = max(max(_house_space(cash(scenario, state, world)),
                   _star_house_space(scenario, state, world))
               for scenario in SCENARIOS)
    cap = _cash_cap_house_space(ps.max_cash)
    if ps.max_cash < _HOUSE_SPACE_DAYS_CLAMP_MAX_CASH:
        cap = min(cap, ps.days + 1)
    return min(cap, best)


def _popularity_reachable(threshold: int, state: "CollectionState",
                          world: "UFO50World") -> bool:
    """A global ``<n> Popularity`` check. Reachable when both hold:

    * ``_base_pop + starting_popularity >= n`` -- the ceiling a run can push
      popularity to, including the head start from ``+1 Starting Popularity``.
    * ``max_popularity >= n`` -- the popularity cap has been raised to at least ``n``.
    """
    ps = party_state(state, world)
    if ps.max_popularity < threshold:
        return False
    return _base_pop(ps) + ps.starting_popularity >= threshold


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Every scenario is open from the start, and so is the global metric region.
    regions["Menu"].connect(regions["The Party"])
    for scenario in SCENARIOS:
        regions["Menu"].connect(regions[scenario])

    for loc_name, info in location_table.items():
        if loc_name in ("Gift", "Gold", "Cherry"):
            continue
        if info.metric == POPULARITY:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold: _popularity_reachable(t, state, world))
            continue
        if info.metric == HOUSE_SPACE:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold: _max_house_space(state, world) >= t)
            continue
        if info.metric == CASH:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, t=info.threshold:
                     max(cash(s, state, world) for s in SCENARIOS) >= t)
            continue
        if info.metric != STAR_GUESTS:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, s=info.region_name, t=info.threshold:
                 max_star_guests(s, state, world) >= t)

    # Gift (vanilla: beat any one scenario).
    set_rule(world.get_location(f"{GAME_NAME} - Gift"),
             lambda state: any(_can_clear(s, state, world) for s in SCENARIOS))

    # Gold (vanilla: beat all five fixed scenarios).
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(_can_clear(s, state, world) for s in FIXED_SCENARIOS))

    # Cherry (vanilla: a 5-win streak in Random Scenario) -- a much deeper Random run:
    # every star guest in hand and enough of them seatable there.
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: _has_all_star_guests(state, world)
             and max_star_guests(RANDOM_SCENARIO, state, world) >= _CHERRY_STAR_GUESTS)
