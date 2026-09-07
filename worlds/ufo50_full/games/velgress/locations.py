from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Velgress"
NUM_LEVELS = 3               # o15_Game.level runs 1..3, one Cavian shop between each
SHOP_ITEMS_PER_LEVEL = 3     # selItem = sel + (level - 1) * 3, sel 0..2

# id offset layout inside Velgress' 1000-id block (level_id(level, slot) = level*10 + slot):
#    N0        Level <N>                  (cleared area N -- reached its shop)
#    N1..N3    Level <N> Shop - Item <k>  (bought the k-th of that shop's three slots)
#   101..106   upgrade items (see items.py)
#   200        Coin (filler)
#   997/998/999   Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_LEVELS + 1):
        table[f"Level {n}"] = LocationInfo(level_id(n, 0), "Tower")
        for k in range(1, SHOP_ITEMS_PER_LEVEL + 1):
            table[f"Level {n} Shop - Item {k}"] = LocationInfo(level_id(n, k), "Tower")
    table["Garden"] = LocationInfo(997, "Tower")
    table["Gold"] = LocationInfo(998, "Tower")
    table["Cherry"] = LocationInfo(999, "Tower")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# every check (level clears, shop purchases, Garden/Gold/Cherry) is reachable from the start
sphere_1_locs: list[str] = list(location_table.keys())


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Clears"] = {f"{GAME_NAME} - Level {n}" for n in range(1, NUM_LEVELS + 1)}
    groups[f"{GAME_NAME} - Shop"] = {f"{GAME_NAME} - Level {n} Shop - Item {k}"
                                     for n in range(1, NUM_LEVELS + 1)
                                     for k in range(1, SHOP_ITEMS_PER_LEVEL + 1)}
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
