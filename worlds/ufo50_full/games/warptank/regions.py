from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# The whole game is one station hub carved into tiers by the `o16_Mecho` gate walls.
# Each tier is a region ("Hub", then "Gate 1/4/9/14/22" after the vanilla cumulative-
# clear thresholds); a sector's locations live in the tier its capsule pad sits behind,
# so the entry rules in rules.py gate them on the matching Capsule Gate item. "Gate 22"
# holds only the goal (Gold/Cherry); the final sector itself is in "Gate 4".
regions: list[str] = [
    "Menu",
    "Hub",
    "Gate 1",
    "Gate 4",
    "Gate 9",
    "Gate 14",
    "Gate 22",
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
