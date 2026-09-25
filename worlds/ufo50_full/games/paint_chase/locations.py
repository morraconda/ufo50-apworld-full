from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Paint Chase"
UNIT = "Level"
NUM_LEVEL = 26   # o49_Game.level, 1..LAST_LEVEL(26)
REGION = "The Circuit"

# id offset layout inside Paint Chase's 1000-id block, via game_helpers.level_id
# (offset = level * 10 + slot):
#     1      Turn Left (item)
#    10..260   Level <n>   (cleared level n; level_id(n, 0))
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_LEVEL + 1):
        table[f"{UNIT} {n}"] = LocationInfo(level_id(n, 0), REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# levels 1..FREE_LEVELS need no Turn Left (rules.tier1)
FREE_LEVELS = 3
sphere_1_locs: list[str] = [f"{UNIT} {n}" for n in range(1, FREE_LEVELS + 1)]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {UNIT} {n}" for n in range(1, NUM_LEVEL + 1)}
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
