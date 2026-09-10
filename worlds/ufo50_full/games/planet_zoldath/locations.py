from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Planet Zoldath"
REGION = "The Planet"

NUM_RANDOM_CHECKS = 15
MAP_TYPES: tuple[str, ...] = ("Overworld", "Trade", "Dungeon")
PIECES_PER_MAP = 3   # 3 checks per map type, unlocked one per pickup across runs

# id offset layout inside Planet Zoldath's 1000-id block:
#     1..15    Random Check <n>   -- every energy cube becomes an AP pickup;
#              sent cumulatively in pickup order.
#    21..23    Overworld Map Piece 1..3    24..26  Trade Map Piece 1..3
#    27..29    Dungeon Map Piece 1..3   -- one physical o48_TreasureMap pickup per type,
#              each pickup sends only the next uncollected piece of that type (Zoldath is
#              a roguelike: the map regenerates each run, so 3 runs collect all 3).
#   200        +1 Starting Resource (filler)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def map_piece_name(map_type: str, piece: int) -> str:
    return f"{map_type} Map Piece {piece}"


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_RANDOM_CHECKS + 1):
        table[f"Random Check {n}"] = LocationInfo(n, REGION)
    for i, mt in enumerate(MAP_TYPES):
        for p in range(1, PIECES_PER_MAP + 1):
            table[map_piece_name(mt, p)] = LocationInfo(21 + i * PIECES_PER_MAP + (p - 1), REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# the first six random checks need nothing (rules.py gates the rest by tier)
sphere_1_locs: list[str] = [f"Random Check {n}" for n in range(1, 7)]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Random Checks"] = {
        f"{GAME_NAME} - Random Check {n}" for n in range(1, NUM_RANDOM_CHECKS + 1)
    }
    groups[f"{GAME_NAME} - Map Pieces"] = {
        f"{GAME_NAME} - {map_piece_name(mt, p)}"
        for mt in MAP_TYPES for p in range(1, PIECES_PER_MAP + 1)
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
