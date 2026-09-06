from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Attactics"

TURN_TIME = "+1s Turn Time"
PROMOTION = "Promotion"
FILLER = "Encouragement"

# id offset layout inside Attactics' 1000-id block:
#   1  +1s Turn Time  (x24 -- more thinking time per turn; also the campaign-chain
#                      currency, one needed per level reached; see rules.py)
#   2  Promotion      (x1 -- also required for deep campaign levels and the upper
#                      ranked ladder; see rules.py)
#   3  Encouragement  (filler -- a "nice try" with no mechanical effect; Attactics is
#                      a bad filler game)
#   locations: see locations.py; 997/998/999 = Garden / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    TURN_TIME: ItemInfo(1, IC.progression, 24),
    PROMOTION: ItemInfo(2, IC.progression, 1),
    FILLER: ItemInfo(3, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 24x +1s Turn Time + 1x Promotion; the framework pads the rest with filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
