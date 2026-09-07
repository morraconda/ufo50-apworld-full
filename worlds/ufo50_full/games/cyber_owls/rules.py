from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Cyber Owls"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every location (bosses, Gift/Gold/Cherry) is sphere 1 -- no item gating
    regions["Menu"].connect(regions["The Ops"])
