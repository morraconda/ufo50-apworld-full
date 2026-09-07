from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Magic Garden"

OPPY_THRESHOLDS = (15, 30, 50, 100, 150)
SCORE_THRESHOLDS = (1000, 5000, 10000)

# id offset layout inside Magic Garden's 1000-id block (thresholds hit within a
# single run -- the mod sends the check the moment savedTotal/myScore/multiplier
# crosses the value):
#    1..5   <n> Oppies Saved   (15 / 30 / 50 / 100 / 150 oppies dropped on stars)
#   11..13  <n> Score          (1000 / 5000 / 10000 points)
#   21      8x Multiplier      (reach an 8x score multiplier during an eating frenzy)
#   997/998/999   Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int


def _build_location_table() -> dict[str, "LocationInfo"]:
    table: dict[str, LocationInfo] = {}
    for offset, n in enumerate(OPPY_THRESHOLDS, start=1):
        table[f"{n} Oppies Saved"] = LocationInfo(offset)
    for offset, n in enumerate(SCORE_THRESHOLDS, start=11):
        table[f"{n} Score"] = LocationInfo(offset)
    table["8x Multiplier"] = LocationInfo(21)
    # goal locations last so create_locations' Cherry/Gold handling can break out safely
    table["Garden"] = LocationInfo(997)
    table["Gold"] = LocationInfo(998)
    table["Cherry"] = LocationInfo(999)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable from the start with no items
sphere_1_locs: list[str] = ["Garden", "15 Oppies Saved"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Oppies Saved"] = {f"{GAME_NAME} - {n} Oppies Saved" for n in OPPY_THRESHOLDS}
    groups[f"{GAME_NAME} - Score"] = {f"{GAME_NAME} - {n} Score" for n in SCORE_THRESHOLDS}
    return groups


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    field = regions["Field"]
    for loc_name, loc_data in location_table.items():
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, field)
            continue

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, field)
        field.locations.append(loc)
