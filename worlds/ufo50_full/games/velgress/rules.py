from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, PROGRESSIVE_JUMP, PROGRESSIVE_GUN

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Single jump to start; each Progressive Jump adds one mid-air jump. One is enough to
    # climb to floor 2 (and the Gold top), two to reach floor 3 (and the Cherry top).
    player = world.player
    jump = f"{GAME_NAME} - {PROGRESSIVE_JUMP}"
    gun = f"{GAME_NAME} - {PROGRESSIVE_GUN}"

    regions["Menu"].connect(regions["Tower 1"])
    regions["Tower 1"].connect(regions["Tower 2"], rule=lambda state: state.has(jump, player, 1))
    regions["Tower 2"].connect(regions["Tower 3"], rule=lambda state: state.has(jump, player, 2))

    # A Progressive Gun is needed to clear floor 2 and for the Gift goal. Gold/Cherry are
    # gated only by their region -- Gold in "Tower 2" (one Progressive Jump), Cherry in
    # "Tower 3" (two).
    set_rule(world.get_location(f"{GAME_NAME} - Level 2"),
             lambda state: state.has(gun, player, 1))
    set_rule(world.get_location(f"{GAME_NAME} - Gift"),
             lambda state: state.has(gun, player, 1))
