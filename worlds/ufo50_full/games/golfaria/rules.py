from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Golfaria"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # simple implementation: every location (abilities, clubs, tee pieces, green balls,
    # parbots, Gift/Gold/Cherry) is sphere 1 -- no item gating
    regions["Menu"].connect(regions["Golfaria"])
