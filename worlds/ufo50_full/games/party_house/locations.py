from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Party House"

# The six scenarios, in play order (index + 1 = the "level" number). The first five
# are the fixed scenarios; the sixth is Random Scenario.
SCENARIOS: list[str] = [
    "Alien Invitation",
    "High or Low",
    "Best Wishes",
    "Money Management",   # in-game scenario[3] (menu "4 MONEY MANAGEMENT")
    "A Magical Night",    # in-game scenario[4] (menu "5 A MAGICAL NIGHT")
    "Random Scenario",
]
FIXED_SCENARIOS: list[str] = SCENARIOS[:5]

# Popularity + House Space checks are GLOBAL -- one set for the whole game, reachable
# in any scenario, awarded once. Popularity: every value 1..20, then every 2 up to 80.
# House Space: every value 6..33, plus the max (34) as its own check named "UFO"; the
# former "5 House Space" slot (id 805) is now the "1 Cash" check.
POPULARITY_VALUES: list[int] = list(range(1, 21)) + list(range(22, 81, 2))
HOUSE_SPACE_VALUES: list[int] = list(range(6, 34))
HOUSE_SPACE_MAX: int = 34
HOUSE_SPACE_MAX_NAME: str = "UFO"
CASH_OFFSET: int = 805           # "1 Cash" (reuses the old "5 House Space" id)
POP_OFFSET_BASE: int = 700       # "<n> Popularity"  -> POP_OFFSET_BASE + n  (701..780)
SPACE_OFFSET_BASE: int = 800     # "<n> House Space" -> SPACE_OFFSET_BASE + n (806..833; 834 = "UFO")
GLOBAL_REGION = "The Party"

# Star Guests + Clear are per-scenario.
STAR_GUEST_THRESHOLDS: list[int] = [1, 2, 3, 4, 5]
# "Clear" = seat six star guests (one past the highest Star Guests location).
CLEAR_STAR_GUESTS: int = 6

# Metric names used by rules.scenario_outcome.
POPULARITY = "popularity"
HOUSE_SPACE = "house_space"
STAR_GUESTS = "star_guests"
CASH = "cash"


# Per-scenario id layout (Clear + 5 Star Guests = 6 slots), via the standard
# game_helpers.level_id (level * 10 + slot; scenario = level 1..6).
#   slot 0     <scenario>          (won the scenario)
#   slots 1..5 <n> Star Guests     (STAR_GUEST_THRESHOLDS in order)
_CLEAR_SLOT = 0
_STAR_GUEST_SLOT0 = 1


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str
    metric: str          # rules.scenario_outcome key: "popularity" / "house_space" / "star_guests"
    threshold: int       # value that metric must reach


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    # Global popularity / house-space checks -- one set, any scenario counts.
    for n in POPULARITY_VALUES:
        table[f"{n} Popularity"] = LocationInfo(
            POP_OFFSET_BASE + n, GLOBAL_REGION, POPULARITY, n)
    table["1 Cash"] = LocationInfo(CASH_OFFSET, GLOBAL_REGION, CASH, 1)
    for n in HOUSE_SPACE_VALUES:
        table[f"{n} House Space"] = LocationInfo(
            SPACE_OFFSET_BASE + n, GLOBAL_REGION, HOUSE_SPACE, n)
    # Max house space (34) is its own check, named "UFO".
    table[HOUSE_SPACE_MAX_NAME] = LocationInfo(
        SPACE_OFFSET_BASE + HOUSE_SPACE_MAX, GLOBAL_REGION, HOUSE_SPACE, HOUSE_SPACE_MAX)
    # Per-scenario Clear + Star Guests.
    for level, scenario in enumerate(SCENARIOS, start=1):
        table[scenario] = LocationInfo(
            level_id(level, _CLEAR_SLOT), scenario, STAR_GUESTS, CLEAR_STAR_GUESTS)
        for i, n in enumerate(STAR_GUEST_THRESHOLDS):
            table[f"{scenario} - {n} Star Guests"] = LocationInfo(
                level_id(level, _STAR_GUEST_SLOT0 + i), scenario, STAR_GUESTS, n)
    # goal locations last so create_locations' Cherry/Gold handling can break out.
    # (metric/threshold here are unused -- rules.py special-cases these three.)
    table["Gift"] = LocationInfo(997, SCENARIOS[0], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Gold"] = LocationInfo(998, FIXED_SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Cherry"] = LocationInfo(999, SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# Popularity / Cash / house-space checks now carry rules (rules._popularity_reachable,
# rules.cash, rules._max_house_space), as do the Star Guests / Clear locations. A fresh
# run (flat base pop 3, base cash 2, max_cash 2, days 5 -> days+1 clamp of 6) reaches
# 6 house space, so only these are sphere 1.
sphere_1_locs: list[str] = ([f"{n} Popularity" for n in POPULARITY_VALUES[:3]]
                            + ["1 Cash", f"{HOUSE_SPACE_VALUES[0]} House Space"])


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Clears"] = {f"{GAME_NAME} - {s}" for s in SCENARIOS}
    groups[f"{GAME_NAME} - Popularity"] = {f"{GAME_NAME} - {n} Popularity" for n in POPULARITY_VALUES}
    groups[f"{GAME_NAME} - House Space"] = (
        {f"{GAME_NAME} - {n} House Space" for n in HOUSE_SPACE_VALUES}
        | {f"{GAME_NAME} - {HOUSE_SPACE_MAX_NAME}"})
    for scenario in SCENARIOS:
        groups[f"{GAME_NAME} - {scenario} Locations"] = {f"{GAME_NAME} - {name}"
                                                      for name, data in location_table.items()
                                                      if data.region_name == scenario}
    return groups


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            continue

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, region)
        region.locations.append(loc)
