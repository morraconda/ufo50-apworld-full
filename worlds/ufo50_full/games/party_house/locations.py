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
    "Money Management",
    "A Magical Night",
    "Random Scenario",
]
FIXED_SCENARIOS: list[str] = SCENARIOS[:5]

# Popularity + House Space checks are GLOBAL -- one set for the whole game, reachable
# in any scenario, awarded once. Popularity: every value 1..20, then every 2 up to 80.
# House Space: every value 5..33, plus the max (34) as its own check named "UFO". The
# mod starts a run at 4 house space, so even 5 has to be bought.
POPULARITY_VALUES: list[int] = list(range(1, 21)) + list(range(22, 81, 2))
HOUSE_SPACE_VALUES: list[int] = list(range(5, 34))
HOUSE_SPACE_MAX: int = 34
HOUSE_SPACE_MAX_NAME: str = "UFO"
POP_OFFSET_BASE: int = 700       # "<n> Popularity"  -> POP_OFFSET_BASE + n  (701..780)
SPACE_OFFSET_BASE: int = 800     # "<n> House Space" -> SPACE_OFFSET_BASE + n (805..833; 834 = "UFO")
GLOBAL_REGION = "The Party"

# Star Guests + Clear are per-scenario.
STAR_GUEST_THRESHOLDS: list[int] = [1, 2, 3, 4, 5]
CLEAR_STAR_GUESTS: int = 6
# streak win # -> star guests. Entry 1 is a single Random win, which has no location of
# its own (that's the scenario's Clear); it carries the floor every Random star-guest
# check needs, since Random deals only a random couple of the 9 prestige types into its
# store. 2..5 are both the seatable threshold their location asks for and, in
# rules.create_rules, how many of the 9 you must hold to sustain that streak.
RANDOM_STREAK_THRESHOLDS: dict[int, int] = {1: 3, 2: 5, 3: 6, 4: 7, 5: 8}
STREAK_LOCATION_WINS: tuple[int, ...] = (2, 3, 4, 5)

# Metric names used by rules.scenario_outcome.
POPULARITY = "popularity"
HOUSE_SPACE = "house_space"
STAR_GUESTS = "star_guests"


# Per-scenario id layout via the standard game_helpers.level_id (level * 10 + slot;
# scenario = level 1..6). Random Scenario (level 6) additionally uses slots 6..9 for
# its streak locations; slots 6..9 are unused by every other scenario.
#   slot 0     <scenario>          (won the scenario)
#   slots 1..5 <n> Star Guests     (STAR_GUEST_THRESHOLDS in order)
#   slots 6..9 Streak 2/3/4/5      (Random Scenario only, STREAK_LOCATION_WINS in order)
_CLEAR_SLOT = 0
_STAR_GUEST_SLOT0 = 1
_STREAK_SLOT0 = 6


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
        if scenario == SCENARIOS[-1]:  # Random Scenario
            for i, streak in enumerate(STREAK_LOCATION_WINS):
                table[f"{scenario} - Streak {streak}"] = LocationInfo(
                    level_id(level, _STREAK_SLOT0 + i), scenario, STAR_GUESTS,
                    RANDOM_STREAK_THRESHOLDS[streak])
    # goal locations last so create_locations' Cherry/Gold handling can break out.
    # (metric/threshold here are unused -- rules.py special-cases these three.)
    table["Gift"] = LocationInfo(997, SCENARIOS[0], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Gold"] = LocationInfo(998, FIXED_SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Cherry"] = LocationInfo(999, SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()


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
