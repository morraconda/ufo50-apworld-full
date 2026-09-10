from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rakshasa"

# Rakshasa (o24_*) is a run-based action-platformer of three stages, each with a
# mid-boss. The three collectible weapon types are AP items -- without the unlock, the
# in-world weapon pickup gives 500 points instead (the mod). Filler is "500 Points"
# (a weak reward -> "bad filler" game).
# o24_Item WEAPON num 0/1/2 -> weaponCurr 0/1/2 in o24_Player_Other_10's switch:
# 0 = o24_Fireball + soundShotFire* (Fire), 1 = o24_Spreadshot x5 arc (Spreadshot),
# 2 = o24_Homeshot + soundShotHoming* (Homing). Order here maps i -> id 511/512/513.
WEAPONS: tuple[str, ...] = ("Fire Weapon", "Spreadshot", "Homing Shot")
FILLER = "500 Points"


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(511 + i, IC.progression, 1) for i, name in enumerate(WEAPONS)},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Weapons"] = {f"{GAME_NAME} - {name}" for name in WEAPONS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 3 weapons enter the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
