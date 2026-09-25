from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Camouflage"
REGION = "The Jungle"
SKY_TEMPLE_REGION = "Sky Temple"

# Camouflage has 15 levels (o04_Game.levelPercent[1..15]; > 0 means escaped/cleared).
# Levels 1..14 each have 3 collectibles -- 1 baby + 2 fruits -- worth BABY_PERCENT (30)
# and FRUIT_PERCENT (20) on top of ESCAPE_PERCENT (30); 100% == all 3. Level 15 (the
# finale) has no collectibles. Names are the in-game level_1..level_15 strings for
# game 4 (ext/<lang>/4_Text.json).
LEVEL_NAMES: tuple[str, ...] = (
    "West Isle", "The Ponds", "River Lands", "Three Watchmen", "Crocodile Isle",
    "Swamp Run", "Rocky Valley", "The Crossing", "Oasis", "Sunny Banks",
    "Devil's Pass", "Dry Gulch", "Rain or Shine", "The Cliffs", "Sky Temple",
)
LEVEL_COUNT = len(LEVEL_NAMES)
COLLECTIBLE_LEVELS = 14
COLLECTIBLES = ("Baby", "Fruit 1", "Fruit 2")

# id offset layout inside Camouflage's 1000-id block, via game_helpers.level_id
# (offset = level * 10 + slot):
#    10..150   <level name>                  (level cleared; level_id(n, 0))
#    11..143   <level name> - <collectible>  (levels 1..14; level_id(n, 1 + k),
#              k = 0 Baby / 1 Fruit 1 / 2 Fruit 2)
#     1        Camouflage (item)
#   200        Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    # Sky Temple (level 15, the finale) is beatable without Camouflage; clearing it is
    # also Gold. Everything else (incl. Gift / Cherry) needs Camouflage.
    for n, level in enumerate(LEVEL_NAMES, start=1):
        region = SKY_TEMPLE_REGION if n == LEVEL_COUNT else REGION
        table[level] = LocationInfo(level_id(n, 0), region)
    for n in range(1, COLLECTIBLE_LEVELS + 1):
        level = LEVEL_NAMES[n - 1]
        for k, name in enumerate(COLLECTIBLES):
            table[f"{level} - {name}"] = LocationInfo(level_id(n, 1 + k), REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, SKY_TEMPLE_REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

sphere_1_locs: list[str] = [name for name, info in location_table.items()
                             if info.region_name == SKY_TEMPLE_REGION]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Levels"] = {f"{GAME_NAME} - {level}" for level in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Collectibles"] = {
        f"{GAME_NAME} - {LEVEL_NAMES[n - 1]} - {name}"
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
