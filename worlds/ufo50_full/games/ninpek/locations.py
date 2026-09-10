from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Ninpek"
REGION = "The Run"
DEEP_REGION = "Deep Run"     # behind all 5 Shuriken -- holds Gold / Cherry

# Ninpek's checks are score milestones every 5,000 points up to 40,000 (o34_Mas.points[0]).
SCORE_STEP = 5000
NUM_STEPS = 8
SHINY_FREE_SCORE = 5000      # reachable with no Shuriken (pickups / bonuses, no shooting)
SCORE_PER_SHURIKEN = 10000   # each Shuriken opens up this much more score in logic

# id offset layout inside Ninpek's 1000-id block:
#     1..8   <n*5000> Points   (offset = milestone index; sent when points[0] reaches it)
#   100      Shuriken (x5, progression)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def shuriken_needed(score: int) -> int:
    """Shuriken required in logic for a given score milestone (uncapped)."""
    if score <= SHINY_FREE_SCORE:
        return 0
    return -(-(score - SHINY_FREE_SCORE) // SCORE_PER_SHURIKEN)   # ceil division


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_STEPS + 1):
        table[f"{n * SCORE_STEP} Points"] = LocationInfo(n, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, DEEP_REGION)
    table["Cherry"] = LocationInfo(999, DEEP_REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items: Gift and the one score milestone that needs 0 Shuriken
sphere_1_locs: list[str] = ["Gift", f"{SHINY_FREE_SCORE} Points"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Score Milestones"] = {
        f"{GAME_NAME} - {n * SCORE_STEP} Points" for n in range(1, NUM_STEPS + 1)
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
