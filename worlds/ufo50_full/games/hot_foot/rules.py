from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hot Foot"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every real check (the 6 tournament games) is sphere 1 -- the athlete items
    # just widen your draft, nothing in logic requires any of them
    regions["Menu"].connect(regions["The Tournament"])

    # Cherry needs 6 athletes total (the 3-4 you start with count).
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: state.has_group(f"{GAME_NAME} - Athletes", world.player, 6))
