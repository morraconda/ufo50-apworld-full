from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Star Waspir"

# Star Waspir runs five waves (o17__Game.wave 1..5). Very basic logic: one item,
# "Shooting" (101). Without it the mod destroys every player shot on spawn and
# auto-clears wave 1, so only Wave 1 is beatable -- every other check needs Shooting.
# Filler is the do-nothing Encouragement (Star Waspir is in `bad_filler_games`).
SHOOTING = "Shooting"
FILLER = "Encouragement"

# id offset layout inside Star Waspir's 1000-id block:
#   101   Shooting
#   200   Encouragement (filler)
#   997/998/999   Gift / Gold / Cherry


item_table: dict[str, ItemInfo] = {
    SHOOTING: ItemInfo(101, IC.progression, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # Shooting enters the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
