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
#   200        +5 Coins (filler)
#   997/998/999   Gift / Gold / Cherry
#
# Floor N's clear + shop live in region "Tower N". You start on a single jump; a
# Progressive Jump opens "Tower 2" and a second opens "Tower 3" (rules.py). Only the
# "Tower 1" locations are in logic with no items. The Gift goal needs a key on two
# separate floors (o15 GARDEN_GOAL = 2), so it sits in "Tower 2"; Gold also sits in
# "Tower 2" (one Progressive Jump in logic) and Cherry in "Tower 3" (two). Clearing
# floor 2 additionally needs a Progressive Gun (rules.py).


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_LEVELS + 1):
        region = f"Tower {n}"
        table[f"Level {n}"] = LocationInfo(level_id(n, 0), region)
        for k in range(1, SHOP_ITEMS_PER_LEVEL + 1):
            table[f"Level {n} Shop - Item {k}"] = LocationInfo(level_id(n, k), region)
    table["Gift"] = LocationInfo(997, "Tower 2")
    table["Gold"] = LocationInfo(998, "Tower 2")
    table["Cherry"] = LocationInfo(999, "Tower 3")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# with no items only floor 1 is reachable -- its clear plus its three shop slots
sphere_1_locs: list[str] = (
    ["Level 1"] + [f"Level 1 Shop - Item {k}" for k in range(1, SHOP_ITEMS_PER_LEVEL + 1)]
)


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
