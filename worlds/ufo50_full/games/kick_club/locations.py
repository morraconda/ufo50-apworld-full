from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import (skip_cherry_location_if_disabled, is_completion_event_location,
                               place_completion_event)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Kick Club"

WORLDS = 4
SUBLEVELS = 10
NUM_LEVELS = WORLDS * SUBLEVELS          # 40 sub-levels, played "1-1" .. "4-10"

# The campaign runs in blocks of 5 sub-levels; each block also holds 20k points, so
# finishing the game (8 blocks) is worth ~160k.
BLOCK_SIZE = 5
NUM_BLOCKS = NUM_LEVELS // BLOCK_SIZE    # 8

# Score checks: every 10k breakpoint up to the 150k Cherry goal.
SCORE_STEP = 10_000
SCORE_MAX = 150_000
SCORES: list[int] = list(range(SCORE_STEP, SCORE_MAX + 1, SCORE_STEP))   # 15 of them

# Each threshold is gated by the block that `points + SCORE_SHIFT` would sit in, so
# only the 10k check is sphere 1 (the pairs then run 20k/30k -> block 2, 40k/50k ->
# block 3, ... 140k/150k -> block 8).
SCORE_SHIFT = 10_000


def level_name(n: int) -> str:
    """"<world>-<sublevel>" for 1-indexed play-order sub-level n (1 -> "1-1")."""
    return f"{(n - 1) // SUBLEVELS + 1}-{(n - 1) % SUBLEVELS + 1}"


def score_name(points: int) -> str:
    return f"{points // 1000}k Points"


def block_of(n: int) -> int:
    """1-indexed block (of 5 sub-levels) that play-order sub-level n belongs to."""
    return (n - 1) // BLOCK_SIZE + 1


def block_start_level(block: int) -> int:
    """Play-order sub-level number that opens the given 1-indexed block."""
    return BLOCK_SIZE * (block - 1) + 1


def block_for_score(points: int) -> int:
    """The block you must be able to play for the `points` check (20k per block,
    shifted up by SCORE_SHIFT so only 10k is sphere 1)."""
    return -(-(points + SCORE_SHIFT) // (BLOCK_SIZE * 4000))   # ceil((points + 10k) / 20000)


# Kick Club has no in-game boss/win text for Gold or Garden separately from finishing
# world 4, and the Runner boss (Garden) is room-placed so its world isn't visible in
# the decompile -- park Garden on the final region too (safe: it's only ever a check).
GARDEN_REGION = level_name(NUM_LEVELS)
GOLD_REGION = level_name(NUM_LEVELS)
CHERRY_REGION = level_name(NUM_LEVELS)


# id offset layout inside Kick Club's 1000-id block:
#   1..2          items (see items.py)
#   10, 20, ...   <world>-<sublevel>   (sub-level clear, via game_helpers.level_id(n, 0))
#   501..515      <n>k Points          (500 + points // 10000)
#   997/998/999   Garden / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_LEVELS + 1):
        table[level_name(n)] = LocationInfo(level_id(n, 0), level_name(n))
    for points in SCORES:
        region = level_name(block_start_level(block_for_score(points)))
        table[score_name(points)] = LocationInfo(500 + points // SCORE_STEP, region)
    # goal locations last so create_locations' Cherry/Gold handling can break out safely
    table["Garden"] = LocationInfo(997, GARDEN_REGION)
    table["Gold"] = LocationInfo(998, GOLD_REGION)
    table["Cherry"] = LocationInfo(999, CHERRY_REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# Block 1 (the first five sub-levels) and the 10k score check need no items.
sphere_1_locs: list[str] = ([level_name(n) for n in range(1, BLOCK_SIZE + 1)]
                            + [score_name(SCORE_STEP)])


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Level Clears"] = {f"{GAME_NAME} - {level_name(n)}"
                                             for n in range(1, NUM_LEVELS + 1)}
    groups[f"{GAME_NAME} - Score"] = {f"{GAME_NAME} - {score_name(p)}" for p in SCORES}
    return groups


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
