from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .locations import NUM_LEVELS, level_name

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol"

plus_3 = f"{GAME_NAME} - +3 Lives"
plus_5 = f"{GAME_NAME} - +5 Lives"
plus_10 = f"{GAME_NAME} - +10 Lives"

# Logic assumes each level costs LIVES_PER_LEVEL lives: to be expected to reach the Nth
# level you need START_LIVES + received >= LIVES_PER_LEVEL * N. So 1-A is free (you start
# with 20), 1-B needs +20, 2-A needs +60, ... 4-B (Gold) needs +180. Cherry costs
# CHERRY_LIVES for the 4-B beat instead of LIVES_PER_LEVEL, i.e.
# LIVES_PER_LEVEL * 9 + CHERRY_LIVES total.
START_LIVES: int = 20
LIVES_PER_LEVEL: int = 20
CHERRY_LIVES: int = 75


def total_life_value(state: CollectionState, player: int) -> int:
    return (START_LIVES
            + 3 * state.count(plus_3, player)
            + 5 * state.count(plus_5, player)
            + 10 * state.count(plus_10, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions[level_name(1)])
    for lvl in range(1, NUM_LEVELS):
        next_lvl = lvl + 1
        regions[level_name(lvl)].connect(
            regions[level_name(next_lvl)],
            rule=lambda state, n=next_lvl: total_life_value(state, player) >= LIVES_PER_LEVEL * n)

    # Gift clears at 2-C, Gold at the 4-B boss -- reaching the region (having the lives
    # for the linear chain) is enough. Cherry needs 75 lives for the 4-B beat instead of
    # the usual 20, i.e. LIVES_PER_LEVEL * 9 + CHERRY_LIVES total.
    cherry_total = LIVES_PER_LEVEL * (NUM_LEVELS - 1) + CHERRY_LIVES
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: total_life_value(state, player) >= cherry_total)
