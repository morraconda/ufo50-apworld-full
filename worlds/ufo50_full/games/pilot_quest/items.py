from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"

# Pilot Quest (o37_*): the Wild Zone (rm37_Incremental2) is split into regions by its
# obstacle blocks and teleporters. Every block starts in place and every teleporter
# starts off; each individual block cluster / teleporter pad is its own item.
#
# The Campsite builds and Dr Lumin's upgrades are decoupled from their
# locations: doing the thing in-game sends the check, and what it would have given you
# (a silo, a workbench, a friend, an upgrade) arrives as an item. Ship parts stay
# vanilla pickups (locations only), as does Ship Fuel (neither).
#
# In vanilla the blocks are the o37__obsA / __obsB / __obsCa / __obsCb / __obsCc
# children, shown or destroyed per run by the obsA/obsB/obsC rolls in scr37_ResetData.
# Here each placed cluster is identified by its room position (top-left instance x,y),
# which the mod must match. "Start-Borlg Area Gate" is new -- it plugs the 64px gap
# at room (1792..1855, ~1504) between Start and the Borlg building.
#
# id offset layout (locations use 1..84 and 997..999 -- items have their own id space):
#      3       Progressive Resource Cap (x4): one resource cap step each (the silos are
#              built in vanilla and no longer raise the caps)
#      4       Meat Shack (builds Parvina's shack, which can't be bought in-game)
#              -- with a Seed, what logic expects before the Wild Zone
#      8       Gear (needed to buy anything that costs science, Ship Fuel included)
#      9       Unktomi (brings her to the Campsite to make silk; needed to buy anything
#              that costs silk)
#      5..7    x2 Ingots / x2 Research / x2 Silk (x5 each; each copy doubles that
#              resource's income)
#     11       Workbench (x6)
#     12       Seed (x6): plants one Moon Drop plant each
#     22       x2 Moon Drops (x5): doubles Moon Drop income
#     23       -50% Meat Generation Time (x4): each halves the Meat Shack's meat timer
#     13..14   Ingot Table / Science Table
#     15..16   Letter (Grull trades it for the Blaster pickup) / Blaster
#     20       x2 Idle Time Multiplier (x4): doubles the time counted while you're away
#     17..19   Productivity / Defense / Metabolism (x5 each): each gives that
#              prestige statue at level = copies held (the statues no longer upgrade)
#     21       Friend (x10)
#     61..65   <Dr Lumin upgrade>
#    101..106  region-boundary blocks
#    111..115  Bottom Left blocks (its entrances, and the Bottom Left Chest pocket)
#    121..124  teleporter pads, teleporter[0..3]
#    201..203  +1 Ingot / +1 Science / +1 Silk (filler; each doubled by its x2 item)
FILLERS: dict[str, int] = {"+1 Ingot": 201, "+1 Science": 202, "+1 Silk": 203}

NUM_SILOS = 2
NUM_RESOURCE_CAPS = 4
NUM_WORKBENCHES = 6
NUM_FRIENDS = 10
NUM_INCOME_DOUBLERS = 5
NUM_IDLE_MULTIPLIERS = 4
NUM_SEEDS = 6
PRESTIGE_LEVELS = 5

# Dr. Lumin's shop, in shopBought[0..4] order (scr37_ResetData); offsets 61..65. The
# sixth, Ship Fuel (shopBought[5]), is left vanilla: no location, no item -- but the
# launch needs it, and it costs science, so Gold needs the Gear.
# the upgrades that cost science, so need the Gear to buy
SCIENCE_UPGRADES: tuple[str, ...] = ("Fertilizer", "Stamin Pill", "Wizard Yoyo")
# the upgrades that cost silk, so need Unktomi to buy
SILK_UPGRADES: tuple[str, ...] = ("Big Silos", "Stamin Pill", "Wizard Yoyo")
LUMIN_UPGRADES: tuple[str, ...] = (
    "Metal Yoyo", "Fertilizer", "Big Silos", "Stamin Pill", "Wizard Yoyo",
)

