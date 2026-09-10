from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Quibble Race"

# Quibble Race (o14_*) is a 1-3 player betting board game. The four turn-menu "shops"
# and the six individual thug actions are AP items -- the mod greys the shop button /
# thug action out and refuses to open it without the matching item.
#
#   Trainer     -> the Stable menu  (STATE_TURN_STABLE, main menu sel2/subsel2)
#   Breeder     -> the Breeder menu (STATE_TURN_SPONSOR, sel1/subsel2)  -- Gift needs this
#   Infobot     -> the Infobot menu (STATE_TURN_INFO,   sel1/subsel1)
#   Loan Shark  -> the Loan Shark   (STATE_TURN_LOAN_SHARK, sel3/subsel1)
#   Steroids / Litter / Cripple / Drugs / Poison / Guard -> the six thug actions
#     (THUG_ROIDS..THUG_GUARD = 1..6 -> item offset 110 + id)
#
# All ten are advancement items so has_group counts them: "X won races" needs
# floor(X / 3) of them in logic, and Cherry needs all ten.
SHOP_ITEMS: tuple[str, ...] = ("Trainer", "Breeder", "Infobot", "Loan Shark")
THUG_ACTIONS: tuple[str, ...] = ("Steroids", "Litter", "Cripple", "Drugs", "Poison", "Guard")
BREEDER = "Breeder"
TOTAL_ITEMS = len(SHOP_ITEMS) + len(THUG_ACTIONS)

# real filler: +$100 to player 0's cash at the start of every game (and mid-game if it
# arrives late) -- so Quibble Race is a "good filler" game.
FILLER = "+$100 Starting Cash"


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(101 + i, IC.progression, 1) for i, name in enumerate(SHOP_ITEMS)},
    **{name: ItemInfo(111 + i, IC.progression, 1) for i, name in enumerate(THUG_ACTIONS)},
    FILLER: ItemInfo(200, IC.filler, 0),
}

UPGRADES_GROUP = f"{GAME_NAME} - Upgrades"


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[UPGRADES_GROUP] = {f"{GAME_NAME} - {name}" for name in (*SHOP_ITEMS, *THUG_ACTIONS)}
    groups[f"{GAME_NAME} - Thug Actions"] = {f"{GAME_NAME} - {name}" for name in THUG_ACTIONS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # the ten shop / thug items enter the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
