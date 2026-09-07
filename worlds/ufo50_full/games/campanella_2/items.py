from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 2"

MAX_HP = "+1 Max HP"
MAX_FUEL = "+100 Max Fuel"
COIN_MULT = "+20% Coin Multiplier"

# Three shop gear items -- the permanent HUD items priced 100 coins in o38_NPC
# (priceDefault). Purely quality-of-life, nothing in logic needs them, so `useful`.
MIRROR_SLASH = "Mirror Slash"
WING_BOOTS = "Wing Boots"
COMPASS = "Compass"

COINS = "+50 Coins"

# id offset layout inside Campanella 2's 1000-id block (game-wide items sit in 1..9,
# below level 1's level_id block at 10..):
#   1  +1 Max HP             (x11; run starts with 5 max HP, each adds 1)
#   2  +100 Max Fuel         (x13; run starts with 700 max fuel, each adds 100)
#   3  +20% Coin Multiplier  (x5; additive, base x1.0, each adds +0.2)
#   4  Mirror Slash          (o38_Game ITEM_MIRROR_SLASH = 1)
#   5  Wing Boots            (o38_Game ITEM_WING_BOOTS  = 5)
#   6  Compass               (o38_Game ITEM_COMPASS     = 14)
#   7  +50 Coins             (filler; +50 to a run's starting coins)
#   locations: see locations.py; 997/998/999 = Gift / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    MAX_HP: ItemInfo(1, IC.progression, 11),
    MAX_FUEL: ItemInfo(2, IC.progression, 13),
    COIN_MULT: ItemInfo(3, IC.progression, 5),
    MIRROR_SLASH: ItemInfo(4, IC.useful, 1),
    WING_BOOTS: ItemInfo(5, IC.useful, 1),
    COMPASS: ItemInfo(6, IC.useful, 1),
    COINS: ItemInfo(7, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Gear"] = {f"{GAME_NAME} - {name}"
                                    for name in (MIRROR_SLASH, WING_BOOTS, COMPASS)}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 11x +1 Max HP + 13x +100 Max Fuel + 5x +20% Coin Multiplier + 3 gear items; the
    # framework pads the rest with "+50 Coins" filler.
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {COINS}"
