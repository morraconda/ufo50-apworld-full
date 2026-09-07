from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rail Heist"
NUM_LEVELS = 20

# the three checks present on every level
CLEAR = "Clear"
ANGEL = "Angel Star"
DEVIL = "Devil Star"
CHECK_TYPES = (CLEAR, ANGEL, DEVIL)

# id offset layout inside Rail Heist's 1000-id block: grouped by level via
# game_helpers.level_id -- offset = level * 10 + check-type slot. So A Simple Heist
# (level 1) = 10/11/12, Roof Assault (level 2) = 20/21/22, ... The Final Score
# (level 20) = 200/201/202.
#   997/998/999   Garden / Gold / Cherry
CHECK_TYPE_SLOT: dict[str, int] = {
    CLEAR: 0,
    ANGEL: 1,
    DEVIL: 2,
}

# In-game mission names for Rail Heist's 20 levels, in play order, keyed by level
# number. Source: the game's ext/ENGLISH/13_Text.json, keys mission_name_1..20.
LEVEL_NAMES: dict[int, str] = {
    1: "A Simple Heist",
    2: "Roof Assault",
    3: "Cargo Ambush",
    4: "High Alert",
    5: "Fowl Business",
    6: "Guarded by Gat",
    7: "Shifting Gears",
    8: "Vault Robbery",
    9: "Winging It",
    10: "Daring Duo",
    11: "Root Around",
    12: "Cow Poke",
    13: "Rescue Mission",
    14: "Long Haul",
    15: "Resupply",
    16: "Armored Up",
    17: "Powder Keg",
    18: "Sitting Ducks",
    19: "Vengeance!",
    20: "The Final Score",
}


def check_location_name(level: int, check_type: str) -> str:
    """Location name for one of a level's checks. The Clear check is just the level
    name -- a bare level name implies its clear -- while Angel / Devil Star are suffixed."""
    if check_type == CLEAR:
        return LEVEL_NAMES[level]
    return f"{LEVEL_NAMES[level]} - {check_type}"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str
    level: int  # 1-indexed level number; 0 for the goal (Garden/Gold/Cherry) locations
    check_type: str  # one of CHECK_TYPES; "" for the goal locations


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for check_type in CHECK_TYPES:
        for level in range(1, NUM_LEVELS + 1):
            table[check_location_name(level, check_type)] = LocationInfo(
                level_id(level, CHECK_TYPE_SLOT[check_type]), "Levels", level, check_type)
    # goal locations always come last so create_locations' Cherry/Gold handling can break out safely
    table["Garden"] = LocationInfo(997, "Levels", 0, "")
    table["Gold"] = LocationInfo(998, "Levels", 0, "")
    table["Cherry"] = LocationInfo(999, "Levels", 0, "")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# "A Simple Heist Time" is precollected (see items.create_items), so all three of Level
# 1's checks are always reachable and seed the fill. The Garden prize (Level 10) is NOT
# sphere 1.
sphere_1_locs: list[str] = [check_location_name(1, check_type) for check_type in CHECK_TYPES]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    for check_type in CHECK_TYPES:
        groups[f"{GAME_NAME} - {check_type}"] = {
            f"{GAME_NAME} - {check_location_name(level, check_type)}" for level in range(1, NUM_LEVELS + 1)
        }
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
