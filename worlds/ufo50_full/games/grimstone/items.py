from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Grimstone"

# Grimstone (o12_*) is a party JRPG. The AP items are quality-of-life only:
#   +20% XP Multiplier (useful) -- each copy adds 20% to a battle's XP (ADDITIVE:
#       20 copies -> x5.0).
#   200 Teeth (filler) -- each copy received adds 200 to o12__Game.teeth (cap 999999),
#       cumulative and persisted (ap_g12_teeth_granted in scr12_SaveGame).
XP_MULT = "+20% XP Multiplier"
FILLER = "200 Teeth"


item_table: dict[str, ItemInfo] = {
    XP_MULT: ItemInfo(511, IC.useful, 20),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # only the 20 XP-multiplier useful items enter the pool; the framework pads with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
