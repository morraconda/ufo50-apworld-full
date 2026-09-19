from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Planet Zoldath"

# Planet Zoldath (o48_*) is a procedurally-generated survival-adventure. In-game energy
# cubes become AP location pickups; the eight equipment items, extra health and carry
# slots become AP items.
ENERGY_CUBE = "Energy Cube"       # +1 max health each: start hp/hpMax 3 -> up to 10
ITEM_SLOT = "Item Slot"           # start with 0 carry slots -> up to 3
# filler, but a functional one -- each copy independently rolls a random resource tier
# (o48_Game.resources[0..3], irandom, unseeded, 1/4 chance each) and adds 1 to it, so
# Planet Zoldath counts as a "good filler game" (not in __init__.bad_filler_games).
START_RESOURCE = "+1 Starting Resource"
# useful, not progression -- doubles every resource gain (starting roll, mid-run
# "+1 Starting Resource" top-up, and in-game pickups/trades/boomerang returns) once held.
DOUBLE_RESOURCES = "Double Resources"

# The eight equipment items (o48 ITEM_* / 48_Text.json item_name_0..7). Without the
# unlock, the pickup in the world is replaced by a friendly NPC who stole it. Two copies
# of each in the pool -- either one unlocks it, holding both does nothing extra (the mod
# only ever checks has_item, never a count), so this is purely a softlock/BK safety net.
# Named "Progressive <Item>" to match -- cosmetic only, the mod also draws a small "+"
# in the corner of the item's icon (both the world pickup and the HUD carry slot).
ZOLDATH_ITEM_COUNT = 2
ZOLDATH_ITEMS: tuple[str, ...] = (
    "Progressive Metamorpher",       # 0  ITEM_SHRINK_RAY
    "Progressive Pulse Generator",   # 1  ITEM_PULSE_DEVICE
    "Progressive Hazard Boots",      # 2  ITEM_HAZARD_BOOTS
    "Progressive Translator",        # 3  ITEM_TRANSLATOR
    "Progressive Boomerang",         # 4  ITEM_BOOMERANG
    "Progressive Meat Printer",      # 5  ITEM_BAIT
    "Progressive Nail Gun",          # 6  ITEM_NAIL_GUN
    "Progressive Bombs",             # 7  ITEM_BOMB
)

# id offset layout inside Planet Zoldath's 1000-id block:
#     1..20    Random Check <n>
#     21..27   Overworld Map Piece 1..3 / Trade Map Piece 1..2 / Dungeon Map Piece 1..2
#   200        +1 Starting Resource (filler)
#   501        Energy Cube (x7, +1 max health each)   502  Item Slot (x3)
#   503        Double Resources (useful, x1)
#   511..518   the eight equipment items (x2 each)
#   997/998/999   Gift / Gold / Cherry
ENERGY_CUBE_COUNT = 7
ITEM_SLOT_COUNT = 3


item_table: dict[str, ItemInfo] = {
    ENERGY_CUBE: ItemInfo(501, IC.progression, ENERGY_CUBE_COUNT),
    ITEM_SLOT: ItemInfo(502, IC.progression, ITEM_SLOT_COUNT),
    DOUBLE_RESOURCES: ItemInfo(503, IC.useful, 1),
    **{name: ItemInfo(511 + i, IC.progression, ZOLDATH_ITEM_COUNT) for i, name in enumerate(ZOLDATH_ITEMS)},
    START_RESOURCE: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Equipment"] = {f"{GAME_NAME} - {name}" for name in ZOLDATH_ITEMS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 7 Energy Cube + 3 Item Slot + Double Resources + 8 equipment x2; framework pads
    # with resources
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {START_RESOURCE}"
