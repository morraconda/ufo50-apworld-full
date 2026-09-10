from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Ninpek"

# Ninpek is an endless arcade run-and-gun (o34_Mas). Its shuriken IS the weapon: the mod
# blocks all shooting until you have received at least one "Shuriken" (id 100, x5), and
# each Shuriken opens up 10,000 more points of logic (rules.py -- score milestones above
# 5,000 are gated on the count). Encouragement stays the filler (a nothing item, so
# Ninpek is still a "bad filler" game).
SHURIKEN = "Shuriken"
SHURIKEN_COUNT = 5
FILLER = "Encouragement"


item_table: dict[str, ItemInfo] = {
    SHURIKEN: ItemInfo(100, IC.progression, SHURIKEN_COUNT),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Shurikens"] = {f"{GAME_NAME} - {SHURIKEN}"}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 5 Shuriken into the pool; the framework fills the rest of Ninpek's locations with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
