from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World

# adapted from Barbuta, thanks Scipio! <3

GAME_NAME = "Vainger"


item_table: dict[str, ItemInfo] = {
    "Heat Mod": ItemInfo(0, IC.progression | IC.useful, 1),
    "Multi Mod": ItemInfo(1, IC.progression | IC.useful, 1),
    "Pulse Mod": ItemInfo(2, IC.progression | IC.useful, 1),
    "Force Mod": ItemInfo(3, IC.progression | IC.useful, 1),
    "Stabilizer": ItemInfo(10, IC.progression, 2),
    "Clone Material": ItemInfo(11, IC.useful, 3),
    "Shield Upgrade": ItemInfo(12, IC.progression_skip_balancing, 25),
    "Key Code A": ItemInfo(20, IC.progression_skip_balancing, 1),
    "Key Code B": ItemInfo(21, IC.progression_skip_balancing, 1),
    "Key Code C": ItemInfo(22, IC.progression_skip_balancing, 1),
    "Key Code D": ItemInfo(23, IC.progression_skip_balancing, 1),
    "Progressive Security Clearance": ItemInfo(24, IC.progression, 3),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    item_groups = game_item_groups(GAME_NAME, item_table)
    item_groups[f"{GAME_NAME} - Mods"] = {f"{GAME_NAME} - {name}"
                                          for name in ["Heat Mod", "Multi Mod", "Pulse Mod", "Force Mod"]}
    item_groups[f"{GAME_NAME} - Key Codes"] = {f"{GAME_NAME} - Key Code {letter}" for letter in ["A", "B", "C", "D"]}
    return item_groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - Shield Upgrade"
