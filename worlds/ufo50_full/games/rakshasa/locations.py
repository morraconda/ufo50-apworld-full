from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rakshasa"

# Rakshasa's three stages, each with a mid-boss:
#   Stage 1  -> region "Stage 1"   miniboss = o24_eTroll
#   Stage 2  -> region "Stage 2"   miniboss = o24_eTriyeTorso   (needs 2 weapons)
#   Stage 3  -> region "Stage 3"   miniboss = o24_eGoruk        (needs all 3 weapons)
# "Level N" is sent when the o24_StageEnd sequence hits its "STAGE CLEAR" screen;
# "Level N Miniboss" when that stage's mid-boss dies.

# id offset layout inside Rakshasa's 1000-id block:
#     1..3   Level <n>            (stage n cleared)
#     4..6   Level <n> Miniboss   (stage n mid-boss defeated; offset = 3 + n)
#   200      500 Points (filler)
#   511..513 Weapon 1..3
#   997/998/999   Gift / Gold / Cherry

REGIONS: tuple[str, ...] = ("Stage 1", "Stage 2", "Stage 3")


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, 4):
        region = f"Stage {n}"
        table[f"Level {n}"] = LocationInfo(n, region)
        table[f"Level {n} Miniboss"] = LocationInfo(3 + n, region)
    table["Gift"] = LocationInfo(997, "Stage 1")
    table["Gold"] = LocationInfo(998, "Stage 3")
    table["Cherry"] = LocationInfo(999, "Stage 3")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# stage 1 (its clear + miniboss) and Gift need nothing; rules.py gates stages 2 and 3
sphere_1_locs: list[str] = ["Level 1", "Level 1 Miniboss", "Gift"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Levels"] = {f"{GAME_NAME} - Level {n}" for n in range(1, 4)}
    groups[f"{GAME_NAME} - Minibosses"] = {f"{GAME_NAME} - Level {n} Miniboss" for n in range(1, 4)}
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
