from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# Map areas from the annotated map, as a region graph (edges + their gate items live in
# rules.py). "Start" is the small unlabelled area between Tree and Spawning Cave.
# Treetop / Entrance / Cave Side Cling carry no locations -- pure traversal nodes.
# "Ending" is behind the beat-the-game requirement and holds Gold / Cherry.
regions: list[str] = [
    "Menu",
    "Start",
    "Tree",
    "Treetop",
    "Spawning Cave",
    "Left Cave",
    "Entrance",
    "Upper Ruins",
    "Lower Ruins",
    "Sewers",
    "Deep Cave",
    "Arena",
    "Cave Side Cling",
    "Upper Castle",
    "Castle Roof",
    "Lower Castle",
    "Final Corridor",
    "Ending",
    "Cherry Ending",     # off "Ending"; needs 99 lives (Cherry only)
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