# name -> (id offset, room x, room y, vanilla object) for every block item
BLOCKS: dict[str, tuple[int, int, int, str]] = {
    "Start-Borlg Area Gate":           (101, 1792, 1504, "(new)"),
    "Start-Right Side Bushes (Upper)": (102, 2912, 1472, "o37_obsA2"),
    "Start-Right Side Bushes (Lower)": (103, 3392, 1568, "o37_obsB2"),
    "Borlg Area-Top Bones":            (104, 2128, 400,  "o37_obsCb"),
    "Left Side-Borlg Area Bones":      (105, 544,  816,  "o37_obsCa"),
    "Left Side-Top Bones":             (106, 784,  192,  "o37_obsCc"),
    "Left Side Tree 1":                (111, 144,  1728, "o37_obsB1"),
    "Left Side Tree 2":                (112, 224,  1648, "o37_obsB1"),
    "Left Side Tree 3":                (113, 352,  2000, "o37_obsA1"),
    "Left Side Tree 4":                (114, 704,  1904, "o37_obsA1"),
    "Left Side Bushes":                (115, 944,  1488, "o37_obsB2"),
}

# teleporter item -> (id offset, teleporter[] index); o37_Teleporter_Create_0 picks n by x
TELEPORTERS: dict[str, tuple[int, int]] = {
    "Left Side Teleporter":  (121, 0),   # pad (1376, 1152)
    "Borlg Area Teleporter": (122, 1),   # pad (2528, 1392)
    "Right Side Teleporter": (123, 2),   # pad (4080, 1136)
    "Top Teleporter":        (124, 3),   # pad (2576, 96)
}


item_table: dict[str, ItemInfo] = {
    "Progressive Resource Cap": ItemInfo(3, IC.progression, NUM_RESOURCE_CAPS),
    "Meat Shack": ItemInfo(4, IC.progression),
    "Gear": ItemInfo(8, IC.progression),
    "Unktomi": ItemInfo(9, IC.progression),
    # all three gate the Ship Fuel (so Gold); x2 Ingots also the ingot ladder's upper rungs
    **{f"x2 {resource}": ItemInfo(offset, IC.progression, NUM_INCOME_DOUBLERS)
       for offset, resource in ((5, "Ingots"), (6, "Research"), (7, "Silk"))},
    "Workbench": ItemInfo(11, IC.progression, NUM_WORKBENCHES),
    "Seed": ItemInfo(12, IC.progression, NUM_SEEDS),
    "x2 Moon Drops": ItemInfo(22, IC.useful, NUM_INCOME_DOUBLERS),
    "-50% Meat Generation Time": ItemInfo(23, IC.useful, 4),
    "Ingot Table": ItemInfo(13, IC.useful),
    "Science Table": ItemInfo(14, IC.useful),
    "Letter": ItemInfo(15, IC.progression),
    "Blaster": ItemInfo(16, IC.progression),  # one of the Cherry weapons
    "x2 Idle Time Multiplier": ItemInfo(20, IC.useful, NUM_IDLE_MULTIPLIERS),
    **{upgrade: ItemInfo(offset, IC.useful, PRESTIGE_LEVELS)
       for offset, upgrade in ((17, "Productivity"), (18, "Defense"), (19, "Metabolism"))},
    "Friend": ItemInfo(21, IC.progression, NUM_FRIENDS),
    # Big Silos is what lets a silo be upgraded (buSilo checks shopBought[2]); the Wizard
    # Yoyo is one of the Cherry weapons
    **{name: ItemInfo(60 + n, IC.progression if name in ("Big Silos", "Wizard Yoyo") else IC.useful)
       for n, name in enumerate(LUMIN_UPGRADES, start=1)},
    **{name: ItemInfo(offset, IC.progression)
       for name, (offset, _x, _y, _obj) in BLOCKS.items()},
    **{name: ItemInfo(offset, IC.progression) for name, (offset, _n) in TELEPORTERS.items()},
    **{name: ItemInfo(offset, IC.filler, 0) for name, offset in FILLERS.items()},
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Dr Lumin Upgrades"] = {f"{GAME_NAME} - {name}" for name in LUMIN_UPGRADES}
    groups[f"{GAME_NAME} - Blocks"] = {f"{GAME_NAME} - {name}" for name in BLOCKS}
    groups[f"{GAME_NAME} - Teleporters"] = {f"{GAME_NAME} - {name}" for name in TELEPORTERS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # every Campsite / Lumin item, block and teleporter; the framework pads
    # the rest with filler
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {world.random.choice(tuple(FILLERS))}"
