from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Bug Hunter"

# Warmup (job 1's 2..6 kills) is free; Job 1 (the rest of job 1, Gift) needs the hand
# unlocked; The Hunt (every later job, Gold, Cherry) also needs 2 of the 3 shop slots;
# Energy's checks each need a high enough energy cap -- see rules.py
regions: list[str] = ["Menu", "Warmup", "Job 1", "The Hunt", "Energy"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
