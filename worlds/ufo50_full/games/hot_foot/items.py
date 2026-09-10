from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hot Foot"

# Hot Foot is a 6-game bean-bag tournament (o43_Game, `game` 1..6). The draftable
# athletes are no longer AP items -- instead shuffled abilities gate the run:
#   Jumping (101) -- the mod blocks the player's jump without it; needed for every
#                    tournament game except the first two (and for Gift/Gold/Cherry).
#   Stars   (102) -- the mod blocks the player's special-meter moves without it;
#                    needed for games 5 & 6 and for Gold/Cherry.
#   Team Builder (103) -- unlocks the title-menu "BUILD TEAM" mode (custom roster);
#                    useful only, nothing in logic needs it.
# Filler is the do-nothing Encouragement (Hot Foot is in `bad_filler_games`).
JUMPING = "Jumping"
STARS = "Stars"
TEAM_BUILDER = "Team Builder"
FILLER = "Encouragement"

# id offset layout inside Hot Foot's 1000-id block:
#   101   Jumping
#   102   Stars
#   103   Team Builder
#   200   Encouragement (filler)
#   997/998/999   Gift / Gold / Cherry


item_table: dict[str, ItemInfo] = {
    JUMPING: ItemInfo(101, IC.progression, 1),
    STARS: ItemInfo(102, IC.progression, 1),
    TEAM_BUILDER: ItemInfo(103, IC.useful, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # Jumping and Stars enter the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
