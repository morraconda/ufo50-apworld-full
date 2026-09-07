from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Cyber Owls"
REGION = "The Ops"

# Cyber Owls's checks are the nine bosses (each is its own enemy object; the location
# is sent when that object is destroyed at hp <= 0). No level/mission checks.
#   Hong Kong    Road Toad            (o45_eToad)
#   Congo Basin  Maniyak / Psycow     (o45_eManiyak / o45_ePsycow -- the dual boss)
#   Chicago      Pyrat                (o45_ePyrat)
#   Moscow       Hackoon              (o45_eHackoon)
#   Antarctica   Dr. Dillo / Missile / Hawk Commander / Tank
#                (o45_eDoctor / o45_eNuke / o45_eHawk / o45_eFinalTank)
BOSS_NAMES: tuple[str, ...] = (
    "Road Toad",
    "Maniyak",
    "Psycow",
    "Pyrat",
    "Hackoon",
    "Dr. Dillo",
    "Missile",
    "Hawk Commander",
    "Tank",
)

# id offset layout inside Cyber Owls's 1000-id block:
#     1..9   <boss name>   (offset = list position; see the mod's per-boss Destroy hook)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(BOSS_NAMES, start=1):
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
