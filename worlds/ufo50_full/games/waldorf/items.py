from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"

# id offset = 100 + the in-game ITEM_* constant (o21_Waldorf: BEACH_BALL=1, HARPOON=2,
# BALLOON=3, PROPELLER=4, BINOCULARS=5, CANNED_FISH=6). The player starts with one of
# each (pushed as precollected in create_items); the mod zeroes the vanilla loadout.
STARTING_ITEMS: dict[str, int] = {
    "Beach Ball": 101,
    "Harpoon": 102,
    "Balloon": 103,
    "Propeller": 104,
    "Binoculars": 105,
    "Canned Fish": 106,
}
FILLER = "Shell"


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(offset, IC.useful, 0) for name, offset in STARTING_ITEMS.items()},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Starting Items"] = {f"{GAME_NAME} - {name}" for name in STARTING_ITEMS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # one of each item, pre-collected -- they don't go in the pool
    for name in STARTING_ITEMS:
        world.multiworld.push_precollected(create_item(name, world))
    return []


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
