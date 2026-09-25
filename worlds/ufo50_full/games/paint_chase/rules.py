from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .items import TURN_LEFT
from .locations import UNIT, NUM_LEVEL, FREE_LEVELS

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Paint Chase"

_turn_left = f"{GAME_NAME} - {TURN_LEFT}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["The Circuit"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # tier 1: nothing required (sphere 1) -> Levels 1-4
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: Turn Left -> Levels 5-26, Gift (clear 12), Gold, Cherry
    def tier2(state: CollectionState) -> bool:
        return state.has(_turn_left, player)

    for n in range(1, NUM_LEVEL + 1):
        rule(f"{UNIT} {n}", tier1 if n <= FREE_LEVELS else tier2)

    rule("Gift", tier2)
    rule("Gold", tier2)
    rule("Cherry", tier2)
