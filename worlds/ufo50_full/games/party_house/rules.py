from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from ...goal_locations import cherry_enabled
from .locations import (GAME_NAME, SCENARIOS, FIXED_SCENARIOS, POPULARITY, HOUSE_SPACE,
                        STAR_GUESTS, CLEAR_STAR_GUESTS, POPULARITY_THRESHOLDS,
                        HOUSE_SPACE_THRESHOLDS, STAR_GUEST_THRESHOLDS, location_table)
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
    house_space=3,
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
# Each check has a "sphere" -- a Thresholds tuple it requires. A check is reachable
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
# are deliberately sphere 1). The star-guest checks 1..6 each get a real star_guests
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


# (metric, threshold value) -> the sphere that check requires.
SPHERES: dict[tuple[str, int], Thresholds] = {
    # --- sphere 1: reachable with nothing ---
    (POPULARITY, 3): ZERO_SPHERE,
    (HOUSE_SPACE, 5): ZERO_SPHERE,
    # --- placeholders (currently all-zero) ---
    **{(POPULARITY, n): _sphere() for n in POPULARITY_THRESHOLDS if n != 3},
    **{(HOUSE_SPACE, n): _sphere() for n in HOUSE_SPACE_THRESHOLDS if n != 5},
    # star-guest checks 1..5 and Clear (6): a dedicated sphere per value -- star_guests
    # set to the target, every other field a placeholder.
    **{(STAR_GUESTS, n): _sphere(star_guests=n) for n in STAR_GUEST_THRESHOLDS},
    (STAR_GUESTS, CLEAR_STAR_GUESTS): _sphere(star_guests=CLEAR_STAR_GUESTS),
}


# (scenario, guest name) -> extra star-guest copies stocked per "+1 Shop Stock", when
# it differs from the usual 1. Alien Invitation offers only one star guest (Alien), so
# it is hardcoded to 2 per check.
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


# Random Scenario supplies every held guest (no fixed pool), so its checks demand
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


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Every scenario is open from the start.
    for scenario in SCENARIOS:
        regions["Menu"].connect(regions[scenario])

    for loc_name, info in location_table.items():
        if loc_name in ("Garden", "Gold", "Cherry"):
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, s=info.region_name, m=info.metric, t=info.threshold:
                 _meets(s, m, t, state, world))

    # Garden (vanilla: beat any one scenario) -- gate on clearing the first.
    set_rule(world.get_location(f"{GAME_NAME} - Garden"),
             lambda state: _can_clear(SCENARIOS[0], state, world))

    # Gold (vanilla: beat all five fixed scenarios).
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(_can_clear(s, state, world) for s in FIXED_SCENARIOS))

    # Cherry (vanilla: a 5-win streak in Random Scenario) -- logic just needs Random
    # Scenario clearable.
    if cherry_enabled(world, GAME_NAME):
        set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
                 lambda state: _can_clear(SCENARIOS[-1], state, world))
