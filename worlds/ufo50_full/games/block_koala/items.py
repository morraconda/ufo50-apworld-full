from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)
from .locations import sphere_1_locs

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Block Koala"

item_table: dict[str, ItemInfo] = {
    "Start Gate": ItemInfo(0, IC.progression),
    "Bottom Left Gate": ItemInfo(1, IC.progression),
    "Centre Gate": ItemInfo(2, IC.progression),
    "Mid Left Gate": ItemInfo(3, IC.progression),
    "Top Right Gates": ItemInfo(4, IC.progression),
    "Boss Gate": ItemInfo(6, IC.progression),
    "Koala Fact": ItemInfo(101, IC.filler, quantity=44),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    overrides = None
    if world.options.block_koala_early_start_gate:
        start_gate = create_item("Start Gate", world)
        world.get_location(f"{GAME_NAME} - " + world.random.choice(sphere_1_locs)).place_locked_item(start_gate)
        overrides = {"Start Gate": 0}
    return _create_items(GAME_NAME, item_table, world, overrides)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - Koala Fact"
