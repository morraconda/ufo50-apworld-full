from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations, CAMPSITE, START, BOTTOM_LEFT, BORLG, LEFT, TOP, RIGHT, UNDERGROUND
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"

# the Campsite, the Wild Zone (rm37_Incremental2) split into areas by its blocks, and
# the Underground behind the dungeon doors; the connections are in rules.py
regions: list[str] = ["Menu", CAMPSITE, START, BOTTOM_LEFT, BORLG, LEFT, TOP, RIGHT, UNDERGROUND]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
