from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import (skip_cherry_location_if_disabled, is_completion_event_location,
                               place_completion_event)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Party House"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str = "The Party House"


location_table: dict[str, LocationInfo] = {
    "Alien Invitation": LocationInfo(0),
    "High or Low": LocationInfo(1),
    "Best Wishes": LocationInfo(2),
    "Money Management": LocationInfo(3),
    "A Magical Night": LocationInfo(4),

    "Garden": LocationInfo(997),
    "Gold": LocationInfo(998),
    "Cherry": LocationInfo(999)
}


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    return game_location_groups(GAME_NAME, location_table)


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if skip_cherry_location_if_disabled(world, GAME_NAME, loc_name):
            break
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            break

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, region)
        region.locations.append(loc)
