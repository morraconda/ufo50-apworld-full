from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Divers"
REGION = "The Depths"

# The 17 treasure chests, by their o19_Chest `num` index (type[num]/value[num] set in
# o19_Chest_Create_0; global.g19_chestOpen[num] persists). Chest 50 also fires the
# vanilla scrWin(GARDEN_WIN) = Gift.
CHEST_NUMS: tuple[int, ...] = (10, 11, 12, 13, 14, 20, 21, 22, 23, 24, 30, 40, 41, 50, 60, 61, 70)
# Player level (global.g19_level, 1..16); a check for reaching each of 2..10.
LEVEL_CHECKS: tuple[int, ...] = tuple(range(2, 11))

# id offset layout inside Divers's 1000-id block:
#     1..9    Level <2..10>   (player reached that level; offset = level - 1)
#    10..70   Chest <num>           (offset = the chest's num index)
#   200       +200 Gold (filler)
#   511       +20% XP Multiplier
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for lvl in LEVEL_CHECKS:
        table[f"Level {lvl}"] = LocationInfo(lvl - 1, REGION)
    for num in CHEST_NUMS:
        table[f"Chest {num}"] = LocationInfo(num, REGION)
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
    groups[f"{GAME_NAME} - Chests"] = {f"{GAME_NAME} - Chest {num}" for num in CHEST_NUMS}
    groups[f"{GAME_NAME} - Levels"] = {f"{GAME_NAME} - Level {lvl}" for lvl in LEVEL_CHECKS}
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
