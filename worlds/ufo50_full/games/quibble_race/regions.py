from typing import TYPE_CHECKING

from BaseClasses import Region

from ...game_helpers import build_regions
from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Quibble Race"

# Racing holds the Won Race checks + Gold; Bred Champion (Gift) is gated on the Breeder
# item; Cash Empire (Cherry) on owning every shop / thug item.
regions: list[str] = ["Menu", "Racing", "Bred Champion", "Cash Empire"]


def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    return build_regions(world, GAME_NAME, regions, create_locations, create_rules)
