from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Barbuta"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


location_table: dict[str, LocationInfo] = {
    "Green Skull - R1C1": LocationInfo(0, "Platforms above R4C4"),  # $100
    "Egg Shop - R2C6": LocationInfo(1, "Boss Area"),  # $100 each
    "Upper Shop Candy - R3C1": LocationInfo(2, "Platforms above R4C4"),  # costs $100
    "Upper Shop Umbrella - R3C1": LocationInfo(3, "Platforms above R4C4"),  # costs $50
    "Chest - R3C2": LocationInfo(4, "Platforms above R4C4"),  # Pin chest
    "Bat Altar - R4C1": LocationInfo(5, "Bat Altar"),  # bat noises
    "Coin - R4C4": LocationInfo(6, "Starting Area"),  # $50, breakable block
    "Little Guy Breaks a Wall - R4C7": LocationInfo(7, "R3C7 above Ladders"),  # costs $500
    "Chest - R5C3": LocationInfo(8, "Blood Sword Room"),  # omelette time
    "Chest - R5C5": LocationInfo(9, "Key Room"),  # I love climbing ladders
    "Chest - R5C8": LocationInfo(10, "R6C7 and Nearby"),  # $50
    "Green Skull - R6C2": LocationInfo(11, "Starting Area"),  # $100
    "Lower Shop Umbrella - R6C2": LocationInfo(12, "Starting Area"),  # costs $100
    "Lower Shop Trash - R6C2": LocationInfo(13, "Starting Area"),  # costs $50
    "Lower Shop Pin - R6C2": LocationInfo(14, "Starting Area"),  # costs $200
    "Chest - R6C3 Door": LocationInfo(15, "R7C3 and Nearby"),  # $100
    "Chest - R6C4": LocationInfo(16, "Starting Area"),  # Umbrella chest
    "Chest - R6C5": LocationInfo(17, "Starting Area"),  # $50
    "Chest - R6C6": LocationInfo(18, "R6C7 and Nearby"),  # $100
    "Chest - R7C2": LocationInfo(19, "Starting Area"),  # $50, requires pin
    "Chest - R7C5": LocationInfo(20, "Starting Area"),  # necklace chest
    "Chest - R8C5": LocationInfo(21, "Starting Area"),  # $100, be fast before the ledge breaks
    "Chest - R8C7": LocationInfo(22, "R7C7 and Nearby"),  # $50
    "Wand Trade - R8C7": LocationInfo(23, "Wand Trade Room"),  # probably should just have it give you the check

    "Garden": LocationInfo(997, "Menu"),
    "Gold": LocationInfo(998, "Boss Area"),
    "Cherry": LocationInfo(999, "Boss Area")
}


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    return game_location_groups(GAME_NAME, location_table)


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            continue

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, region)
        region.locations.append(loc)
