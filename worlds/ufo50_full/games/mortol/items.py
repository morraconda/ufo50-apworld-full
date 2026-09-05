from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)
from .locations import PICKUPS

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol"

PLUS_3 = "+3 Lives"
PLUS_5 = "+5 Lives"
PLUS_10 = "+10 Lives"
FILLER = "+1 Life"

# one life item per pickup, quantities matching the in-game pickups (31 x +3, 20 x +5,
# 9 x +10). Life items are progression -- they're the only way to unlock later levels
# (logic assumes 20 lives per level). "+1 Life" is filler, created on demand only.
_QTY_3 = sum(1 for *_r, num, _lvl in PICKUPS if num == 3)
_QTY_5 = sum(1 for *_r, num, _lvl in PICKUPS if num == 5)
_QTY_10 = sum(1 for *_r, num, _lvl in PICKUPS if num == 10)


item_table: dict[str, ItemInfo] = {
    PLUS_3: ItemInfo(200, IC.progression, _QTY_3),
    PLUS_5: ItemInfo(201, IC.progression, _QTY_5),
    PLUS_10: ItemInfo(202, IC.progression, _QTY_10),
    FILLER: ItemInfo(203, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Lives"] = {f"{GAME_NAME} - {n}" for n in (PLUS_3, PLUS_5, PLUS_10, FILLER)}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
