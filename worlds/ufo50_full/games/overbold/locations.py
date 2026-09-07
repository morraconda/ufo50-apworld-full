from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Overbold"
REGION = "The Arena"

# Overbold's wave prize (o30_Game.prize) runs $100..$1600 in $100 steps
# (PRIZE_INCREASE 100, MAX_PRIZE 1600). Beating a wave worth >= $n*100 awards the
# "Beat a $<n*100> Wave" check -- cumulative, so a big wave awards all lower ones.
PRIZE_STEP = 100
NUM_STEPS = 16

# id offset layout inside Overbold's 1000-id block:
#     1..16   Beat a $<n*100> Wave   (offset = n; cleared a wave with prize >= n*100)
#   200       Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _wave_name(n: int) -> str:
    return f"Beat a ${n * PRIZE_STEP:,} Wave"


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_STEPS + 1):
        table[_wave_name(n)] = LocationInfo(n, REGION)
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
    groups[f"{GAME_NAME} - Waves"] = {f"{GAME_NAME} - {_wave_name(n)}" for n in range(1, NUM_STEPS + 1)}
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
