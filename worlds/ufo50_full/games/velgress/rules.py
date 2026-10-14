from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, PROGRESSIVE_JUMP, PROGRESSIVE_GUN
from .locations import SHOP_ITEMS_PER_LEVEL

if TYPE_CHECKING:
    from ... import UFO50World


_jump = f"{GAME_NAME} - {PROGRESSIVE_JUMP}"
_gun = f"{GAME_NAME} - {PROGRESSIVE_GUN}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # You start on a single jump; each Progressive Jump adds one mid-air jump. Floor N's
    # clear ("Level N") is reaching its shop, so floor N's shop slots share its tier.
    player = world.player
    regions["Menu"].connect(regions["Tower"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # tier 1: nothing required (sphere 1) -> Level 1 + its shop
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: 1 Progressive Jump + 1 Progressive Gun -> Level 2 + its shop, Gift, Gold
    def tier2(state: CollectionState) -> bool:
        return state.has(_jump, player, 1) and state.has(_gun, player, 1)

    # tier 3: 2 Progressive Jumps + 1 Progressive Gun -> Level 3 + its shop, Cherry
    def tier3(state: CollectionState) -> bool:
        return state.has(_jump, player, 2) and state.has(_gun, player, 1)

    for n, tier in ((1, tier1), (2, tier2), (3, tier3)):
        rule(f"Level {n}", tier)
        for k in range(1, SHOP_ITEMS_PER_LEVEL + 1):
            rule(f"Level {n} Shop - Item {k}", tier)

    # Gift needs a key on two separate floors (o15 GARDEN_GOAL = 2)
    rule("Gift", tier2)
    rule("Gold", tier2)
    rule("Cherry", tier3)
