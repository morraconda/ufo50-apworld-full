from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 2"

# The seven named stages, in play order, each tagged with its world (A..D). Crepelia
# (world D, the finale) is the only stage with a third milestone.
#   (stage name, world region, has a "III" milestone)
LEVELS: list[tuple[str, str, bool]] = [
    ("Burrows",         "A", False),
    ("Moire Woods",     "B", False),
    ("Rink",            "B", False),
    ("Vaalpolis",       "C", False),
    ("Gut",             "C", False),
    ("Temple Grounds",  "C", False),
    ("Crepelia",        "D", True),
]

# level_id(level, slot) = level * 10 + slot -- slot layout inside a stage's block, per
# unit (I / II, plus III for Crepelia):
#    0/1/2   <stage> <unit>              milestone
#    3/4     <stage> <unit> Cave Item    (I and II only)
#    5/6/7   <stage> <unit> Shop Item    (every unit except Burrows I -- Burrows I has
#                                         no shop)
#   (roman label, milestone slot, cave-item slot or None, shop-item slot)
_UNITS: list[tuple[str, int, "int | None", int]] = [
    ("I",   0, 3,    5),
    ("II",  1, 4,    6),
    ("III", 2, None, 7),   # Crepelia only
]


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for level, (name, region, has_iii) in enumerate(LEVELS, start=1):
        for roman, milestone_slot, cave_slot, shop_slot in _UNITS:
            if roman == "III" and not has_iii:
                continue
            table[f"{name} {roman}"] = LocationInfo(level_id(level, milestone_slot), region)
            if cave_slot is not None:
                table[f"{name} {roman} Cave Item"] = LocationInfo(level_id(level, cave_slot), region)
            if not (name == "Burrows" and roman == "I"):
                table[f"{name} {roman} Shop Item"] = LocationInfo(level_id(level, shop_slot), region)
    # goal locations last so create_locations' Cherry/Gold handling can break out.
    # Garden only needs world B; Gold/Cherry are the finale (world D).
    table["Garden"] = LocationInfo(997, "B")
    table["Gold"] = LocationInfo(998, "D")
    table["Cherry"] = LocationInfo(999, "D")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# World A (Burrows) is reachable with nothing.
sphere_1_locs: list[str] = [name for name, info in location_table.items() if info.region_name == "A"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    for world in ("A", "B", "C", "D"):
        groups[f"{GAME_NAME} - World {world}"] = {f"{GAME_NAME} - {name}"
                                                 for name, info in location_table.items()
                                                 if info.region_name == world}
    groups[f"{GAME_NAME} - Cave Items"] = {f"{GAME_NAME} - {name}"
                                          for name in location_table if name.endswith("Cave Item")}
    groups[f"{GAME_NAME} - Shop Items"] = {f"{GAME_NAME} - {name}"
                                          for name in location_table if name.endswith("Shop Item")}
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
