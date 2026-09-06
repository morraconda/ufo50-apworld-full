from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 2"

# One region per world; every stage's checks (and the goal locations) live in the
# world they belong to, so the world-entry rules in rules.py gate them.
regions: list[str] = ["Menu", "A", "B", "C", "D"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
