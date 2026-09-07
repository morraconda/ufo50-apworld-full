from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Camouflage"

# every location is reachable from the start, so there is just the required Menu region
# plus one region holding all the level / collectible locations
regions: list[str] = ["Menu", "The Jungle"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
