from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pingolf"
REGION = "The Course"

# The 18 holes in PLAY order -- the order Pingolf presents them (scr23_Constants
# `stageSequence` = [0,1,6,2,12,7,13,3,8,9,4,14,15,10,5,11,16,17] indexing o23_Mas
# holeName[]), which is what the in-game HUD numbers ("HOLE n" = g23_currStage + 1).
# Names from ext/ENGLISH/23_Text.json ("hole1".."hole18") title-cased, then permuted by
# stageSequence. One location per hole: "<hole name> - Par", offset = play position,
# sent the instant the ball sinks in par or fewer strokes.
HOLE_NAMES: tuple[str, ...] = (
    "A Warm Welcome",   # stageSequence[0]  = hole 1
    "Gustaf's Zig",     # stageSequence[1]  = hole 2
    "Fun and Games",    # stageSequence[2]  = hole 7
    "Big Air",          # stageSequence[3]  = hole 3
    "Internal Logic",   # stageSequence[4]  = hole 13
    "Little Cannon",    # stageSequence[5]  = hole 8
    "Lonely Acrobat",   # stageSequence[6]  = hole 14
    "Glacial Passage",  # stageSequence[7]  = hole 4
    "Juggle Pit",       # stageSequence[8]  = hole 9
    "Bouncing Back",    # stageSequence[9]  = hole 10
    "Chunk",            # stageSequence[10] = hole 5
    "Island Hopping",   # stageSequence[11] = hole 15
    "Chunkier",         # stageSequence[12] = hole 16
    "Bumper Paradise",  # stageSequence[13] = hole 11
    "Moray's Outlook",  # stageSequence[14] = hole 6
    "Chicken",          # stageSequence[15] = hole 12
    "Shrine of Venus",  # stageSequence[16] = hole 17
    "Journey's End",    # stageSequence[17] = hole 18
)
NUM_HOLES = len(HOLE_NAMES)

# id offset layout inside Pingolf's 1000-id block:
#     1..18  <hole name> - Par   (offset = play position, i.e. g23_currStage + 1)
#   200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry  (vanilla scrWin: hole-in-one / final score)


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(HOLE_NAMES, start=1):
        table[f"{name} - Par"] = LocationInfo(n, REGION)
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
    groups[f"{GAME_NAME} - Pars"] = {f"{GAME_NAME} - {name} - Par" for name in HOLE_NAMES}
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
