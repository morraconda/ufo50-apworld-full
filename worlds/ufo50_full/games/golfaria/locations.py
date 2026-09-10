from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Golfaria"
REGION = "Golfaria"

# Simple implementation -- every location is a one-off pickup / milestone, all sphere 1.
ABILITIES = ("Block Buster", "Brakes", "Sand Roll", "Water Roll")
NUM_CLUBS = 20
TEE_PIECE_COLORS = ("Blue", "Red", "Yellow", "Purple")
NUM_GREEN_BALLS = 8
NUM_PARBOTS = 10

# id offset layout inside Golfaria's 1000-id block:
#     1..4    <ability>          (Block Buster / Brakes / Sand Roll / Water Roll)
#    11..30   Club <1..20>       (offset = 10 + n)
#    41..44   <colour> Tee Piece (Blue / Red / Yellow / Purple)
#    51..58   Green Ball <1..8>  (offset = 50 + n)
#    61..70   Parbot <1..10>     (offset = 60 + n)
#   200       Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for i, name in enumerate(ABILITIES, start=1):
        table[name] = LocationInfo(i, REGION)
    for n in range(1, NUM_CLUBS + 1):
        table[f"Club {n}"] = LocationInfo(10 + n, REGION)
    for i, color in enumerate(TEE_PIECE_COLORS, start=41):
        table[f"{color} Tee Piece"] = LocationInfo(i, REGION)
    for n in range(1, NUM_GREEN_BALLS + 1):
        table[f"Green Ball {n}"] = LocationInfo(50 + n, REGION)
    for n in range(1, NUM_PARBOTS + 1):
        table[f"Parbot {n}"] = LocationInfo(60 + n, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# every location is reachable from the start -- no item gating anywhere in this game
sphere_1_locs: list[str] = list(location_table.keys())


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Abilities"] = {f"{GAME_NAME} - {name}" for name in ABILITIES}
    groups[f"{GAME_NAME} - Clubs"] = {f"{GAME_NAME} - Club {n}" for n in range(1, NUM_CLUBS + 1)}
    groups[f"{GAME_NAME} - Tee Pieces"] = {f"{GAME_NAME} - {c} Tee Piece" for c in TEE_PIECE_COLORS}
    groups[f"{GAME_NAME} - Green Balls"] = {f"{GAME_NAME} - Green Ball {n}" for n in range(1, NUM_GREEN_BALLS + 1)}
    groups[f"{GAME_NAME} - Parbots"] = {f"{GAME_NAME} - Parbot {n}" for n in range(1, NUM_PARBOTS + 1)}
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
