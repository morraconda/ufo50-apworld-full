from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Barbuta"

regions: list[str] = [
    "Menu",  # the non-existent start menu, every game needs a region named "Game Name - Menu"
    "Starting Area",
    "Key Room",  # the room with the key, where you can access the key
    "Platforms above R4C4",  # the "first" moving platforms
    "Blood Sword Room",  # E3, probably unnecessary unless we randomize switches
    "R7C3 and Nearby",  # idk what to call this, it's up the poison ladder and right of some balls
    "R6C7 and Nearby",  # lots of purple blocks here
    "Bat Altar",  # the altar at D1 and the room next to it at D2
    "Above Entrance",  # in the sign
    "Wand Trade Room",  # where you trade your sword for a wand
    "R7C7 and Nearby",  # down where the shield guys are, need pin to get to wand
    "Mimic Room",  # H1, where the mimic is
    "Boss Area",  # B6, point of no return unless you paid $500 to break a wall
    "R3C7 above Ladders",  # C7, up by the little guy who breaks the wall
]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
