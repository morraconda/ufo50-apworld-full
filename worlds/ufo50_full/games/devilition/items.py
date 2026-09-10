from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Devilition"

# Devilition is a ten-round survival puzzler (o05_Game). Rounds no longer hand out
# pieces -- your placement budget starts at the vanilla 15 and only grows from items:
#   "+15 Pieces"      (id 101, progression, PLUS_15_COUNT) -- +15 to the per-run budget
#   "+5 Pieces"       (id 102, filler)           -- +5 to the per-run piece budget
#   "Tier 1 Pieces"   (id 100, progression, x1)  -- unlocks the tier-1 bag pieces
#                     (Bomb / Cannon / Rocket); without it those never draw, so rounds
#                     past 3 are unwinnable.
# Logic (rules.py): round n needs (n-1) "+15 Pieces"; rounds 4-10 also need "Tier 1
# Pieces". Devilition is a GOOD filler game now ("+5 Pieces" is a real bonus).
PLUS_15 = "+15 Pieces"
TIER1 = "Tier 1 Pieces"
FILLER = "+5 Pieces"

PLUS_15_COUNT = 15


item_table: dict[str, ItemInfo] = {
    TIER1: ItemInfo(100, IC.progression, 1),
    PLUS_15: ItemInfo(101, IC.progression, PLUS_15_COUNT),
    FILLER: ItemInfo(102, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # PLUS_15_COUNT "+15 Pieces" + 1 "Tier 1 Pieces" into the pool; the framework pads
    # the rest of Devilition's locations with "+5 Pieces".
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
