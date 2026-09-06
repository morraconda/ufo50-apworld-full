from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import (skip_cherry_location_if_disabled, is_completion_event_location,
                               place_completion_event)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Party House"

# The six scenarios, in play order (index + 1 = the "level" number). The first five
# are the fixed scenarios; the sixth is Random Scenario.
SCENARIOS: list[str] = [
    "Alien Invitation",
    "High or Low",
    "Best Wishes",
    "A Magical Night",
    "Money Management",
    "Random Scenario",
]
FIXED_SCENARIOS: list[str] = SCENARIOS[:5]

# Per-scenario check thresholds.
POPULARITY_THRESHOLDS: list[int] = [3, 5, 10, 20, 30, 40, 50, 60, 75]
HOUSE_SPACE_THRESHOLDS: list[int] = [5, 7, 10, 15, 20, 25, 30]
STAR_GUEST_THRESHOLDS: list[int] = [1, 2, 3, 4, 5]
# "Clear" = seat six star guests (one past the highest Star Guests check).
CLEAR_STAR_GUESTS: int = 6

# Metric names used by rules.scenario_outcome.
POPULARITY = "popularity"
HOUSE_SPACE = "house_space"
STAR_GUESTS = "star_guests"


# --- per-level id layout ---------------------------------------------------------
# Party House has 22 checks per scenario, so the standard game_helpers.level_id
# (level * 10 + slot) is too tight -- use the same idea with 100 ids per level.
IDS_PER_LEVEL = 100


def level_id(level: int, slot: int = 0) -> int:
    """``level * 100 + slot``. ``level`` is 1..6, ``slot`` is 0..99. Offsets 1..99
    stay free for the game-wide items; 997/998/999 are the goal locations."""
    if not 1 <= level <= len(SCENARIOS):
        raise ValueError(f"level {level} out of range 1..{len(SCENARIOS)}")
    if not 0 <= slot < IDS_PER_LEVEL:
        raise ValueError(f"slot {slot} out of range 0..{IDS_PER_LEVEL - 1}")
    return level * IDS_PER_LEVEL + slot


# slot layout inside a scenario's 100-id block:
#    0        Clear
#    1..9     <n> Popularity      (POPULARITY_THRESHOLDS in order)
#   10..16    <n> House Space     (HOUSE_SPACE_THRESHOLDS in order)
#   17..21    <n> Star Guests     (STAR_GUEST_THRESHOLDS in order)
_CLEAR_SLOT = 0
_POPULARITY_SLOT0 = 1
_HOUSE_SPACE_SLOT0 = 10
_STAR_GUEST_SLOT0 = 17


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str
    metric: str          # rules.scenario_outcome key: "popularity" / "house_space" / "star_guests"
    threshold: int       # value that metric must reach


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for level, scenario in enumerate(SCENARIOS, start=1):
        table[f"{scenario} - Clear"] = LocationInfo(
            level_id(level, _CLEAR_SLOT), scenario, STAR_GUESTS, CLEAR_STAR_GUESTS)
        for i, n in enumerate(POPULARITY_THRESHOLDS):
            table[f"{scenario} - {n} Popularity"] = LocationInfo(
                level_id(level, _POPULARITY_SLOT0 + i), scenario, POPULARITY, n)
        for i, n in enumerate(HOUSE_SPACE_THRESHOLDS):
            table[f"{scenario} - {n} House Space"] = LocationInfo(
                level_id(level, _HOUSE_SPACE_SLOT0 + i), scenario, HOUSE_SPACE, n)
        for i, n in enumerate(STAR_GUEST_THRESHOLDS):
            table[f"{scenario} - {n} Star Guests"] = LocationInfo(
                level_id(level, _STAR_GUEST_SLOT0 + i), scenario, STAR_GUESTS, n)
    # goal locations last so create_locations' Cherry/Gold handling can break out.
    # (metric/threshold here are unused -- rules.py special-cases these three.)
    table["Garden"] = LocationInfo(997, SCENARIOS[0], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Gold"] = LocationInfo(998, FIXED_SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    table["Cherry"] = LocationInfo(999, SCENARIOS[-1], STAR_GUESTS, CLEAR_STAR_GUESTS)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# "3 Popularity" and "5 House Space" for each scenario are the intended sphere-1
# checks (need nothing); every other check is gated by rules.SPHERES (all placeholder
# all-zero spheres for now).
sphere_1_locs: list[str] = ([f"{s} - 3 Popularity" for s in SCENARIOS]
                            + [f"{s} - 5 House Space" for s in SCENARIOS])


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Clears"] = {f"{GAME_NAME} - {s} - Clear" for s in SCENARIOS}
    for scenario in SCENARIOS:
        groups[f"{GAME_NAME} - {scenario}"] = {f"{GAME_NAME} - {name}"
                                               for name, data in location_table.items()
                                               if data.region_name == scenario}
    return groups


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if skip_cherry_location_if_disabled(world, GAME_NAME, loc_name):
            break
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            break

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, region)
        region.locations.append(loc)
