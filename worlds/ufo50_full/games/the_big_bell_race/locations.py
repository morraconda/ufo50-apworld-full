from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "The Big Bell Race"
NUM_RACE = 8   # a championship of 8 races (o28_Mas.currStage 0..7)
REGION = "Grand Prix"

# The location for race n is sent only when you finish that race in 1st place -- hence
# the "Win Race <n>" name. It is still sphere 1 (no item gates it), just a skill wall.

# id offset layout inside The Big Bell Race's 1000-id block:
#     1..8   Win Race <n>   (finished race n of the grand prix in 1st place)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


def race_name(n: int) -> str:
    return f"Win Race {n}"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_RACE + 1):
        table[race_name(n)] = LocationInfo(n, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# every location is reachable from the start -- no item gating anywhere in this game
sphere_1_locs: list[str] = list(location_table.keys())


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Races"] = {f"{GAME_NAME} - {race_name(n)}" for n in range(1, NUM_RACE + 1)}
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
