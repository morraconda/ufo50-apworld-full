from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# The four playable guises. Every check needs at least one of them.
CHARACTERS = ("Warrior", "Scout", "Engineer", "Bomber")
NUM_DOORS = 14
# "blue/green/yellow switch blocks" -- each item toggles that colour's switch blocks.
SWITCH_COLORS = ("Blue", "Green", "Yellow")
FILLER = "+1 Life"

# id offset layout inside Mortol II's 1000-id block:
#   101..104   Warrior / Scout / Engineer / Bomber
#   111..124   Door 1 .. Door 14
#   141..143   Blue / Green / Yellow Switch Block
#   200        +1 Life (filler)


def _build_item_table() -> dict[str, ItemInfo]:
    table: dict[str, ItemInfo] = {}
    for offset, name in enumerate(CHARACTERS, start=101):
        table[name] = ItemInfo(offset, IC.progression, 1)
    for n in range(1, NUM_DOORS + 1):
        table[f"Door {n}"] = ItemInfo(110 + n, IC.progression, 1)
    for offset, color in enumerate(SWITCH_COLORS, start=141):
        table[f"{color} Switch Block"] = ItemInfo(offset, IC.progression, 1)
    table[FILLER] = ItemInfo(200, IC.filler, 0)
    return table


item_table: dict[str, ItemInfo] = _build_item_table()


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Characters"] = {f"{GAME_NAME} - {name}" for name in CHARACTERS}
    groups[f"{GAME_NAME} - Doors"] = {f"{GAME_NAME} - Door {n}" for n in range(1, NUM_DOORS + 1)}
    groups[f"{GAME_NAME} - Switch Blocks"] = {f"{GAME_NAME} - {c} Switch Block" for c in SWITCH_COLORS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
