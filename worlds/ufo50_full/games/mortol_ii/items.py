from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# The four playable guises. Every location needs at least one of them.
CHARACTERS = ("Warrior", "Scout", "Engineer", "Bomber")
# The 14 locked doors, in door-number order (door n -> DOOR_NAMES[n - 1], id 110 + n).
# rules.py's door()/doors() index this by number. Doors 1-4 (Hearts Upper) and doors
# 5-8 (Hearts Lower) are each always required together as a group (doors(1, 4) /
# doors(1, 8), never individually), so each group shares a single item -- id 111 and
# 115, the first of each group's four slots; 112-114 and 116-118 are unused.
DOOR_NAMES = (
    "Hearts Upper Doors", "Hearts Upper Doors", "Hearts Upper Doors", "Hearts Upper Doors",
    "Hearts Lower Doors", "Hearts Lower Doors", "Hearts Lower Doors", "Hearts Lower Doors",
    "Tree Door", "Bottom Door", "Castle Entry Door", "Castle Door 1", "Castle Door 2",
    "Subsurface Key Door",
)
NUM_DOORS = len(DOOR_NAMES)
# "blue/green/yellow switch blocks" -- each item toggles that colour's switch blocks.
SWITCH_COLORS = ("Blue", "Green", "Yellow")

# The "lives" resource (rules.py: each region has a hardcoded life requirement, from a
# STARTING_LIVES 20 budget + these). "+10 Lives" is progression (state.count only sees
# advancement items) -- 10 of them, worth 10 each, is enough for every region incl.
# "Cherry Ending" (99). "+5 Lives" is the filler (worth 5 each in-game via the mod;
# framework-padding copies are plain filler so they do not count toward logic).
LIFE_PICKUP = "+10 Lives"
LIFE_PICKUP_COUNT = 10
LIFE_PICKUP_VALUE = 10
FILLER = "+5 Lives"
FILLER_VALUE = 5

# id offset layout inside Mortol II's 1000-id block:
#   101..104   Warrior / Scout / Engineer / Bomber
#   111..124   the 14 locked doors (DOOR_NAMES order = door number 1..14); 111 is
#              "Hearts Upper Doors" (covers door numbers 1-4, 112-114 unused), 115 is
#              "Hearts Lower Doors" (covers door numbers 5-8, 116-118 unused)
#   141..143   Blue / Green / Yellow Switch Block
#   200        +5 Lives (filler)      201  +10 Lives (x10, progression -- lives resource)


def _build_item_table() -> dict[str, ItemInfo]:
    table: dict[str, ItemInfo] = {}
    for offset, name in enumerate(CHARACTERS, start=101):
        table[name] = ItemInfo(offset, IC.progression, 1)
    for n, name in enumerate(DOOR_NAMES, start=1):
        if name in table:
            continue
        table[name] = ItemInfo(110 + n, IC.progression, 1)
    for offset, color in enumerate(SWITCH_COLORS, start=141):
        table[f"{color} Switch Block"] = ItemInfo(offset, IC.progression, 1)
    table[LIFE_PICKUP] = ItemInfo(201, IC.progression, LIFE_PICKUP_COUNT)
    table[FILLER] = ItemInfo(200, IC.filler, 0)
    return table


item_table: dict[str, ItemInfo] = _build_item_table()


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Characters"] = {f"{GAME_NAME} - {name}" for name in CHARACTERS}
    groups[f"{GAME_NAME} - Doors"] = {f"{GAME_NAME} - {name}" for name in DOOR_NAMES}
    groups[f"{GAME_NAME} - Switch Blocks"] = {f"{GAME_NAME} - {c} Switch Block" for c in SWITCH_COLORS}
    groups[f"{GAME_NAME} - Lives"] = {f"{GAME_NAME} - {LIFE_PICKUP}", f"{GAME_NAME} - {FILLER}"}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
