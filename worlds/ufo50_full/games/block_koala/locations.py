from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Block Koala"

# Block Koala's story map is 50 levels split across 6 zones by the star gates
# (rules.py). id offset layout inside Block Koala's 1000-id block, via
# game_helpers.level_id (offset = level * 10 + slot):
#    7        Progressive Move Speed (filler item, see items.py)
#    10..500  Level <n>   (level_id(n, 0))
#   101       Koala Fact (filler item, see items.py)
#   997/998/999   Gift / Gold / Cherry

_ZONE_BY_LEVEL: dict[int, str] = {
    1: "Start",
    **{n: "Bottom Left" for n in range(2, 7)},
    **{n: "Mid Left" for n in range(7, 15)},
    **{n: "Bottom Right" for n in range(15, 28)},
    **{n: "Top" for n in range(28, 41)},
    **{n: "Mid Right" for n in range(41, 50)},
    50: "Boss",
}


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


location_table: dict[str, LocationInfo] = {
    **{f"Level {n}": LocationInfo(level_id(n, 0), zone) for n, zone in _ZONE_BY_LEVEL.items()},
    # Goal locations
    "Gift": LocationInfo(997, "Start"),
    "Gold": LocationInfo(998, "Boss"),
    "Cherry": LocationInfo(999, "Boss"),
}


sphere_1_locs: list[str] = ["Level 1", "Gift"]


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
