from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hot Foot"
REGION = "The Tournament"

# Hot Foot is a 6-game bean-bag tournament (o43_Game, `game` 1..6, game 6 = "FINAL
# GAME"). Each "Game n" check fires the moment you advance past it (o43_Game
# STATE_NEXT_GAME). "10 Points" fires the first time your team (pointScore[1]) reaches
# 10 in any match -- reachable in game 1 with no items.
GAME_NAMES: tuple[str, ...] = (
    "Game 1", "Game 2", "Game 3", "Game 4", "Game 5", "Final Game",
)

# id offset layout inside Hot Foot's 1000-id block:
#     1..6   <game name>   (won tournament game n)
#     10     10 Points      (pointScore[1] >= 10 in a match)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(GAME_NAMES, start=1):
        table[name] = LocationInfo(n, REGION)
    table["10 Points"] = LocationInfo(10, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items: Game 1, Game 2 and 10 Points (rules.py leaves them unruled)
sphere_1_locs: list[str] = ["Game 1", "Game 2", "10 Points"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Games"] = {f"{GAME_NAME} - {name}" for name in GAME_NAMES}
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
