from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Grimstone"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # every location (level milestones, Gift/Gold/Cherry) is sphere 1 -- the +20% XP
    # Multiplier is useful, not required
    regions["Menu"].connect(regions["The Frontier"])
