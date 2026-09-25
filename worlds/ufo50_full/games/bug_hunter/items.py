from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Bug Hunter"

# Bug Hunter is an endless job streak; the first six jobs (Gift at 1, Gold at 3, Cherry at 6)
# and kill counts / held energy are the locations. The items lock parts of your hand / the
# shop (1P only, mod-side): Module 6 / 7 (deck slots 6 / 7), Shop Slot 1..3 (the first
# three shop entries). +1 Max Energy (x10) raises the energy cap from 5. +1 Energy Cube
# Drop (x6) drops one more energy cube each day; +1 Starting Energy (x5) is energy you
# start each job with. All three stack past that as filler (padding copies are
# filler-classified, so logic only counts the 10 Max Energy).
MODULES = ("Module 6", "Module 7")
SHOP_SLOTS = ("Shop Slot 1", "Shop Slot 2", "Shop Slot 3")
ENERGY_DROP = "+1 Energy Cube Drop"
MAX_ENERGY = "+1 Max Energy"
STARTING_ENERGY = "+1 Starting Energy"


item_table: dict[str, ItemInfo] = {
    MODULES[0]: ItemInfo(2, IC.progression),
    MODULES[1]: ItemInfo(3, IC.progression),
    SHOP_SLOTS[0]: ItemInfo(4, IC.progression),
    SHOP_SLOTS[1]: ItemInfo(5, IC.progression),
    SHOP_SLOTS[2]: ItemInfo(6, IC.progression),
    ENERGY_DROP: ItemInfo(7, IC.filler, 6),
    MAX_ENERGY: ItemInfo(8, IC.progression, 10),
    STARTING_ENERGY: ItemInfo(9, IC.filler, 5),
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
    return f"{GAME_NAME} - {world.random.choice((ENERGY_DROP, STARTING_ENERGY, MAX_ENERGY))}"
