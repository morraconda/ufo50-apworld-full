from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Magic Garden"

POTION = "Progressive Potion"
OPPY = "+1 Starting Red Oppy"
POTION_TIME = "Progressive Potion Time"
JUMP = "Jump"

# id offset layout inside Magic Garden's 1000-id block:
#   1  Progressive Potion       (x6 -- unlock progressively stronger brews; start with none.
#                                only 4 tiers exist, so copies 5 and 6 do nothing)
#   2  +1 Starting Red Oppy     (x4 -- extra oppies on the field at the start of a run;
#                                you begin with just one)
#   4  Progressive Potion Time  (x10 -- a potion's eating frenzy lasts 20 + 5 per copy on
#                                the in-game counter, vs 48 in vanilla. Also this game's
#                                filler: padding adds extra copies classified as filler)
#   5  Jump                     (x1 -- without it the jump button does nothing)
#   locations: see locations.py; 997/998/999 = Gift / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    POTION: ItemInfo(1, IC.progression, 6),
    OPPY: ItemInfo(2, IC.progression, 4),
    POTION_TIME: ItemInfo(4, IC.progression, 10),
    JUMP: ItemInfo(5, IC.progression, 1),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 6x Progressive Potion + 4x +1 Starting Red Oppy + 10x Progressive Potion Time +
    # 1x Jump; the framework pads with filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {POTION_TIME}"
