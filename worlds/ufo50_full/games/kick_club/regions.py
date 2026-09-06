from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import GAME_NAME, NUM_LEVELS, create_locations, level_name
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


# One region per sub-level, played as a single continuous chain off the menu.
regions: list[str] = ["Menu"] + [level_name(n) for n in range(1, NUM_LEVELS + 1)]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
