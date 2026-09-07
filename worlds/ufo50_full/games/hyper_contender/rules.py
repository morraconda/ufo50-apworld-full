from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hyper Contender"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every location (the tournament rounds, Gift/Gold/Cherry) is sphere 1 -- the
    # fighter items only widen your roster, nothing in logic requires any of them
    regions["Menu"].connect(regions["The Tournament"])
