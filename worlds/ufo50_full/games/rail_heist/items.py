from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items, level_id)
from .locations import LEVEL_NAMES

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rail Heist"
NUM_LEVELS = 20

# the global time upgrades apply to every level, hence the "All Levels" prefix
# (mirrors the per-level "<level> Time" / "<level> Bullets" items). FILLER is the
# weaker, filler-classified version of PLUS_2_SECONDS -- +1s to every level.
PLUS_2_SECONDS = "All Levels +2 Seconds"
FILLER = "All Levels +1 Second"


def _build_item_table() -> dict[str, ItemInfo]:
    # id offset layout inside Rail Heist's 1000-id block. Level-specific items are
    # grouped by level via game_helpers.level_id -- offset = level * 10 + slot, so
    # A Simple Heist (level 1) is Time 10 / Bullets 11, Roof Assault (level 2) is
    # 20 / 21, ... level 20 is 200 / 201.
    #   1   All Levels +2 Seconds   (x20 in the pool)
    #   2   All Levels +1 Second    (filler, created on demand only)
    table: dict[str, ItemInfo] = {
        PLUS_2_SECONDS: ItemInfo(1, IC.progression, 20),
        FILLER: ItemInfo(2, IC.filler, 0),
    }
    for level in range(1, NUM_LEVELS + 1):
        table[f"{LEVEL_NAMES[level]} Time"] = ItemInfo(level_id(level, 0), IC.progression, 1)
    for level in range(1, NUM_LEVELS + 1):
        table[f"{LEVEL_NAMES[level]} Bullets"] = ItemInfo(level_id(level, 1), IC.progression, 1)
    return table


item_table: dict[str, ItemInfo] = _build_item_table()


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    time_items = {f"{GAME_NAME} - {PLUS_2_SECONDS}", f"{GAME_NAME} - {FILLER}"}
    time_items |= {f"{GAME_NAME} - {LEVEL_NAMES[level]} Time" for level in range(1, NUM_LEVELS + 1)}
    bullet_items = {f"{GAME_NAME} - {LEVEL_NAMES[level]} Bullets" for level in range(1, NUM_LEVELS + 1)}
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Time"] = time_items
    groups[f"{GAME_NAME} - Bullets"] = bullet_items
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


STARTING_TIME_ITEM = f"{LEVEL_NAMES[1]} Time"  # "A Simple Heist Time"


def create_items(world: "UFO50World") -> list[Item]:
    # "A Simple Heist Time" is precollected -- it's the sphere-1 seed (all three of
    # Level 1's checks are reachable with no other items), replacing the old hardcoded
    # LEVEL_1_START_TIME. Its normal pool copy is kept: it does nothing extra in logic
    # (Level 1 is already fully open) but it keeps the fill's slack where the old
    # design's inert Level 1 Time item used to sit.
    world.multiworld.push_precollected(create_item(STARTING_TIME_ITEM, world))
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
