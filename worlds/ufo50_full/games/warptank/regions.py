from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# The whole game is one station hub carved into tiers by the `o16_Mecho` gate walls.
# Each tier is a region; a sector's locations (and the goal locations) live in the tier
# its capsule pad sits behind, so the entry rules in rules.py gate them on the matching
# "Mecho Gate <n>" item (Block Koala model). Region names keep the vanilla
# cumulative-clear thresholds (1/4/9/14) as tier labels.
regions: list[str] = [
    "Menu",
    "Station Hub",
    "Hub - Gate 1",
    "Hub - Gate 4",
    "Hub - Gate 9",
    "Hub - Gate 14",
    "Final Sector",
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
