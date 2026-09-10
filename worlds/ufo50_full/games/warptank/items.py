from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# Warptank is a warp-tank metroidvania on one big station hub (rm16_Warptank) with 27
# sectors reached from it via capsule pads.
#
# Gates: vanilla carves the hub into tiers with `o16_Mecho` walls that slide open once
# a cumulative number of sectors has been cleared (trig 1 / 4 / 9 / 14 / 22), plus
# `o16_MechoE` shortcut walls. Following the Block Koala model, each Mecho wall is now
# a single named progression item (named for its trig threshold) -- you receive the
# gate to open it, no counting:
#   "1 Capsule Gate"   (511)  o16_Mecho trig 1   -- Hub -> tier 2
#   "4 Capsule Gate"   (512)  o16_Mecho trig 4
#   "9 Capsule Gate"   (513)  o16_Mecho trig 9   (also opens the o16_MechoE shortcut walls)
#   "14 Capsule Gate"  (514)  o16_Mecho trig 14
#   "22 Capsule Gate"  (515)  o16_Mecho trig 22  -- last tier -> Final Sector
#
# Coffee is unchanged: the hub "coffee bridge" to the Final Sector still grows one tile
# per received Coffee item; COFFEE_COUNT in the pool, the bridge needs 23 to be crossable.
COFFEE = "Coffee"
FILLER = "Encouragement"

GATES: dict[str, int] = {
    "1 Capsule Gate": 511,
    "4 Capsule Gate": 512,
    "9 Capsule Gate": 513,
    "14 Capsule Gate": 514,
    "22 Capsule Gate": 515,
}
COFFEE_COUNT = 30
COFFEE_FOR_FINAL = 23       # bridge is crossable -> also enough for Gold and Cherry


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(offset, IC.progression, 1) for name, offset in GATES.items()},
    COFFEE: ItemInfo(502, IC.progression_skip_balancing, COFFEE_COUNT),
    FILLER: ItemInfo(600, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Gates"] = {f"{GAME_NAME} - {name}" for name in GATES}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 5 gate items + 25 Coffee into the pool; the framework pads the rest with Encouragement
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
