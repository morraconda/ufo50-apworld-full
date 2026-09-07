from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rail Heist"

# Rail Heist has no in-game progression gating: every level can be selected from the
# main menu at the start of the game. The only region besides the required Menu is the
# one that holds all of the level locations.
regions: list[str] = [
    "Menu",
    "Levels",
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
