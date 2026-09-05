from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import (skip_cherry_location_if_disabled, is_completion_event_location,
                               place_completion_event)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"
NUM_CHESTS = 5   # cumulative across runs -- 3 chests spawn per journey (2 procedural + 1 in the castle)
NUM_SIGNS = 10   # cumulative sign reads (the game tracks signCount up to 22)

# id offset layout inside Waldorf's Journey's 1000-id block:
#     1..5     Chest <n>   (opened your n-th chest, counted across all runs)
#    11..20    Sign <n>    (read your n-th sign, counted across all runs)
#   101..106   items (see items.py)
#   200        Shell (filler)
#   997/998/999   Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_CHESTS + 1):
        table[f"Chest {n}"] = LocationInfo(n, "Island")
    for n in range(1, NUM_SIGNS + 1):
        table[f"Sign {n}"] = LocationInfo(10 + n, "Island")
    table["Garden"] = LocationInfo(997, "Island")
    table["Gold"] = LocationInfo(998, "Island")
    table["Cherry"] = LocationInfo(999, "Island")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# every check is reachable from the start
sphere_1_locs: list[str] = list(location_table.keys())


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Chests"] = {f"{GAME_NAME} - Chest {n}" for n in range(1, NUM_CHESTS + 1)}
    groups[f"{GAME_NAME} - Signs"] = {f"{GAME_NAME} - Sign {n}" for n in range(1, NUM_SIGNS + 1)}
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
