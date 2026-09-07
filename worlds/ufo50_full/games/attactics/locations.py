from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Attactics"

# The 24 campaign levels in play order, by their in-game names (ext/ENGLISH/2_Text.json
# keys level_101..level_124). Checks/regions use these names directly.
LEVEL_NAMES: list[str] = [
    "FIRST ENCOUNTER", "ARROW DEFENSE", "ATTRITION", "UNDER FIRE",
    "HERE THEY COME", "ESCALATION", "PROTECT YOURSELF", "WHAT'S THE POINT?",
    "PORCUPINE STYLE", "SO IT GOES", "KNIVES OUT", "POKE AND DAGGER",
    "STEM THE TIDE", "READY OR NOT", "STAND BACK", "BLAST DAMAGE",
    "GUERILLA WARFARE", "RALLY THE TROOPS", "TRAFFIC JAM", "ACTS OF HEROISM",
    "BACK TO BASICS", "BARRELING AHEAD", "WAR IS BAD", "THE FINAL BATTLE",
]
NUM_LEVELS = len(LEVEL_NAMES)

# Ranked ladder milestones: rank climbs in steps of RANK_STEP and a check fires the
# first time each milestone is reached. The ladder is independent of the campaign.
RANK_STEP = 10
FIRST_RANK = 10
LAST_RANK = 100
RANKS: list[int] = list(range(FIRST_RANK, LAST_RANK + 1, RANK_STEP))

# Vanilla goal wiring (scr02_SaveGame / 2_Text.json): Garden = beat the first 12
# campaign levels, Gold = beat all 24, Cherry = beat the campaign AND reach rank 100.
GARDEN_LEVEL = 12


def level_name(n: int) -> str:
    """In-game name for a 1-indexed play-order campaign level."""
    return LEVEL_NAMES[n - 1]


def rank_region(r: int) -> str:
    return f"Rank {r}"


GARDEN_REGION = level_name(GARDEN_LEVEL)
GOLD_REGION = level_name(NUM_LEVELS)
CHERRY_REGION = rank_region(LAST_RANK)


# id offset layout inside Attactics' 1000-id block:
#   1..3          items (see items.py)
#   10, 20, ...   <level name>   (campaign level clear, via game_helpers.level_id(n, 0))
#   301..310      Rank <r>       (ranked ladder milestone, 300 + r // RANK_STEP)
#   997/998/999   Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_LEVELS + 1):
        table[level_name(n)] = LocationInfo(level_id(n, 0), level_name(n))
    for r in RANKS:
        table[rank_region(r)] = LocationInfo(300 + r // RANK_STEP, rank_region(r))
    # goal locations last so create_locations' Cherry/Gold handling can break out safely
    table["Garden"] = LocationInfo(997, GARDEN_REGION)
    table["Gold"] = LocationInfo(998, GOLD_REGION)
    table["Cherry"] = LocationInfo(999, CHERRY_REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# The ranked ladder is open from the start; milestones below the promotion wall need
# no items.
sphere_1_locs: list[str] = [rank_region(r) for r in RANKS if r < 50]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Level Clears"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Ranks"] = {f"{GAME_NAME} - {rank_region(r)}" for r in RANKS}
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
