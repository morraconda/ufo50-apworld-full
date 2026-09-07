from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Avianos"
REGION = "The War"

# Avianos is an 8-scenario turn-based strategy game (o50_Game, `scenarioY` 0..7:
# the Hatchling/Fledgling/Adult campaign then Trials 1-5). Names from
# ext/ENGLISH/50_Text.json scenario_1..8; the location is sent on winning that scenario.
UNIT_NAMES: tuple[str, ...] = (
    "Hatchling",
    "Fledgling",
    "Adult",
    "Trial 1",
    "Trial 2",
    "Trial 3",
    "Trial 4",
    "Trial 5",
)
NUM_UNITS = len(UNIT_NAMES)

# id offset layout inside Avianos's 1000-id block:
#     1..8   <unit name>   (offset = play-order position)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(UNIT_NAMES, start=1):
        table[name] = LocationInfo(n, REGION)
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
    groups[f"{GAME_NAME} - Scenarios"] = {f"{GAME_NAME} - {name}" for name in UNIT_NAMES}
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
