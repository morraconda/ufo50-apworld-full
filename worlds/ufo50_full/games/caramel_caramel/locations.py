from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Caramel Caramel"
UNIT = "Level"
REGION = "The Shoot"

# Level display names by normalizedLevel 1..6 (the same numbering scr46_SaveGame
# uses for highestLevel), from ext/ENGLISH/46_Text.json "level_1".."level_7".
# The one-off PROLOGUE (room level 5) normalizes back to 1, so it is not its own
# location; FINALE (room level 6) is normalizedLevel 6.
LEVEL_NAMES: tuple[str, ...] = (
    "Snack Planet",
    "Orb Shower A",
    "Ghost Planet",
    "Orb Shower B",
    "Dino Planet",
    "Finale",
)
NUM_LEVEL = len(LEVEL_NAMES)

# Two named bosses, defeated (their enemy object's Destroy at life < 1):
#   Cookie -> o46_eBella ; Toad -> o46_eToadead
BOSS_NAMES: tuple[str, ...] = ("Cookie", "Toad")

# id offset layout inside Caramel Caramel's 1000-id block:
#     1..6   <level name>   (reached level n; offset = normalizedLevel)
#     7..8   Cookie / Toad  (boss defeated)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(LEVEL_NAMES, start=1):
        table[name] = LocationInfo(n, REGION)
    for i, name in enumerate(BOSS_NAMES):
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
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Bosses"] = {f"{GAME_NAME} - {name}" for name in BOSS_NAMES}
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
