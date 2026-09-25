from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Camouflage"

# Camouflage (o04_*) is a 15-level stealth game (guide the lizard home). All levels are
# open from the start; the one real item is Camouflage, the lizard's colour change
# (fire2) -- without it the lizard keeps its starting colour, which only gets you
# through the Sky Temple finale (and so Gold); every other check needs it. Encouragement is the do-nothing filler (hence a "bad
# filler" game).
CAMOUFLAGE = "Camouflage"
FILLER = "Encouragement"


item_table: dict[str, ItemInfo] = {
    CAMOUFLAGE: ItemInfo(1, IC.progression),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
