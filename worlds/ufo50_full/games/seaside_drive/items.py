from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Seaside Drive"

# Seaside Drive is a five-stage drive (o47_Control.level 0..4). One real item,
# "Progressive Max Charge" x4 -- the mod caps the player's drift-charge gauge
# (o47_Player.driftgauge) lower with fewer copies, so grade 2 / grade 3 charge shots
# stay out of reach: 0-1 -> grade 1 only, 2 -> grade 2, 3 -> grade 3 (partial gauge),
# 4 -> full vanilla. Filler is the do-nothing Encouragement (Seaside Drive is in
# `bad_filler_games`).
PROG_CHARGE = "Progressive Max Charge"
PROG_CHARGE_COUNT = 4
FILLER = "Encouragement"

# id offset layout: 101 Progressive Max Charge; 200 Encouragement (filler).


item_table: dict[str, ItemInfo] = {
    PROG_CHARGE: ItemInfo(101, IC.progression, PROG_CHARGE_COUNT),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # the 4 Progressive Max Charge enter the pool; the framework fills the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
