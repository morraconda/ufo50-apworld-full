from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Camouflage"
REGION = "The Jungle"

# Camouflage has 15 levels (o04_Game.levelPercent[1..15]; > 0 means escaped/cleared).
# Levels 1..14 each have 3 collectibles -- 1 baby + 2 fruits -- worth BABY_PERCENT (30)
# and FRUIT_PERCENT (20) on top of ESCAPE_PERCENT (30); 100% == all 3. Level 15 (the
# finale) has no collectibles.
LEVEL_COUNT = 15
COLLECTIBLE_LEVELS = 14
COLLECTIBLES = ("Baby", "Fruit 1", "Fruit 2")

# id offset layout inside Camouflage's 1000-id block:
#     1..15    Level <n>                     (level cleared)
#   100..141   Level <n> - <collectible>     (n 1..14; offset = 100 + (n-1)*3 + k)
#   200        Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, LEVEL_COUNT + 1):
        table[f"Level {n}"] = LocationInfo(n, REGION)
    for n in range(1, COLLECTIBLE_LEVELS + 1):
        for k, name in enumerate(COLLECTIBLES):
            table[f"Level {n} - {name}"] = LocationInfo(100 + (n - 1) * 3 + k, REGION)
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
    groups[f"{GAME_NAME} - Levels"] = {f"{GAME_NAME} - Level {n}" for n in range(1, LEVEL_COUNT + 1)}
    groups[f"{GAME_NAME} - Collectibles"] = {
        f"{GAME_NAME} - Level {n} - {name}"
        for n in range(1, COLLECTIBLE_LEVELS + 1) for name in COLLECTIBLES
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
