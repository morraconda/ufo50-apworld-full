from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Divers"

# Divers (o19_*) is a party RPG dive. The AP items are quality-of-life only:
#   +20% XP Multiplier (useful) -- each copy adds 20% to post-battle XP gain.
#   +200 Gold (filler) -- each copy received adds 200 to global.g19_cash (cap 9999).
XP_MULT = "+20% XP Multiplier"
FILLER = "+200 Gold"


item_table: dict[str, ItemInfo] = {
    XP_MULT: ItemInfo(511, IC.useful, 10),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # only the 10 XP-multiplier useful items enter the pool; the framework pads with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
