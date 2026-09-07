from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rock On! Island"

# Menu -> The Island (free) -> Fireside (Progressive Fire >= 1) -> Spearpoint
# (Progressive Spear >= 2) -> Mastery (every progression item). See rules.py.
regions: list[str] = ["Menu", "The Island", "Fireside", "Spearpoint", "Mastery"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
