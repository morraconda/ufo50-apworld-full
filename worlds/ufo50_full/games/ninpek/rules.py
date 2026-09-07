from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Ninpek"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every location (score milestones, Gift/Gold/Cherry) is sphere 1 -- no item gating
    regions["Menu"].connect(regions["The Run"])
