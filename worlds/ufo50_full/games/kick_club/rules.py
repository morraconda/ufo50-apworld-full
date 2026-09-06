from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region

from .locations import (GAME_NAME, BLOCK_SIZE, NUM_LEVELS, block_of, block_start_level,
                        level_name)

if TYPE_CHECKING:
    from ... import UFO50World


REAL_SECOND = f"{GAME_NAME} - +1 Real Second"
EXTRA_LIFE = f"{GAME_NAME} - Extra Life"

# The run is continuous (no level select) -- these are logic assumptions, not a hard
# in-game lock: to be expected to survive block K (sub-levels 5*(K-1)+1 .. 5*K) you
# need SECONDS_PER_BLOCK more real seconds on the timer and LIVES_PER_BLOCK more lives
# than the block before. Block 1 is free.
SECONDS_PER_BLOCK = 5
LIVES_PER_BLOCK = 1


def _seconds(state: CollectionState, player: int) -> int:
    return state.count(REAL_SECOND, player)


def _lives(state: CollectionState, player: int) -> int:
    return state.count(EXTRA_LIFE, player)


def _can_play_block(state: CollectionState, player: int, block: int) -> bool:
    return (_seconds(state, player) >= SECONDS_PER_BLOCK * (block - 1)
            and _lives(state, player) >= LIVES_PER_BLOCK * (block - 1))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # continuous chain: Menu -> 1-1 -> 1-2 -> ... -> 4-10. Crossing into a new block of
    # five sub-levels carries that block's seconds/lives requirement; everything else
    # (including the score checks parked in each block's opening region) is free.
    for n in range(1, NUM_LEVELS + 1):
        source = regions["Menu"] if n == 1 else regions[level_name(n - 1)]
        block = block_of(n)
        if n == block_start_level(block) and block >= 2:
            source.connect(
                regions[level_name(n)],
                rule=lambda state, b=block: _can_play_block(state, player, b))
        else:
            source.connect(regions[level_name(n)])
