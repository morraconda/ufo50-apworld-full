from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Combatants"

# All 13 missions (12 + hidden "Nemuru's Way") start unlocked and live in "The
# Campaign" (each one carries its own ability requirement as a per-location rule). The
# three goal locations sit in gated regions: Spider Hunt (Gift), Final Assault
# (Gold = beat "This Is It"), Total Victory (Cherry = clear all 12).
regions: list[str] = ["Menu", "The Campaign", "Spider Hunt", "Final Assault", "Total Victory"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
