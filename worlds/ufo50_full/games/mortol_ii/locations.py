from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# 17 lettered key pickups A..Q, 3 coloured switches, 3 bosses.
KEY_LETTERS = "ABCDEFGHIJKLMNOPQ"
SWITCH_COLORS = ("Blue", "Yellow", "Green")
NUM_BOSSES = 3

# id offset layout inside Mortol II's 1000-id block:
#    1..17   Key A .. Key Q
#   21..23   Blue / Yellow / Green Switch
#   31..33   Boss 1 .. Boss 3
#   998/999  Gold / Cherry  (both = "beat the game"; this game has no Garden prize)


class LocationInfo(NamedTuple):
    id_offset: int


def _build_location_table() -> dict[str, "LocationInfo"]:
    table: dict[str, LocationInfo] = {}
    for offset, letter in enumerate(KEY_LETTERS, start=1):
        table[f"Key {letter}"] = LocationInfo(offset)
    for offset, color in enumerate(SWITCH_COLORS, start=21):
        table[f"{color} Switch"] = LocationInfo(offset)
    for n in range(1, NUM_BOSSES + 1):
        table[f"Boss {n}"] = LocationInfo(30 + n)
    # goal locations last so create_locations' Cherry/Gold handling can break out safely
    table["Gold"] = LocationInfo(998)
    table["Cherry"] = LocationInfo(999)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# "Key A" is the only check reachable with no items ("Always").
sphere_1_locs: list[str] = ["Key A"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Keys"] = {f"{GAME_NAME} - Key {letter}" for letter in KEY_LETTERS}
    groups[f"{GAME_NAME} - Switches"] = {f"{GAME_NAME} - {c} Switch" for c in SWITCH_COLORS}
    groups[f"{GAME_NAME} - Bosses"] = {f"{GAME_NAME} - Boss {n}" for n in range(1, NUM_BOSSES + 1)}
    return groups


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    ruins = regions["Ruins"]
    for loc_name, loc_data in location_table.items():
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, ruins)
            continue

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, ruins)
        ruins.locations.append(loc)
