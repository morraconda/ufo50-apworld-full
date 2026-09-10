from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .locations import (GAME_NAME, SCENARIOS, FIXED_SCENARIOS, POPULARITY, HOUSE_SPACE,
                        HOUSE_SPACE_MAX, STAR_GUESTS, CLEAR_STAR_GUESTS,
                        STAR_GUEST_THRESHOLDS, location_table)
from .items import (MAX_TROUBLE, SHOP_STOCK, MAX_POPULARITY, MAX_CASH, DAY,
                    START_POPULARITY, START_CASH, GUESTS, SCENARIO_GUESTS)

if TYPE_CHECKING:
    from ... import UFO50World


class PartyState(NamedTuple):
    """A run's Party House resources: the starting value plus every received item."""
    max_popularity: int
    max_cash: int
    house_space: int
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
    house_space=5,
    trouble_threshold=1,
    days=5,
    shop_stock=1,
    starting_popularity=0,
    starting_cash=0,
)

# field -> (item name, amount one copy adds). house_space has no item -- it only grows
# through the per-scenario simulation, so it stays at its base value here.
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
# Each location has a "sphere" -- a Thresholds tuple it requires. A location is reachable
# when, for every one of the nine fields, the value the player can ACHIEVE is >= the
# value the sphere REQUIRES (a pure AND).
#
# Achieved values:
#   money_score / pop_score / util_score  -- sum of that score over the held guests
#                                            the scenario can supply.
#   star_guests                           -- shop_stock * (# held star guests the
#                                            scenario supplies that cost <= max_popularity).
#   trouble_threshold / max_popularity / max_cash / days / shop_stock
#                                         -- straight from party_state (items only).
#
# money/pop/util score thresholds are all 0 for now ("3 Popularity" and "5 House Space"
# are deliberately sphere 1). The star-guest locations 1..6 each get a real star_guests
# requirement; every other field is still a placeholder to fill in per (metric, threshold).
# ---------------------------------------------------------------------------

class Thresholds(NamedTuple):
    money_score: int
    pop_score: int
    util_score: int
    star_guests: int
    trouble_threshold: int
    max_popularity: int
    max_cash: int
    days: int
    shop_stock: int


ZERO_SPHERE = Thresholds(0, 0, 0, 0, 0, 0, 0, 0, 0)


def _sphere(money_score: int = 0, pop_score: int = 0, util_score: int = 0,
           star_guests: int = 0, trouble_threshold: int = 0, max_popularity: int = 0,
           max_cash: int = 0, days: int = 0, shop_stock: int = 0) -> Thresholds:
    return Thresholds(money_score, pop_score, util_score, star_guests,
                      trouble_threshold, max_popularity, max_cash, days, shop_stock)


# (metric, threshold value) -> the sphere that location requires. Popularity / House
# Space checks are now global sphere-1 progress markers with no rule, so only the
# per-scenario Star Guests locations 1..5 and Clear (6) appear here: a dedicated sphere
# per value, star_guests set to the target and every other field a placeholder.
SPHERES: dict[tuple[str, int], Thresholds] = {
    **{(STAR_GUESTS, n): _sphere(star_guests=n) for n in STAR_GUEST_THRESHOLDS},
    (STAR_GUESTS, CLEAR_STAR_GUESTS): _sphere(star_guests=CLEAR_STAR_GUESTS),
}


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


def _seatable_star_guests(scenario: str, ps: PartyState,
                          state: "CollectionState", world: "UFO50World") -> int:
    """How many star (prestige) guests you could get into the party: for each held
    star guest the scenario supplies that you can AFFORD (cost <= max_popularity),
    the copies you can BUY (see _star_supply)."""
    return sum(_star_supply(scenario, g, ps)
               for g in available_guests(scenario, state, world)
               if g.is_star and g.cost <= ps.max_popularity)


def max_star_guests(scenario: str, state: "CollectionState",
                    world: "UFO50World") -> int:
    """The most star guests ``scenario`` can seat: for each held star guest it
    supplies whose cost is within ``max_popularity``, the copies you can buy
    (``_star_supply``). A star guest that is also a troublemaker is capped at
    ``trouble_threshold + flags - 2`` copies, where ``flags`` is the held flag
    guests the scenario supplies. Random Scenario's total is divided by 5 (it
    supplies every held guest, so its raw count is far larger)."""
    ps = party_state(state, world)
    available = available_guests(scenario, state, world)
    flags = sum(1 for g in available if g.is_flag)
    trouble_cap = ps.trouble_threshold + flags - 2
    total = 0
    for g in available:
        if not g.is_star or g.cost > ps.max_popularity:
            continue
        copies = _star_supply(scenario, g, ps)
        if g.is_trouble:
            copies = max(0, min(copies, trouble_cap))
        total += copies
    if scenario == RANDOM_SCENARIO:
        total //= _RANDOM_SCORE_DIVISOR
    return total


def _achieved(scenario: str, state: "CollectionState", world: "UFO50World") -> Thresholds:
    ps = party_state(state, world)
    guests = available_guests(scenario, state, world)
    return Thresholds(
        money_score=sum(g.money_score for g in guests),
        pop_score=sum(g.pop_score for g in guests),
        util_score=sum(g.util_score for g in guests),
        star_guests=_seatable_star_guests(scenario, ps, state, world),
        trouble_threshold=ps.trouble_threshold,
        max_popularity=ps.max_popularity,
        max_cash=ps.max_cash,
        days=ps.days,
        shop_stock=ps.shop_stock,
    )


