from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Elfazar's Hat"

# a linear chain gated by the aim/dash items (rules.py):
#   Menu -> Stages 1-2 (shoot up only) -> Cardinal Zone (dash + 3 other cardinals)
#   -> Demon Tower (+ the 4 diagonals; holds Gold/Cherry)
# plus a "Ticket Gate" hung off Stages 1-2, holding the Gift (needs one Ticket).
regions: list[str] = ["Menu", "Stages 1-2", "Ticket Gate", "Cardinal Zone", "Demon Tower"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
