from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Barbuta"

item_table: dict[str, ItemInfo] = {
    "$50": ItemInfo(0, IC.progression, 5),
    "$100": ItemInfo(1, IC.progression, 5),
    "Umbrella": ItemInfo(2, IC.progression, 1),
    "Necklace": ItemInfo(3, IC.progression, 1),
    "Pin": ItemInfo(4, IC.progression | IC.useful, 1),
    "Candy": ItemInfo(5, IC.progression, 1),
    "Wand": ItemInfo(6, IC.progression | IC.useful, 1),
    "Blood Sword": ItemInfo(7, IC.progression, 1),
    "Key": ItemInfo(8, IC.progression, 1),
    "Bat Orb": ItemInfo(9, IC.progression, 1),
    "Trash": ItemInfo(10, IC.filler, 1),
    "Egg": ItemInfo(11, IC.progression, 2),
    "A Broken Wall": ItemInfo(12, IC.progression, 1),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - Egg"
