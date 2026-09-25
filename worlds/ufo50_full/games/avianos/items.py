from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Avianos"

# Avianos is an eight-scenario turn-based strategy game (o50_Game).
# Progression (1P, mod-side locks while missing):
#   Blessings -- without it, earned blessings are never granted (no action upgrades)
#   Rexadon   -- without it, you cannot pray to Rexadon
#   Trilock   -- without it, you cannot pray to Trilock
# Filler starting-resource bonuses: +3 Starting Seeds (x3), +1 Starting Bone (x1),
# +1 Starting Worker (x1). All three stack past that as filler padding; the framework
# pads the rest of its locations with filler.
BLESSINGS = "Blessings"
REXADON = "Rexadon"
TRILOCK = "Trilock"
STARTING_SEEDS = "+3 Starting Seeds"
STARTING_BONE = "+1 Starting Bone"
STARTING_WORKER = "+1 Starting Worker"


item_table: dict[str, ItemInfo] = {
    BLESSINGS: ItemInfo(1, IC.progression),
    REXADON: ItemInfo(2, IC.progression),
    TRILOCK: ItemInfo(3, IC.progression),
    STARTING_SEEDS: ItemInfo(201, IC.filler, 3),
    STARTING_BONE: ItemInfo(202, IC.filler, 1),
    STARTING_WORKER: ItemInfo(203, IC.filler, 1),
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
    return f"{GAME_NAME} - {world.random.choice((STARTING_SEEDS, STARTING_BONE, STARTING_WORKER))}"
