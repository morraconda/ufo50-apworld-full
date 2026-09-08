from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Valbrace"
REGION = "The Descent"

# Valbrace descends floors 0..6 (o35_Game.currentFloor / global.deepestFloor). Checks:
#   Floor 0..5   sent when you have *left* that floor (global.deepestFloor >= n + 1).
#   3 bosses     Phantom Knight (floor 2, o35_ePhantomKnight),
#                Hive Queen     (floor 4, o35_eBroodQueen),
#                Abyss Lord     (floor 6, o35_eAbyssLord -- the final boss).
FLOOR_COUNT = 6            # Floor 0 .. Floor 5
# (name, floor) -- the floor is only informational; the mod hooks each by offset.
BOSSES: tuple[tuple[str, int], ...] = (
    ("Phantom Knight", 2),
    ("Hive Queen", 4),
    ("Abyss Lord", 6),
)

# id offset layout inside Valbrace's 1000-id block:
#     1..6    Floor 0..5      (offset = floor number + 1; sent on leaving that floor)
#     7..9    Phantom Knight / Hive Queen / Abyss Lord
#   200       Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(FLOOR_COUNT):
        table[f"Floor {n}"] = LocationInfo(n + 1, REGION)
    for i, (name, _floor) in enumerate(BOSSES):
        table[name] = LocationInfo(7 + i, REGION)
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
    groups[f"{GAME_NAME} - Floors"] = {f"{GAME_NAME} - Floor {n}" for n in range(FLOOR_COUNT)}
    groups[f"{GAME_NAME} - Bosses"] = {f"{GAME_NAME} - {name}" for name, _floor in BOSSES}
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
