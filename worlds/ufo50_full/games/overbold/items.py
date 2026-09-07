from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Overbold"

# Overbold (o30_*) is a wave-survival arena shooter where you can voluntarily raise the
# wave's prize (o30_Game.prize, $100..$1600) and buy gear between waves.
#   Sales   (useful) -- every gear item is flagged on sale each shop visit (-$100);
#           the vanilla price hike still rolls and applies on top of it.
#   +$100 Starting Cash (filler) -- START_MONEY gets +100 per copy received.
SALES = "Sales"
FILLER = "+$100 Starting Cash"


item_table: dict[str, ItemInfo] = {
    SALES: ItemInfo(511, IC.useful, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    return game_item_groups(GAME_NAME, item_table)


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # only the Sales useful item enters the pool; the framework pads the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
