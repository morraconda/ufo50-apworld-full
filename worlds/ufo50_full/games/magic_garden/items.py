from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Magic Garden"

POTION = "Progressive Potion"
OPPY = "+1 Starting Red Oppy"
FILLER = "Cloverana's Love"

# id offset layout inside Magic Garden's 1000-id block:
#   1  Progressive Potion    (x4 -- unlock progressively stronger brews; start with none)
#   2  +1 Starting Red Oppy  (x4 -- extra oppies on the field at the start of a run;
#                             you begin with just one)
#   3  Cloverana's Love      (filler -- does nothing)
#   locations: see locations.py; 997/998/999 = Garden / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    POTION: ItemInfo(1, IC.progression, 4),
    OPPY: ItemInfo(2, IC.progression, 4),
    FILLER: ItemInfo(3, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 4x Progressive Potion + 4x +1 Starting Red Oppy; the framework pads with filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