# Random Scenario supplies every held guest (no fixed pool), so its locations demand
# twice the sphere's money / pop / util score requirement (the other five fields are
# item-driven and unchanged).
RANDOM_SCENARIO = SCENARIOS[-1]


def _required(scenario: str, metric: str, threshold: int) -> Thresholds:
    base = SPHERES.get((metric, threshold), ZERO_SPHERE)
    if scenario == RANDOM_SCENARIO:
        return base._replace(money_score=2 * base.money_score,
                             pop_score=2 * base.pop_score,
                             util_score=2 * base.util_score)
    return base


def _meets(scenario: str, metric: str, threshold: int,
           state: "CollectionState", world: "UFO50World") -> bool:
    required = _required(scenario, metric, threshold)
    achieved = _achieved(scenario, state, world)
    return all(a >= r for a, r in zip(achieved, required))


def _can_clear(scenario: str, state: "CollectionState", world: "UFO50World") -> bool:
    return _meets(scenario, STAR_GUESTS, CLEAR_STAR_GUESTS, state, world)


def _base_pop(ps: PartyState) -> int:
    """The popularity a run can grind out with no unlocked guests"""
    return 2 * (ps.trouble_threshold - 1) * ps.days


def _base_cash(ps: PartyState) -> int:
    """The cash a run can grind out with no unlocked guests."""
    return (ps.trouble_threshold - 1) * ps.days


# Buying house space: you start at 5, raising it to ``n`` costs ``min(n - 4, 12)``
# (so 6 costs $2, 7 costs $3, ... flat $12 from 16 on), and 34 is the ceiling.
_HOUSE_SPACE_STEP_CAP = 12

def _house_space(cash: int) -> int:
    """The house space ``cash`` can buy, from the base 5 up to ``HOUSE_SPACE_MAX``."""
    space = BASE_STATE.house_space
    while space < HOUSE_SPACE_MAX:
        step = min((space + 1) - 4, _HOUSE_SPACE_STEP_CAP)
        if cash < step:
            break
        cash -= step
        space += 1
    return space


_SCORE_CATEGORIES = ("money_score", "pop_score", "util_score")
_SCORE_SLOTS = 8
# Random Scenario can turn up any held guest, so it averages a much wider pool: the
# best 40 slots per category, then the totals divided by 5 back to the /8 scale.
_RANDOM_SCORE_SLOTS = 40
_RANDOM_SCORE_DIVISOR = 5


def adjusted_scores(scenario: str, state: "CollectionState",
                    world: "UFO50World") -> tuple[int, int, int]:
    """``(money, pop, util)`` for ``scenario``. Star guests and troublemakers aside,
    rank the held guests the scenario supplies by each category; every guest fills
    ``shop_stock`` slots, and the best 8 slots per category go into one pool (so with
    3 shop stock that's 3 of the top guest, 3 of the second, 2 of the third; short
    lists just leave slots empty -- worth 0). Each pooled slot contributes the
    guest's *entire* score, so a guest taken for its popularity still drags in its
    negative utility. A guest already pooled for an earlier category is skipped, so
    no guest is counted twice. Random Scenario instead pools the best 40 slots per
    category and divides the totals by 5."""
    ps = party_state(state, world)
    guests = [g for g in available_guests(scenario, state, world)
              if not g.is_star and not g.is_trouble]
    random = scenario == RANDOM_SCENARIO
    slots = _RANDOM_SCORE_SLOTS if random else _SCORE_SLOTS
    divisor = _RANDOM_SCORE_DIVISOR if random else 1
    pool: list = []
    seen: set = set()
    for cat in _SCORE_CATEGORIES:
        ranked = sorted(guests, key=lambda g, c=cat: getattr(g, c), reverse=True)
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
    return tuple(sum(getattr(g, cat) for g in pool) // divisor
                 for cat in _SCORE_CATEGORIES)


def _popularity_reachable(threshold: int, state: "CollectionState",
                          world: "UFO50World") -> bool:
    """A global ``<n> Popularity`` check. Reachable when both hold:

    * ``_base_pop + 3 + starting_popularity >= n`` -- the ceiling a run can push
      popularity to, including the head start from ``+1 Starting Popularity``.
    * ``max_popularity >= n`` -- the popularity cap has been raised to at least ``n``.
    """
    ps = party_state(state, world)
    if ps.max_popularity < threshold:
        return False
    return _base_pop(ps) + 3 + ps.starting_popularity >= threshold


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
        # Global house-space checks are still plain sphere-1 progress markers.
        if info.metric != STAR_GUESTS:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, s=info.region_name, m=info.metric, t=info.threshold:
                 _meets(s, m, t, state, world))

    # Gift (vanilla: beat any one scenario) -- gate on clearing the first.
    set_rule(world.get_location(f"{GAME_NAME} - Gift"),
             lambda state: _can_clear(SCENARIOS[0], state, world))

    # Gold (vanilla: beat all five fixed scenarios).
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(_can_clear(s, state, world) for s in FIXED_SCENARIOS))

    # Cherry location (vanilla: a 5-win streak in Random Scenario) -- logic just needs
    # Random Scenario clearable.
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: _can_clear(SCENARIOS[-1], state, world))
