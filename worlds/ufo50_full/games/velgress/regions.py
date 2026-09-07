from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Velgress"

# One region per floor of the climb. Menu -> Tower 1 is free; Tower 1 -> Tower 2 needs
# one Progressive Jump and Tower 2 -> Tower 3 needs two (rules.py).
regions: list[str] = ["Menu", "Tower 1", "Tower 2", "Tower 3"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
