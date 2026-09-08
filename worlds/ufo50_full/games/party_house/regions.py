from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import GAME_NAME, SCENARIOS, GLOBAL_REGION, create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


# One region per scenario plus the global metric region ("The Party"), all reachable
# straight from the menu.
regions: list[str] = ["Menu", GLOBAL_REGION] + list(SCENARIOS)


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
