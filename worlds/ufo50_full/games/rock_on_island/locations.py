from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rock On! Island"

# Rock On! Island's 10 tower-defense levels (o44__Game.level[1..10]; value 1 = cleared,
# 2 = perfect/no-damage clear) + the 2 village map nodes (currLevel 0 / 11).
# Levels 1-5 have known names; 6-10 are generic.
LEVEL_NAMES: tuple[str, ...] = (
    "Initial Encounter", "Spiral", "Underbrush", "Wasteland", "Crossroads",
    "Level 6", "Level 7", "Level 8", "Level 9", "Level 10",
)
VILLAGE_PEACE = "Village of Peace"
VILLAGE_TWO = "Second Village"

# regions (rules.py chains them): The Island (free) -> Fireside (Progressive Fire >= 1)
#   -> Spearpoint (Progressive Spear >= 2) -> Mastery (every progression item)
R_ISLAND = "The Island"
R_FIRE = "Fireside"
R_SPEAR = "Spearpoint"
R_MASTERY = "Mastery"

# 1-Fire tier: Initial Encounter (+ perfect), Spiral (+ perfect), Underbrush, Wasteland,
# Crossroads (clears only). Everything else's clear + the Second Village -> Spearpoint.
# The remaining 8 perfects -> Mastery.
_FIRE_CLEARS = {"Initial Encounter", "Spiral", "Underbrush", "Wasteland", "Crossroads"}
_FIRE_PERFECTS = {"Initial Encounter", "Spiral"}

# id offset layout inside Rock On! Island's 1000-id block:
#     1..10   <level name>            (level cleared)
#    11..20   <level name> Perfect    (level cleared with no damage; offset = 10 + n)
#    21       Village of Peace        (entered node currLevel 0)
#    22       Second Village          (entered node currLevel 11)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(LEVEL_NAMES, start=1):
        clear_region = R_FIRE if name in _FIRE_CLEARS else R_SPEAR
        table[name] = LocationInfo(n, clear_region)
        perfect_region = R_FIRE if name in _FIRE_PERFECTS else R_MASTERY
        table[f"{name} Perfect"] = LocationInfo(10 + n, perfect_region)
    table[VILLAGE_PEACE] = LocationInfo(21, R_ISLAND)
    table[VILLAGE_TWO] = LocationInfo(22, R_SPEAR)
    table["Gift"] = LocationInfo(997, R_SPEAR)
    table["Gold"] = LocationInfo(998, R_SPEAR)
    table["Cherry"] = LocationInfo(999, R_SPEAR)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# only the starting village needs nothing; rules.py gates the rest
sphere_1_locs: list[str] = [VILLAGE_PEACE]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Levels"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Perfects"] = {f"{GAME_NAME} - {name} Perfect" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Villages"] = {f"{GAME_NAME} - {VILLAGE_PEACE}", f"{GAME_NAME} - {VILLAGE_TWO}"}
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
