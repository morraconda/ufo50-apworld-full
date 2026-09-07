from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hot Foot"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every location (the 6 tournament games, Gift/Gold/Cherry) is sphere 1 -- the
    # athlete items just widen your draft, nothing in logic requires any of them
    regions["Menu"].connect(regions["The Tournament"])
