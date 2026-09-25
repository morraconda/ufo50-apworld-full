from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, CAMOUFLAGE

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # Sky Temple / Gold are sphere 1
    regions["Menu"].connect(regions["Sky Temple"])
    # every other level, collectible, Gift and Cherry needs Camouflage
    regions["Menu"].connect(regions["The Jungle"],
                            rule=lambda state: state.has(f"{GAME_NAME} - {CAMOUFLAGE}", player))
