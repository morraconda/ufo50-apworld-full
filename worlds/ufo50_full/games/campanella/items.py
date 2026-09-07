from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella"

# Campanella (o03_*) is a 50-level lunar-lander shooter (A-1 .. E-Boss).
#
# Lives are the logic currency: you start a run with 3 (scr03_Init) and the mod grants
# the AP total on top, mid-run. The vanilla "extra life every 1000 points" is disabled,
# so lives come only from these items. Each "1/2 Life" is worth half a life -- two of
# them make one -- and it is also this game's filler item.
#
# "Left Thruster" is a single progression item -- without it the ship cannot accelerate
# left, which is only survivable on a handful of early stages (see rules.py).
HALF_LIFE = "1/2 Life"
LEFT_THRUSTER = "Left Thruster"

# id offset layout inside Campanella's 1000-id block:
#     1..50    <stage> clear   (offset = o03_Mas.currStage + 1)
#   100..148   <stage> - Coffee   (offset = 100 + currStage; only the 8 non-bonus,
#              non-boss stages per world have one)
#   201..240   <n>000 Points   (offset = 200 + n, n = 1..40)
#   501 1/2 Life   511 Left Thruster
#   997/998/999   Gift / Gold / Cherry
#
# "1/2 Life" is progression (state.count only sees advancement items). The life gates
# in rules.py are capped at LIFE_CAP so the pool stays a sane size -- 42 halves give
# 21 guaranteed lives, and the framework pads with more.
HALF_LIFE_COUNT = 42


item_table: dict[str, ItemInfo] = {
    HALF_LIFE: ItemInfo(501, IC.progression, HALF_LIFE_COUNT),
    LEFT_THRUSTER: ItemInfo(511, IC.progression, 1),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 100x 1/2 Life + Left Thruster; framework pads leftovers with more 1/2 Life
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {HALF_LIFE}"
