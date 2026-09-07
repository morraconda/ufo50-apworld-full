from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol"
NUM_LEVELS = 10

# In-game stage names in play order (world-substage): worlds 1 and 2 have A/B/C,
# worlds 3 and 4 have A/B. LEVEL_NAMES[n - 1] is play-order level n.
LEVEL_NAMES: list[str] = ["1-A", "1-B", "1-C", "2-A", "2-B", "2-C", "3-A", "3-B", "4-A", "4-B"]


def level_name(lvl: int) -> str:
    """Stage name for a 1-indexed play-order level (1 -> "1-A", ... 10 -> "4-B")."""
    return LEVEL_NAMES[lvl - 1]


# Every life pickup in rm29_Sacrifice, as (x, y, num_lives, level), extracted from the
# vanilla room and sorted by (y, x). The pickup's location number is its 1-based index
# in this list. `level` is the 1..10 play order: the room is one tall stage split into
# 256px y-bands, and Mortol's `lvl` runs 1,3,4,5,6,7,8,9,10,11 (band + 1, "2" skipped),
# which we remap to 1..10. Level 10 ("4-B", the boss) has no pickups.
PICKUPS: list[tuple[int, int, int, int]] = [
    (2832, 32, 5, 1), (3872, 128, 10, 1), (3632, 144, 3, 1), (2608, 160, 3, 1),
    (928, 176, 3, 1), (1360, 176, 3, 1),
    (3936, 544, 5, 2), (656, 624, 3, 2), (1376, 624, 5, 2), (912, 640, 5, 2),
    (2240, 656, 3, 2), (3104, 688, 5, 2), (3920, 688, 10, 2),
    (3904, 896, 10, 3), (432, 912, 3, 3), (3104, 928, 3, 3), (1440, 944, 3, 3),
    (2000, 944, 3, 3), (2336, 944, 5, 3), (1104, 960, 3, 3),
    (2960, 1056, 3, 4), (976, 1072, 3, 4), (1328, 1104, 3, 4), (2272, 1136, 3, 4),
    (1856, 1168, 3, 4), (3840, 1168, 10, 4), (3584, 1200, 3, 4),
    (2272, 1296, 3, 5), (2896, 1296, 3, 5), (3904, 1392, 10, 5), (3392, 1440, 3, 5),
    (688, 1456, 3, 5), (3008, 1456, 3, 5),
    (2368, 1584, 5, 6), (3904, 1648, 10, 6), (3112, 1672, 3, 6), (144, 1712, 3, 6),
    (1584, 1728, 3, 6), (1728, 1728, 5, 6),
    (464, 1808, 5, 7), (3400, 1808, 5, 7), (2368, 1824, 5, 7), (3920, 1824, 10, 7),
    (832, 1888, 3, 7), (1728, 1984, 3, 7), (2624, 1984, 5, 7),
    (3296, 2080, 3, 8), (3872, 2080, 10, 8), (1504, 2208, 5, 8), (1744, 2208, 3, 8),
    (2432, 2224, 5, 8), (320, 2240, 5, 8),
    (3568, 2320, 5, 9), (1216, 2336, 5, 9), (1136, 2384, 5, 9), (640, 2416, 3, 9),
    (3024, 2432, 3, 9), (1888, 2448, 5, 9), (2512, 2464, 5, 9), (3920, 2464, 10, 9),
]

# id offset layout inside Mortol's 1000-id block, grouped by level via
# game_helpers.level_id -- offset = level * 10 + slot:
#   <lvl>*10        <stage>                     (level clear, slot 0)
#   <lvl>*10 + <y>  <stage> - Life Pickup <y>   (slot 1..8, in PICKUPS order)
#   200..203       items (see items.py)
#   997/998/999    Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for lvl in range(1, NUM_LEVELS + 1):
        table[level_name(lvl)] = LocationInfo(level_id(lvl, 0), level_name(lvl))
    per_level: dict[int, int] = {}
    for _x, _y, _n, lvl in PICKUPS:
        per_level[lvl] = per_level.get(lvl, 0) + 1
        table[f"{level_name(lvl)} - Life Pickup {per_level[lvl]}"] = LocationInfo(
            level_id(lvl, per_level[lvl]), level_name(lvl))
    # goal locations last (Cherry/Gold handling in create_locations breaks out)
    table["Garden"] = LocationInfo(997, level_name(6))   # vanilla fires GARDEN_WIN on clearing 2-C
    table["Gold"] = LocationInfo(998, level_name(NUM_LEVELS))
    table["Cherry"] = LocationInfo(999, level_name(NUM_LEVELS))
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# Stage 1-A is always reachable from the start.
sphere_1_locs: list[str] = [level_name(1)]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Level Clears"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Life Pickups"] = {f"{GAME_NAME} - {loc_name}" for loc_name in location_table
                                             if "Life Pickup" in loc_name}
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
