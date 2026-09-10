from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Devilition"

# "The Village" holds the round + villager + Gift locations (each round/villager check
# gets its own piece-count rule in rules.py). "Endgame" holds Gold / Cherry behind
# round 10's full requirements.
regions: list[str] = ["Menu", "The Village", "Endgame"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
