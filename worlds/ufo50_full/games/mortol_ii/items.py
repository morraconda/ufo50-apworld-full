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
# rules.py's door()/doors() index this by number.
DOOR_NAMES = (
    "Hearts Upper Door 1", "Hearts Upper Door 2", "Hearts Upper Door 3", "Hearts Upper Door 4",
    "Hearts Lower Door 1", "Hearts Lower Door 2", "Hearts Lower Door 3", "Hearts Lower Door 4",
    "Tree Door", "Bottom Door", "Castle Entry Door", "Castle Door 1", "Castle Door 2",
    "Subsurface Key Door",
)
NUM_DOORS = len(DOOR_NAMES)
# "blue/green/yellow switch blocks" -- each item toggles that colour's switch blocks.
SWITCH_COLORS = ("Blue", "Green", "Yellow")

# The "lives" resource (rules.py: each region has a hardcoded life requirement, from a
# STARTING_LIVES 30 budget + these). "+10 Lives" is progression (state.count only sees
# advancement items) -- 7 of them, worth 10 each, is enough for every region incl.
# "Cherry Ending" (99). "+5 Lives" is the filler (worth 5 each in-game via the mod;
# framework-padding copies are plain filler so they do not count toward logic).
LIFE_PICKUP = "+10 Lives"
LIFE_PICKUP_COUNT = 7
LIFE_PICKUP_VALUE = 10
FILLER = "+5 Lives"
FILLER_VALUE = 5

# id offset layout inside Mortol II's 1000-id block:
#   101..104   Warrior / Scout / Engineer / Bomber
#   111..124   the 14 locked doors (DOOR_NAMES order = door number 1..14)
#   141..143   Blue / Green / Yellow Switch Block
#   200        +5 Lives (filler)      201  +10 Lives (x7, progression -- lives resource;
#                                          x6 when this game has no Cherry check)


def _build_item_table() -> dict[str, ItemInfo]:
    table: dict[str, ItemInfo] = {}
    for offset, name in enumerate(CHARACTERS, start=101):
        table[name] = ItemInfo(offset, IC.progression, 1)
    for n, name in enumerate(DOOR_NAMES, start=1):
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
    # "+10 Lives" x7 is calibrated for "Cherry Ending" (99 lives); "Ending" (Gold) only
    # needs 2. Drop one copy when this game has no Cherry so the pool doesn't exceed the
    # Cherry-less location count.
    overrides = None
    if GAME_NAME not in world.options.cherry_enabled_games.value:
        overrides = {LIFE_PICKUP: LIFE_PICKUP_COUNT - 1}
    return _create_items(GAME_NAME, item_table, world, overrides)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
