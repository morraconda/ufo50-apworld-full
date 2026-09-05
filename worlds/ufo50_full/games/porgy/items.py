from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)
from ...options import PorgyRadar

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Porgy"


class ItemInfo(NamedTuple):
    id_offset: int
    classification: IC
    quantity: int
    group: Optional[str] = None


item_table: dict[str, ItemInfo] = {
    "Torpedo Upgrade": ItemInfo(300, IC.progression, 20),
    "Fuel Tank": ItemInfo(301, IC.progression, 20),
    "Fish Gratitude": ItemInfo(302, IC.progression, 20),
    # modules
    "Missile System Module": ItemInfo(191, IC.progression, 1, "Modules"),
    "Radar System Module": ItemInfo(291, IC.progression, 1, "Modules"),
    "Buster Torpedoes Module": ItemInfo(90, IC.progression, 1, "Modules"),
    "Depth Charge Module": ItemInfo(92, IC.progression, 1, "Modules"),
    "Efficient Fuel Module": ItemInfo(290, IC.progression, 1, "Modules"),
    "Armor Plating Module": ItemInfo(292, IC.useful, 1, "Modules"),
    "Super Booster Module": ItemInfo(93, IC.useful, 1, "Modules"),
    "Spotlight Module": ItemInfo(192, IC.progression, 1, "Modules"),
    "Drill Module": ItemInfo(91, IC.progression, 1, "Modules"),
    "Targeting System Module": ItemInfo(190, IC.useful, 1, "Modules"),

    # the mcguffins
    "Strange Light": ItemInfo(303, IC.progression_skip_balancing, 5),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    overrides = {"Radar System Module": 0} if world.options.porgy_radar == PorgyRadar.option_always_on else None
    return _create_items(GAME_NAME, item_table, world, overrides)


filler_items = ["Porgy - Fuel Tank", "Porgy - Torpedo Upgrade"]


def get_filler_item_name(world: "UFO50World") -> str:
    return world.random.choice(filler_items)
