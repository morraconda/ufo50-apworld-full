from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations, LEVEL_NAMES
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Fist Hell"

# One region per scare, chained Menu -> Southside -> Ride or Die -> ... -> Paradiso.
# Each step needs one more $25 than the last (rules.py).
regions: list[str] = ["Menu", *LEVEL_NAMES]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
