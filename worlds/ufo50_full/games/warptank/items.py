from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# Warptank is a warp-tank metroidvania on one big station "hub" (rm16_Warptank) with
# 27 sectors reached from it via capsule pads. Vanilla gates the hub with `o16_Mecho`
# walls that open once a cumulative number of sectors has been cleared (1 / 4 / 9 / 14
# / 22), and the coffee "bridge" across the hub grows one tile per coffee collected.
#
# For AP those two counters become item counts instead of in-game progress:
#   - Capsule : opens the hub Mecho gates. 25 in the pool; the final gate wants 22.
#   - Coffee  : extends the hub bridge to the Final Sector. 25 in the pool; the bridge
#               needs 23 to be crossable.
CAPSULE = "Capsule"
COFFEE = "Coffee"
FILLER = "Encouragement"

# how many of each gating item exists, and the thresholds the logic checks
CAPSULE_COUNT = 25
COFFEE_COUNT = 25
COFFEE_FOR_FINAL = 23       # bridge is crossable -> also enough for Gold and Cherry


item_table: dict[str, ItemInfo] = {
    CAPSULE: ItemInfo(501, IC.progression, CAPSULE_COUNT),
    COFFEE: ItemInfo(502, IC.progression_skip_balancing, COFFEE_COUNT),
    FILLER: ItemInfo(600, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 25 Capsule + 25 Coffee into the pool; the framework pads the rest with Encouragement
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
