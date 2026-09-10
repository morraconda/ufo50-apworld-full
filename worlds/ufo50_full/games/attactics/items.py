from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Attactics"

TURN_TIME = "+1s Turn Time"
PROMOTION = "Promotion"
EXPLOSIONS = "Explosions"
GRUNT_DEFENCE = "Grunt Defence"
FILLER = "Encouragement"

# id offset layout inside Attactics' 1000-id block:
#   1  +1s Turn Time  (x11 -- more thinking time per turn; also the campaign-chain
#                      currency. Base timer is 4s and logic assumes everything is
#                      possible at 12s total, i.e. 8 of these; 3 copies are surplus.)
#   2  Promotion      (x1 -- also required for deep campaign levels and the upper
#                      ranked ladder; see rules.py)
#   3  Encouragement  (filler -- a "nice try" with no mechanical effect; Attactics is
#                      a bad filler game)
#   4  Explosions     (useful x1 -- Kamikaze units don't detonate on death without it)
#   5  Grunt Defence  (useful x1 -- grunts in a column of 3 don't get the no-melee-damage
#                      formation without it)
#   locations: see locations.py; 997/998/999 = Gift / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    TURN_TIME: ItemInfo(1, IC.progression, 11),
    PROMOTION: ItemInfo(2, IC.progression, 1),
    EXPLOSIONS: ItemInfo(4, IC.useful, 1),
    GRUNT_DEFENCE: ItemInfo(5, IC.useful, 1),
    FILLER: ItemInfo(3, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 11x +1s Turn Time + 1x Promotion; the framework pads the rest with filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
