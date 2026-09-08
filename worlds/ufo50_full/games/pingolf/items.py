from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pingolf"

# Pingolf is an 18-hole pinball-golf game (o23_Mas / o23_Ball).
# One real item, "Dunking" (id 500): needed for every location EXCEPT the Par
# checks on the first eight holes (see locations.py / rules.py -- holes 9..18 and
# Gift/Gold/Cherry live behind it). Without it the mod re-labels the DUNK button
# "DUNK'NT". Everything else this game contributes is the Encouragement filler
# (a nothing item -- Pingolf is a "bad filler" game).
DUNKING = "Dunking"
FILLER = "Encouragement"


item_table: dict[str, ItemInfo] = {
    DUNKING: ItemInfo(500, IC.progression, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # one "Dunking" into the pool; the framework fills the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
