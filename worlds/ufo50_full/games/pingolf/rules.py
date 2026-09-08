from typing import TYPE_CHECKING

from BaseClasses import Region

from .locations import DUNK_REGION

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pingolf"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # holes 1-8's Par checks are sphere 1; everything else needs the "Dunking" item.
    regions["Menu"].connect(regions["The Course"])
    regions["The Course"].connect(
        regions[DUNK_REGION],
        rule=lambda state: state.has(f"{GAME_NAME} - Dunking", world.player))
