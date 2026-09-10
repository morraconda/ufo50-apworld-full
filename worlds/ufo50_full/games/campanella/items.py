from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella"

# Campanella (o03_*) is a 50-level lunar-lander shooter (A-1 .. E-Boss).
#
# Two currencies gate progress (see rules.py):
#  - Lives: you start a run with 3 (scr03_Init) and the mod grants the AP total on top,
#    mid-run. The vanilla "extra life every 1000 points" is disabled, so lives come only
#    from "+1 Life" items (each worth one whole life). "+1 Life" is also this game's filler.
#  - Fuel: max fuel is global, starts at 3x normal (300) and is NOT refilled per level;
#    enemy drops that also give points no longer give fuel. Each "Fuel Tank" item is
#    worth 300 fuel -- a full refill -- granted mid-run. Logic wants one fuel tank per
#    level / per 1000 pts.
#
# "Left Thruster" is a single progression item -- without it the ship cannot accelerate
# left, which is only survivable on a handful of early stages (see rules.py).
LIFE = "+1 Life"
FUEL_TANK = "Fuel Tank"
LEFT_THRUSTER = "Left Thruster"

# id offset layout inside Campanella's 1000-id block:
#     1..50    <stage> clear   (offset = o03_Mas.currStage + 1)
#   100..148   <stage> - Coffee   (offset = 100 + currStage; only the 8 non-bonus,
#              non-boss stages per world have one)
#   201..240   <n>000 Points   (offset = 200 + n, n = 1..40)
#   501 +1 Life   502 Fuel Tank   511 Left Thruster
#   997/998/999   Gift / Gold / Cherry
#
# "+1 Life" / "Fuel Tank" are progression (state.count only sees advancement items). The
# life / fuel gates in rules.py are capped at LIFE_CAP so the requirement never exceeds
# 20 of either; 60 of each go in the pool (plus framework padding with more "+1 Life").
LIFE_COUNT = 60
FUEL_TANK_COUNT = 60


item_table: dict[str, ItemInfo] = {
    LIFE: ItemInfo(501, IC.progression, LIFE_COUNT),
    FUEL_TANK: ItemInfo(502, IC.progression, FUEL_TANK_COUNT),
    LEFT_THRUSTER: ItemInfo(511, IC.progression, 1),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 60x +1 Life + 60x Fuel Tank + Left Thruster; framework pads leftovers with more +1 Life
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {LIFE}"
