from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Onion Delivery"

# Onion Delivery is a seven-day week (o32_Mas.dayNumber 0..6). Two restrictive items
# go in the pool, and the mod reads them live every frame (has_item):
#   101 Throttle  -- without it the gas button does nothing; the van can only reverse.
#   102 Handbrake -- without it gas+brake while turning never starts a drift
#                    (so no drift / spin attack); reversing is unaffected.
#   103 Progressive Top Speed -- top speed starts at 3 of the 7 speedometer bars; each
#                    copy is +1 bar (4 copies = vanilla, the 5th goes past it). Extra
#                    copies are also this game's filler.
# Gating is in rules.py.
THROTTLE = "Throttle"
HANDBRAKE = "Handbrake"
TOP_SPEED = "Progressive Top Speed"
NUM_TOP_SPEED = 5


item_table: dict[str, ItemInfo] = {
    THROTTLE: ItemInfo(101, IC.progression, 1),
    HANDBRAKE: ItemInfo(102, IC.progression, 1),
    TOP_SPEED: ItemInfo(103, IC.progression, NUM_TOP_SPEED),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # Throttle + Handbrake + 5 Progressive Top Speed into the pool; the framework pads
    # the rest with more Progressive Top Speed (as filler)
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {TOP_SPEED}"
