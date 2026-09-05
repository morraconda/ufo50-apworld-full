from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Party House"

regions: list[str] = [
    "Menu",
    "The Party House",
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    game_regions = build_regions(world, GAME_NAME, regions, create_locations)
    game_regions["Menu"].connect(game_regions["The Party House"])
    return game_regions
