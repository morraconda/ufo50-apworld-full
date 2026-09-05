from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"

# Waldorf's Journey is a short game; every check is reachable from the start, so there
# is just the required Menu region plus one region holding everything.
regions: list[str] = ["Menu", "Island"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
