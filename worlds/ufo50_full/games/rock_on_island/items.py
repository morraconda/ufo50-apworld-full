from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rock On! Island"

# Rock On! Island (o44_*) is a tower-defense of 10 levels + 2 villages. The AP items do
# NOT hand you anything -- they merely unlock a build-menu option so it can be bought
# with meat (the mod gates each purchase on has_item / get_item_count).
CHICKENS = "Chickens"                              # MENU_BUY_CHICKEN
CAMPFIRES = "Campfires"                            # MENU_BUY_CAMPFIRE
PROG_SPEAR = "Progressive Spear"                   # x1 -> SPEAR_I ; x2 -> SPEAR_II + BOW
PROG_FIRE = "Progressive Fire"                     # x1 -> FIRE_I  ; x2 -> FIRE_II + TAR
PROG_ROCK = "Progressive Rock"                     # x1 -> ROCK_I  ; x2 -> ROCK_II + WHEEL
PROG_WEAPON_UP = "Progressive Weapon Upgrade"      # x1 -> ATK_UPGRADE_I  ; x2 -> ATK_UPGRADE_II
PROG_THROW_UP = "Progressive Throwing Upgrade"     # x1 -> DIST_UPGRADE_I ; x2 -> DIST_UPGRADE_II
FILLER = "+5 Starting Meat"

# id offset layout inside Rock On! Island's 1000-id block:
#   200        +5 Starting Meat (filler)
#   511        Chickens        512  Campfires
#   513        Progressive Spear (x2)
#   514        Progressive Fire (x2)
#   515        Progressive Rock (x2)
#   516        Progressive Weapon Upgrade (x2)
#   517        Progressive Throwing Upgrade (x2)


item_table: dict[str, ItemInfo] = {
    CHICKENS: ItemInfo(511, IC.progression, 1),
    CAMPFIRES: ItemInfo(512, IC.progression, 1),
    PROG_SPEAR: ItemInfo(513, IC.progression, 2),
    PROG_FIRE: ItemInfo(514, IC.progression, 2),
    PROG_ROCK: ItemInfo(515, IC.progression, 2),
    PROG_WEAPON_UP: ItemInfo(516, IC.progression, 2),
    PROG_THROW_UP: ItemInfo(517, IC.progression, 2),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Weapons"] = {f"{GAME_NAME} - {n}" for n in (PROG_SPEAR, PROG_FIRE, PROG_ROCK)}
    groups[f"{GAME_NAME} - Upgrades"] = {f"{GAME_NAME} - {n}" for n in (PROG_WEAPON_UP, PROG_THROW_UP)}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 12 progression unlocks enter the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
