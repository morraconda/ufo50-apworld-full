from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hyper Contender"

# Hyper Contender is a platform-fighter tournament (o42_Game). You start with Yogo
# unlocked; the other 7 fighters arrive from the multiworld and only owned
# fighters can be chosen at the select screen. Item id = 101 + vanilla char
# index (0..7). Nothing in logic needs a specific fighter.
CHARACTERS: tuple[str, ...] = (
    "Elka",
    "Yogo",
    "Brazz",
    "Reck",
    "Sephy",
    "Gilroy",
    "Voltana",
    "Donkus",
)
STARTER = "Yogo"
# The tournament is winnable with any fighter, so this game contributes no real
# filler -- its filler is the do-nothing Encouragement (Hyper Contender is in `bad_filler_games`).
FILLER = "Encouragement"

# id offset layout inside Hyper Contender's 1000-id block:
#   101..108   the fighters (CHARACTERS order = vanilla char index 0..7)
#   200        Encouragement (filler)
#   997/998/999   Gift / Gold / Cherry


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(101 + i, IC.progression, 1) for i, name in enumerate(CHARACTERS)},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Fighters"] = {f"{GAME_NAME} - {name}" for name in CHARACTERS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # You start with STARTER unlocked; every other fighter is shuffled into the
    # multiworld. STARTER is never findable.
    world.multiworld.push_precollected(create_item(STARTER, world))
    return _create_items(GAME_NAME, item_table, world, quantity_overrides={STARTER: 0})


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
