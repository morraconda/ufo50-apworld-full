from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 3"

# a linear chain gated by the three weapon items (rules.py):
#   Menu -> Stage A (free) -> Armed (Forward Shot) -> Up Armed (Upward Beam)
#   -> Fully Armed (Sideways Beam, holds Gold/Cherry)
regions: list[str] = ["Menu", "Stage A", "Armed", "Up Armed", "Fully Armed"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
