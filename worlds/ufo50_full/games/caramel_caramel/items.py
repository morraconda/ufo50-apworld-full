from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Caramel Caramel"

# Caramel Caramel has six photo-shoot levels (o46_Mas normalizedLevel 1..6). One real
# item, "Shooting" (100) -- the fire1 weapon (o46_pFire1 / o46_pFire2). Without it the
# mod destroys every player shot, so you can still fly + take photos (letters, wrenches)
# but can't kill enemies / clear a level. Filler is the do-nothing Encouragement
# (Caramel Caramel is in `bad_filler_games`).
SHOOTING = "Shooting"
FILLER = "Encouragement"

# id offset layout: 100 Shooting; 200 Encouragement (filler); locations use level_id.


item_table: dict[str, ItemInfo] = {
    SHOOTING: ItemInfo(100, IC.progression, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # Shooting enters the pool; the framework fills the rest of the locations with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
