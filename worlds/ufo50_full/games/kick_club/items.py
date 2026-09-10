from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Kick Club"

REAL_SECOND = "+5 Seconds"
EXTRA_LIFE = "Extra Life"

# id offset layout inside Kick Club's 1000-id block:
#   1  +5 Seconds   (progression x40 -- each adds 5 real seconds to the single GLOBAL
#                    run timer, which starts at 25 and carries over between levels
#                    (Campanella-style); also this game's filler item. In logic: block K
#                    wants SECONDS_PER_BLOCK * (K-1) of them, same counts as before.)
#   2  Extra Life   (progression x10 -- each adds 1 life; you start a run with 0)
#   locations: see locations.py; 997/998/999 = Gift / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    REAL_SECOND: ItemInfo(1, IC.progression, 40),
    EXTRA_LIFE: ItemInfo(2, IC.progression, 10),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 40x +5 Seconds + 10x Extra Life; the framework pads the rest with "+5 Seconds"
    # filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {REAL_SECOND}"
