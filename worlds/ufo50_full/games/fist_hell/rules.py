from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, CASH, WATCH, COINS
from .locations import LEVEL_NAMES

if TYPE_CHECKING:
    from ... import UFO50World

DOLLARS_PER_SCARE = 20


def _money(state, player: int) -> int:
    return (5 * state.count(f"{GAME_NAME} - {CASH}", player)
            + 10 * state.count(f"{GAME_NAME} - {WATCH}", player)
            + state.count(f"{GAME_NAME} - {COINS}", player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Southside is free; each later scare needs $20 more than the one before it, on the
    # dollar total of every money item received (bills $5 / watches $10 / pad $1).
    player = world.player

    regions["Menu"].connect(regions[LEVEL_NAMES[0]])
    for i in range(1, len(LEVEL_NAMES)):
        regions[LEVEL_NAMES[i - 1]].connect(
            regions[LEVEL_NAMES[i]],
            rule=lambda state, need=DOLLARS_PER_SCARE * i: _money(state, player) >= need,
        )
