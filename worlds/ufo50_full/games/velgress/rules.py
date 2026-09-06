from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Velgress"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # Every check (level clears, shop purchases, Garden/Gold/Cherry) is sphere 1 -- no
    # item gating. Shop prices persist across runs in-game, but AP places the upgrade
    # elsewhere, so buying is never actually blocked here.
    regions["Menu"].connect(regions["Tower"])
