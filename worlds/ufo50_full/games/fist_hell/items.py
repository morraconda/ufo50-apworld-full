from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Fist Hell"

# Fist Hell (o09__Game) is a five-"scare" beat-em-up. Mortol-style rework: every scare
# clear is a check, and every BILL and WATCH is a check, while in-game level progression
# stays vanilla. (Coins/$1 from trash cans and crates are left alone -- too many, and
# their placement is not cleanly enumerable -- they just give cash as normal.)
#
# Money items, each mirroring the in-game value (like Mortol's +3/+5/+10 life items):
#   $5  cash  -- a bill (o09_iCash01) hidden in a breakable. 9 total (2/3/3/1/0 per scare).
#   $10 watch -- dropped by the one killable o09_eUFO in scares 1-4. 4 total.
# 13 money items <-> 13 money checks, one to one. "$1" is only the fill-item name.
#
# A further scare needs $20 more than the last (rules.py, on the dollar total of money
# items received): Southside free, Ride or Die $20, The Darkwoods $40, Boardwalk Bash
# $60, Paradiso $80. (~$89 of money exists, so "$25/scare" -- $100 at Paradiso -- is out
# of reach; the rung is $20.)
#
# You start as CAT only; JAY / VICTOR / AMY are `useful` unlock items (never required)
# and the char-select screen blacks out the ones you have not received yet.
CASH = "$5"      # o09_iCash01 bills hidden in breakables
WATCH = "$10"    # o09_eUFO drops, scares 1-4
COINS = "$1"     # fill-item name only (no coin checks)
CASH_COUNT = 9
WATCH_COUNT = 4

CHARACTERS: tuple[str, ...] = ("Jay", "Victor", "Amy")
CHAR_OFFSET = {name: 101 + i for i, name in enumerate(CHARACTERS)}  # Jay 101 / Victor 102 / Amy 103

FILLER = COINS


item_table: dict[str, ItemInfo] = {
    CASH: ItemInfo(201, IC.progression, CASH_COUNT),
    WATCH: ItemInfo(202, IC.progression, WATCH_COUNT),
    COINS: ItemInfo(200, IC.filler, 0),
    **{name: ItemInfo(CHAR_OFFSET[name], IC.useful, 1) for name in CHARACTERS},
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Characters"] = {f"{GAME_NAME} - {name}" for name in CHARACTERS}
    groups[f"{GAME_NAME} - Money"] = {f"{GAME_NAME} - {n}" for n in (CASH, WATCH)}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 9x $5 + 4x $10 + the three character unlocks; framework pads leftovers with $1
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
