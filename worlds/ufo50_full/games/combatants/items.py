from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Combatants"

# Combatants is a real-time ant-war campaign of 12 missions on a branching map
# (o25__Game, `mapComplete[0..11]`). Every mission starts unlocked, but the nine
# command-menu abilities are AP items -- the mod greys out and refuses to fire any
# ability the player has not received. Seven are advancement (mission gates); the two
# extras (Soldier Instinct, Surrender) are useful-only. Filler is "+20% Movement Speed"
# (additive: the player ant's walkSpeed becomes 0.4 * (1 + 0.2 * count)), so Combatants
# is a "good filler" game.
#
# Item offset == the in-game MENU_* radial-menu id it unlocks:
#   101 Follow / 102 Hold / 103 Instinct / 104 Soldier Follow / 105 Soldier Hold /
#   106 Soldier Instinct / 107 Produce Workers / 108 Produce Soldiers / 109 Surrender
PROGRESSION_ABILITIES: tuple[str, ...] = (
    "Follow", "Hold", "Instinct", "Soldier Follow", "Soldier Hold",
    "Produce Workers", "Produce Soldiers",
)
USEFUL_ABILITIES: tuple[str, ...] = ("Soldier Instinct", "Surrender")
ABILITIES: tuple[str, ...] = (*PROGRESSION_ABILITIES, *USEFUL_ABILITIES)

FILLER = "+20% Movement Speed"

_ABILITY_ID: dict[str, int] = {
    "Follow": 101, "Hold": 102, "Instinct": 103, "Soldier Follow": 104,
    "Soldier Hold": 105, "Soldier Instinct": 106, "Produce Workers": 107,
    "Produce Soldiers": 108, "Surrender": 109,
}


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(_ABILITY_ID[name], IC.progression, 1) for name in PROGRESSION_ABILITIES},
    **{name: ItemInfo(_ABILITY_ID[name], IC.useful, 1) for name in USEFUL_ABILITIES},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Abilities"] = {f"{GAME_NAME} - {name}" for name in ABILITIES}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # the nine abilities enter the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
