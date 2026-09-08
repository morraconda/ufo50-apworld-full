from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every real check (chests, signs) is sphere 1 -- no item gating.
    regions["Menu"].connect(regions["Island"])

    # Cherry needs any 2 of the six toolkit items.
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: state.has_group(f"{GAME_NAME} - Starting Items", world.player, 2))
