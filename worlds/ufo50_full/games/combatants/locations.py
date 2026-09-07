from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Combatants"
REGION = "The Campaign"

# Combatants is a 12-mission real-time strategy campaign (o25__Game, `mapComplete[i]`
# for map node `indexNum` 0..11). Each location is sent when that mission's node is
# cleared; missions can be tackled in branching order, so no cumulative sweep is
# needed -- the mod just watches the array.
MISSION_COUNT = 12

# id offset layout inside Combatants's 1000-id block:
#     1..12   Mission <n>   (offset = map node indexNum + 1)
#   200       Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, MISSION_COUNT + 1):
        table[f"Mission {n}"] = LocationInfo(n, REGION)
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
    groups[f"{GAME_NAME} - Missions"] = {f"{GAME_NAME} - Mission {n}" for n in range(1, MISSION_COUNT + 1)}
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
