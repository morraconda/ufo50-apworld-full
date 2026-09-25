from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .items import BLESSINGS, REXADON, TRILOCK
from .locations import location_table, sphere_1_locs

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Avianos"

_unlocks = tuple(f"{GAME_NAME} - {name}" for name in (BLESSINGS, REXADON, TRILOCK))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["The War"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # tier 1: nothing required (sphere 1) -> Hatchling, 9 Bones, 9 Workers, 50 Seeds, 99 Seeds
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: Blessings -> Gift (max out blessings from one ancestor)
    def tier2(state: CollectionState) -> bool:
        return state.has(f"{GAME_NAME} - {BLESSINGS}", player)

    # tier 3: Blessings, Rexadon and Trilock -> every other scenario, Gold, Cherry
    def tier3(state: CollectionState) -> bool:
        return state.has_all(_unlocks, player)

    for loc_name in location_table:
        if loc_name in sphere_1_locs:
            rule(loc_name, tier1)
        elif loc_name == "Gift":
            rule(loc_name, tier2)
        else:
            rule(loc_name, tier3)
