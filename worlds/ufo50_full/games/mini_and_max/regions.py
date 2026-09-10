from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations, SHRINK_REGIONS
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mini & Max"

# "Hub" is the Regular room + the singly-shrunk Small world (reachable with nothing) --
# it holds the sphere-1 checks and Gift. The 40 shrink regions are the cells of the 8x5
# Small grid -- each reached from the Hub by owning that region's gate item (and at
# least one Progressive Magic Potion). "Ending" holds Gold behind the full kit;
# "Cherry Ending" hangs off it and additionally needs the Clock reachable.
regions: list[str] = ["Menu", "Hub", *SHRINK_REGIONS, "Ending", "Cherry Ending"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
