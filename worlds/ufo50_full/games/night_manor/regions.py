from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Night Manor"

regions: list[str] = [
    "Menu",  # the non-existent start menu, every game needs a region named "Game Name - Menu"
    "Starting Room",  # the initial room the game starts in
    "First Floor & Exterior",  # the floor accessible immediately after you exit the starting area
    "Second Floor",  # second floor accessible after you get powered flashlight
    "Shed",  # shed accessible after you get copper key
    "Master Bedroom",  # master bedroom accessible after you get gold key
    "Maze",  # maze accessible after you get 4 gems
    "Basement",  # accessible after you get the iron key
]


# this function is required, and its only argument can be the world class
# it must return the regions that it created
# it is recommended that you prepend each region name with the game it is from to avoid overlap
def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
