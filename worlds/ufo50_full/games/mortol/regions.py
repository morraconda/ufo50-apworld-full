from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import LEVEL_NAMES, create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol"

# Linear progression: Menu -> 1-A -> 1-B -> ... -> 4-B, one region per level. Each
# level's clear location and its life pickups live in that level's region.
regions: list[str] = ["Menu"] + list(LEVEL_NAMES)


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
