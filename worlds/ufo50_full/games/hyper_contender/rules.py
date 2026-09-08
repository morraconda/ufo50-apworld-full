from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hyper Contender"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every round check is sphere 1 -- the fighter items only widen your roster
    regions["Menu"].connect(regions["The Tournament"])

    # Gold needs a fighter sent from the multiworld (you start with Yogo, so >= 2).
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: state.has_group(f"{GAME_NAME} - Fighters", world.player, 2))
    # Cherry needs 5 fighters total (Yogo, the one you start with, counts).
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: state.has_group(f"{GAME_NAME} - Fighters", world.player, 5))
