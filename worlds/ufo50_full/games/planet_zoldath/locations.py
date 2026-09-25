from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Planet Zoldath"
REGION = "The Planet"

NUM_RANDOM_CHECKS = 10
MAP_TYPES: tuple[str, ...] = ("Overworld", "Trade", "Dungeon")
# checks per map type, unlocked one per pickup across runs
PIECES_PER_MAP: dict[str, int] = {"Overworld": 3, "Trade": 2, "Dungeon": 2}

# holding this many of EVERY resource simultaneously (min across the 4 types)
ALL_RESOURCE_THRESHOLDS: tuple[int, ...] = (1, 3, 5, 10, 20, 31)
# holding this many of ANY one resource (max across the 4 types)
ANY_RESOURCE_THRESHOLDS: tuple[int, ...] = (3, 5, 10, 20, 30, 40, 50, 63)

# id offset layout inside Planet Zoldath's 1000-id block:
#     1..10    Random Check <n>   -- every energy cube becomes an AP pickup;
#              sent cumulatively in pickup order.
#    21..23    Overworld Map Piece 1..3    24..25  Trade Map Piece 1..2
#    26..27    Dungeon Map Piece 1..2   -- one physical o48_TreasureMap pickup per type,
#              each pickup sends only the next uncollected piece of that type (Zoldath is
#              a roguelike: the map regenerates each run, so N runs collect all N pieces
#              of that type).
#    28..33    <n> of All Resources (min(resources[0..3]) >= n; ALL_RESOURCE_THRESHOLDS)
#    34..41    <n> of Any Resource (max(resources[0..3]) >= n; ANY_RESOURCE_THRESHOLDS)
#              -- resources fluctuate (spent on trades/items), so these are a ladder:
#              once reached they stay collected, same as the map/random checks.
#   200        +1 Starting Resource (filler)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def map_piece_name(map_type: str, piece: int) -> str:
    return f"{map_type} Map Piece {piece}"


def all_resource_name(n: int) -> str:
    return f"{n} of All Resources"


def any_resource_name(n: int) -> str:
    return f"{n} of Any Resource"


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_RANDOM_CHECKS + 1):
        table[f"Random Check {n}"] = LocationInfo(n, REGION)
    offset = 21
    for mt in MAP_TYPES:
        for p in range(1, PIECES_PER_MAP[mt] + 1):
            table[map_piece_name(mt, p)] = LocationInfo(offset, REGION)
            offset += 1
    offset = 28
    for n in ALL_RESOURCE_THRESHOLDS:
        table[all_resource_name(n)] = LocationInfo(offset, REGION)
        offset += 1
    for n in ANY_RESOURCE_THRESHOLDS:
        table[any_resource_name(n)] = LocationInfo(offset, REGION)
        offset += 1
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# rules.py tier 1: the first five random checks and the lowest resource-ladder rungs
sphere_1_locs: list[str] = ([f"Random Check {n}" for n in range(1, 6)]
                            + [any_resource_name(n) for n in (3, 5, 10)])


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Random Checks"] = {
        f"{GAME_NAME} - Random Check {n}" for n in range(1, NUM_RANDOM_CHECKS + 1)
    }
    groups[f"{GAME_NAME} - Map Pieces"] = {
        f"{GAME_NAME} - {map_piece_name(mt, p)}"
        for mt in MAP_TYPES for p in range(1, PIECES_PER_MAP[mt] + 1)
    }
    groups[f"{GAME_NAME} - Resource Checks"] = (
        {f"{GAME_NAME} - {all_resource_name(n)}" for n in ALL_RESOURCE_THRESHOLDS}
        | {f"{GAME_NAME} - {any_resource_name(n)}" for n in ANY_RESOURCE_THRESHOLDS}
    )
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
