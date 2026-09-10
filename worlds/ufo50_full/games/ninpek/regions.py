from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Ninpek"

# "The Run" holds the score-milestone locations + Gift; "Deep Run" (behind all 5
# Shuriken) holds Gold / Cherry. Score milestones above 5,000 get a per-location
# Shuriken-count rule in rules.py.
regions: list[str] = ["Menu", "The Run", "Deep Run"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
