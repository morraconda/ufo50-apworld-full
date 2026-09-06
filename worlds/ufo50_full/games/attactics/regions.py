from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import GAME_NAME, LEVEL_NAMES, RANKS, create_locations, rank_region
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


# Two independent progressions off the menu: the linear campaign (24 named levels) and
# the ranked ladder (Rank 10..100).
regions: list[str] = ["Menu"] + list(LEVEL_NAMES) + [rank_region(r) for r in RANKS]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
