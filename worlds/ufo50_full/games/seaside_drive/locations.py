from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Seaside Drive"
UNIT = "Stage"
NUM_STAGE = 4   # o47_Control.level 0..3 -- "BEAT ALL 4 STAGES" (bonus stage not counted)
REGION = "The Drive"

# id offset layout inside Seaside Drive's 1000-id block:
#     1..4   Stage <n>   (cleared stage n; Stage 4 == "FINAL STAGE")
#   101      Progressive Max Charge (item, see items.py)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_STAGE + 1):
        table[f"{UNIT} {n}"] = LocationInfo(n, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# Stage 1 / Stage 2 / Gift need no charge; Stage 3 needs 2 Progressive Max Charge,
# Stage 4 + Gold need 3, Cherry needs all 4 (rules.py).
sphere_1_locs: list[str] = ["Stage 1", "Stage 2", "Gift"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {UNIT} {n}" for n in range(1, NUM_STAGE + 1)}
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
