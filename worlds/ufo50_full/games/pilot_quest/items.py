from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"

# Pilot Quest (o37_*) is an open-map build-up adventure. Simple implementation: nothing
# from this game enters the pool. Its filler is "+1 Zoldnak" -- a real reward that adds
# one Zoldnak (o37_Game.tokens, the Wild Zone currency) per copy -- so Pilot Quest is a
# "good filler" game. The framework pads every location with filler from the seed.
FILLER = "+1 Zoldnak"


item_table: dict[str, ItemInfo] = {
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # nothing from this game enters the pool as advancement; the framework fills its
    # locations with filler (its own "+1 Zoldnak" or another game's)
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
