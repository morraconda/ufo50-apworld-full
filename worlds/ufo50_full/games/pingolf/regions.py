from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pingolf"

# holes 1-8's Par checks are reachable from the start ("The Course"); everything else
# -- holes 9-18's Par checks and Gift/Gold/Cherry -- needs the "Dunking" item
# ("Dunk Zone", gated in rules.py).
regions: list[str] = ["Menu", "The Course", "Dunk Zone"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
