from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rakshasa"

# One region per stage. Menu -> Stage 1 is free; Stage 1 -> Stage 2 needs any 2 of the
# 3 weapon items, Stage 2 -> Stage 3 needs all 3 (rules.py).
regions: list[str] = ["Menu", "Stage 1", "Stage 2", "Stage 3"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
