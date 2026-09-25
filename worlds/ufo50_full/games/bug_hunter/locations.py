from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Bug Hunter"
UNIT = "Job"
NUM_JOB = 6   # the job streak (o20_Game.job); GOLD_GOAL 3, CHERRY_GOAL 6
KILL_MILESTONES = (10, 20)   # per-job kill counts (points[]; 30 = POINT_GOAL beats the job)
JOB_1_KILL_MILESTONES = (2, 4, 6, 8)   # extra job-1-only kill counts
WARMUP_KILLS = 6            # job-1 kill counts up to this are free
ENERGY_CHECKS = 12          # <X> Energy, X = 1..ENERGY_CHECKS (held energy, treasure[])
STARTING_MAX_ENERGY = 5     # energy cap before any +1 Max Energy (mod: TREASURE_MAX)

# regions (see rules.py): the first few job-1 kills are free, the rest of job 1 needs the
# hand unlocked, anything past job 1 also needs 2 of the 3 shop slots; the energy checks
# only depend on the energy cap
WARMUP_REGION = "Warmup"
JOB_1_REGION = "Job 1"
REGION = "The Hunt"
ENERGY_REGION = "Energy"

# id offset layout inside Bug Hunter's 1000-id block, via game_helpers.level_id
# (offset = level * 10 + slot):
#    10..60   Job <n>   (beat job n of a hunting streak; level_id(n, 0))
#    11..62   Job <n> - <k> Kills   (k kills during job n; level_id(n, 1 + i),
#             i = 0 for 10 / 1 for 20)
#    13..16   Job 1 - <k> Kills     (k = 2 / 4 / 6 / 8; level_id(1, 3 + i))
#   101..112  <X> Energy            (hold X energy; 100 + X)
#     2..9    items: Module 6, Module 7, Shop Slot 1..3, +1 Energy Cube Drop,
#             +1 Max Energy, +1 Starting Energy
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _kill_region(job: int, kills: int) -> str:
    if job > 1:
        return REGION
    return WARMUP_REGION if kills <= WARMUP_KILLS else JOB_1_REGION


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_JOB + 1):
        table[f"{UNIT} {n}"] = LocationInfo(level_id(n, 0), JOB_1_REGION if n == 1 else REGION)
        for i, kills in enumerate(KILL_MILESTONES):
            table[f"{UNIT} {n} - {kills} Kills"] = LocationInfo(level_id(n, 1 + i), _kill_region(n, kills))
    for i, kills in enumerate(JOB_1_KILL_MILESTONES):
        table[f"{UNIT} 1 - {kills} Kills"] = LocationInfo(level_id(1, 3 + i), _kill_region(1, kills))
    for x in range(1, ENERGY_CHECKS + 1):
        table[f"{x} Energy"] = LocationInfo(100 + x, ENERGY_REGION)
    table["Gift"] = LocationInfo(997, JOB_1_REGION)   # job 1
    table["Gold"] = LocationInfo(998, REGION)         # job 3
    table["Cherry"] = LocationInfo(999, REGION)       # job 6
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

sphere_1_locs: list[str] = (
    [name for name, info in location_table.items() if info.region_name == WARMUP_REGION]
    + [f"{x} Energy" for x in range(1, STARTING_MAX_ENERGY + 1)]
)


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {UNIT} {n}" for n in range(1, NUM_JOB + 1)}
    groups[f"{GAME_NAME} - Kills"] = {f"{GAME_NAME} - {name}" for name in location_table
                                      if name.endswith(" Kills")}
    groups[f"{GAME_NAME} - Energy"] = {f"{GAME_NAME} - {x} Energy" for x in range(1, ENERGY_CHECKS + 1)}
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
