from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region

from .items import GAME_NAME, WEAPONS

if TYPE_CHECKING:
    from ... import UFO50World


_weapons = tuple(f"{GAME_NAME} - {name}" for name in WEAPONS)


def _weapon_count(state: CollectionState, player: int) -> int:
    return sum(1 for w in _weapons if state.has(w, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["Stage 1"])
    # Stage 2 needs any 2 weapon items, Stage 3 needs all 3 (also the Gold/Cherry goal).
    regions["Stage 1"].connect(regions["Stage 2"],
                               rule=lambda state: _weapon_count(state, player) >= 2)
    regions["Stage 2"].connect(regions["Stage 3"],
                               rule=lambda state: _weapon_count(state, player) >= 3)
