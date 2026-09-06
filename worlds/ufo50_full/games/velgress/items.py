from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Velgress"

# The upgrades the Cavian's shop sells. In o15_Game the shuffled shopItems slots map
# to internal counters: values 0/1 -> iRecov, 2/3 -> iGun, 4/5 -> iFoot, 6 -> iMagnet,
# 7 -> iLightning, 8 -> iJump. Recovery / Power / Lightfoot each have two tiers, so
# their items stack x2; Magnet / Lightning / Double Jump are one-shot. Exactly nine
# purchases exist over a full climb (three slots per shop, three shops), matched
# one-to-one by these nine item copies. Nothing in Velgress' logic gates on them
# (every check is sphere 1), so they are `useful`, not progression.
UPGRADES: dict[str, tuple[int, int]] = {
    "Recovery": (101, 2),
    "Power": (102, 2),
    "Lightfoot": (103, 2),
    "Magnet": (104, 1),
    "Lightning": (105, 1),
    "Double Jump": (106, 1),
}
FILLER = "Coin"


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(offset, IC.useful, qty) for name, (offset, qty) in UPGRADES.items()},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Upgrades"] = {f"{GAME_NAME} - {name}" for name in UPGRADES}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # the nine upgrade copies into the pool; the framework pads the rest with Coin filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
