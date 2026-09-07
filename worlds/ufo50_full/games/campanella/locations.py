from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella"
REGION = "Space"

# o03_Mas.currStage runs 0..49 = 5 worlds x 10 slots. Slot names match the game's
# stageName[] (slot 4 = the bonus stage, slot 9 = the boss).
WORLDS: tuple[str, ...] = ("A", "B", "C", "D", "E")
SLOT_NAMES: tuple[str, ...] = ("1", "2", "3", "4", "Bonus", "6", "7", "8", "9", "Boss")
COFFEE_SLOTS: tuple[int, ...] = (0, 1, 2, 3, 5, 6, 7, 8)   # one coffee each, not on Bonus/Boss
NUM_STAGES = len(WORLDS) * len(SLOT_NAMES)                 # 50
SCORE_MAX_K = 40                                           # point checks at 1000..40000


def stage_name(currstage: int) -> str:
    return f"{WORLDS[currstage // 10]}-{SLOT_NAMES[currstage % 10]}"


def coffee_currstages() -> list[int]:
    return [w * 10 + s for w in range(len(WORLDS)) for s in COFFEE_SLOTS]


# id offset layout inside Campanella's 1000-id block:
#     1..50    <stage> clear         (offset = currStage + 1)
#   100..148   <stage> - Coffee      (offset = 100 + currStage)
#   201..240   <n>000 Points         (offset = 200 + n)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for s in range(NUM_STAGES):
        table[stage_name(s)] = LocationInfo(s + 1, REGION)
    for s in coffee_currstages():
        table[f"{stage_name(s)} - Coffee"] = LocationInfo(100 + s, REGION)
    for k in range(1, SCORE_MAX_K + 1):
        table[f"{k * 1000} Points"] = LocationInfo(200 + k, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# nothing is region-gated; per-location rules (rules.py) handle the life / Left Thruster
# requirements. Only the stuff that needs neither is truly sphere 1.
sphere_1_locs: list[str] = [
    "A-1", "A-2", "A-3", "A-1 - Coffee", "A-2 - Coffee", "A-4 - Coffee", "1000 Points",
]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Stages"] = {f"{GAME_NAME} - {stage_name(s)}" for s in range(NUM_STAGES)}
    groups[f"{GAME_NAME} - Coffees"] = {f"{GAME_NAME} - {stage_name(s)} - Coffee" for s in coffee_currstages()}
    groups[f"{GAME_NAME} - Points"] = {f"{GAME_NAME} - {k * 1000} Points" for k in range(1, SCORE_MAX_K + 1)}
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
