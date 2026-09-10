from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mini & Max"

# Mini & Max is a big shrinking adventure: the storage room (Regular) shrinks to the
# 8x5 grid of the Small world (vanilla calls each cell an "atom"), and each cell can
# shrink again into a Micro world where the NPC factions live. Here each cell is a
# "shrink region".
#
# Items handed out here:
#   * every player-facing upgrade (o41 `UP_*`; the hidden `UP_SMELL` is left out),
#     named as the game names it (ext/ENGLISH/41_Text.json `up_*_name`). The seven
#     two-level upgrades become a Progressive item (x2); the nine one-level ones are a
#     single. The mod drives `global.mmUpgrades[i]` straight off get_item_count.
#   * 40 shrink-region gates -- one per cell of the 8x5 Small grid. The gate item shares
#     its name with the shrink region it opens; that name is the grid ref RrCc where
#     there is no established landmark (r = 1..5 top->floor, c = 1..8 left->right).
#     Without a shrink region's gate you cannot shrink to Micro there, and you cannot
#     walk into that region while doubly shrunk. This replaces the vanilla single Super
#     Shrink unlock as the thing that opens Micro, per shrink region.
#   * "Mittens' Gate" -- opens King Mittens' gate in the Doorknob kingdom (vanilla opens
#     it after beating GearFace).
#   * "Launch Codes" -- the Central Computer password (vanilla `EVENT_GOT_PASSWORD`).
#
# Progression items: Progressive Magic Potion (needed to do anything past sphere 1, and
# both copies for Gold/Cherry), Progressive Protein (both copies for Gold/Cherry), Dog
# Armor (Gold/Cherry), Mittens' Gate, Launch Codes, and all 40 shrink-region gates.
# Every other upgrade is purely `useful`.
#
# Micro-world item pickups are removed by the mod -- upgrades only ever arrive as checks.

# name -> (id offset, in-game UP_* index). Two in-game levels each -> Progressive, qty 2.
# Names are the level-1 `up_*_name` string from 41_Text.json.
PROGRESSIVE_UPGRADES: dict[str, tuple[int, int]] = {
    "Progressive Magic Potion":  (101, 1),   # UP_SUPERSHRINK       "MAGIC POTION"
    "Progressive Protein":       (102, 4),   # UP_HIGHERJUMP        "PROTEIN"
    "Progressive Glove":         (103, 0),   # UP_PICKUPSPEED       "GLOVE"
    "Progressive Backpack":      (104, 3),   # UP_BACKPACK          "BACKPACK"
    "Progressive Boots":         (105, 6),   # UP_KICK              "BOOTS"
    "Progressive Old Book":      (106, 8),   # UP_CONTROLCREATURES  "OLD BOOK"
    "Progressive Spin Bauble":   (107, 10),  # UP_FLIP              "SPIN BAUBLE"
}

# name -> (id offset, in-game UP_* index). One in-game level each -> single, qty 1.
SINGLE_UPGRADES: dict[str, tuple[int, int]] = {
    "Special Anklet":  (111, 2),    # UP_DROPDOWN      "SPECIAL ANKLET"
    "Gravity Charm":   (112, 5),    # UP_SURVIVEFALL   "GRAVITY CHARM"
    "Pheromone":       (113, 7),    # UP_BUGSAFE       "PHEROMONE"
    "Coffee Ground":   (114, 9),    # UP_SPRINT        "COFFEE GROUND"
    "Chitin Armor":    (115, 11),   # UP_CHITIN        "CHITIN ARMOR"
    "Whistle":         (116, 12),   # UP_WHISTLE       "WHISTLE"
    "Mol Dok Food":    (117, 13),   # UP_IMMUNE        "MOL DOK FOOD"
    "Dog Armor":       (118, 14),   # UP_ARMOR         "DOG ARMOR"
    "Sacred Wings":    (119, 15),   # UP_WINGS         "SACRED WINGS"
}

PROGRESSIVE_SHRINK = "Progressive Magic Potion"
PROGRESSIVE_HIGHER_JUMP = "Progressive Protein"
PROGRESSIVE_GLOVE = "Progressive Glove"
ARMOR = "Dog Armor"
MITTENS_GATE = "Mittens' Gate"
LAUNCH_CODES = "Launch Codes"

# EVERY upgrade counts toward logic now -- the shiny thresholds are gated on the
# "Mini & Max - Upgrades" group count (2 per 100 shinies, rules.py), and has_group only
# sees advancement items. The four hard-gate upgrades (needed for a specific region or
# the goal) are full `progression`; the rest are `progression_skip_balancing` so they
# count in logic without distorting item balancing.
_HARD_GATE_UPGRADES = {PROGRESSIVE_SHRINK, PROGRESSIVE_HIGHER_JUMP, PROGRESSIVE_GLOVE, ARMOR}

# total upgrade item copies in the pool (7 progressive x2 + 9 single) -- the cap for
# the shiny gate so the top thresholds stay reachable.
TOTAL_UPGRADE_COPIES = 2 * len(PROGRESSIVE_UPGRADES) + len(SINGLE_UPGRADES)

# The 8x5 grid, row 1..5 (GRID_ROWS, R1 top -> R5 floor) x column 1..8 (GRID_COLS,
# C1 left -> C8 right). id offset for a cell = 200 + (row - 1) * 8 + (col - 1).
GRID_ROWS = 5
GRID_COLS = 8

# ONLY the named grid cells are gated shrink regions -- each is one AP region and its
# gate item shares that name. The other 17 cells have no gate and no region: you can
# shrink to Micro there freely (the mod's ap41_micro_access whitelists these ids).
# Keys are region name == gate item name; value is 200 + atomY*8 + atomX.
SHRINK_REGION_IDS: dict[str, int] = {
    "Top Left":                  200,   # R1C1
    "Clock":                     203,   # R1C4  (Cherry ending is reached from here)
    "Lamptopian Proving Ground": 206,   # R1C7
    "Top Right":                 207,   # R1C8
    "Lamptopia":                 209,   # R2C2
    "Portrait":                  210,   # R2C3
    "Top Shelf Left":            212,   # R2C5
    "Top Shelf Right":           213,   # R2C6  (Moldovia entrance)
    "Third Shelf Left":          220,   # R3C5
    "Third Shelf Right":         221,   # R3C6
    "West Pot":                  224,   # R4C1
    "East Pot":                  226,   # R4C3
    "Pig":                       228,   # R4C5  (the piggy bank)
    "Silverfish Books":          229,   # R4C6
    "Doorknob":                  231,   # R4C8  (King Mittens' kingdom -- verified:
                                        #        scr41_GetZone ZONE_DOORKNOB = InAtom(7,3);
                                        #        shrinking here goes to rm41_MicroGearHead)
    "West Pot Base":             232,   # R5C1
    "Left Outlet":               233,   # R5C2
    "East Pot Base":             234,   # R5C3
    "Dust Bunnies":              235,   # R5C4
    "Angel":                     236,   # R5C5
    "Train":                     237,   # R5C6
    "Eleanor's House":           238,   # R5C7
    "Right Outlet":              239,   # R5C8
}

# region / gate-item names in row-major order (== SHRINK_REGION_IDS keys)
SHRINK_REGION_NAMES: list[str] = list(SHRINK_REGION_IDS)


FILLER = "+5 Shinies"


def _upgrade_class(name: str) -> IC:
    return IC.progression if name in _HARD_GATE_UPGRADES else IC.progression_skip_balancing


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(offset, _upgrade_class(name), 2)
       for name, (offset, _idx) in PROGRESSIVE_UPGRADES.items()},
    **{name: ItemInfo(offset, _upgrade_class(name), 1)
       for name, (offset, _idx) in SINGLE_UPGRADES.items()},
    MITTENS_GATE: ItemInfo(130, IC.progression, 1),
    LAUNCH_CODES: ItemInfo(131, IC.progression, 1),
    **{name: ItemInfo(offset, IC.progression, 1) for name, offset in SHRINK_REGION_IDS.items()},
    FILLER: ItemInfo(300, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Upgrades"] = {
        f"{GAME_NAME} - {name}"
        for name in (*PROGRESSIVE_UPGRADES, *SINGLE_UPGRADES)
    }
    groups[f"{GAME_NAME} - Shrink Regions"] = {
        f"{GAME_NAME} - {name}" for name in SHRINK_REGION_IDS
    }
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 14 progressive-upgrade copies + 9 single upgrades + Mittens' Gate + Launch Codes
    # into the pool; the framework pads the rest with "+5 Shinies" filler.
    #
    # TEMP: start with every shrink-region gate precollected (all regions unlocked from
    # the boot). Drop the precollect + the quantity_overrides to shuffle them back in.
    for name in SHRINK_REGION_IDS:
        world.multiworld.push_precollected(create_item(name, world))
    return _create_items(GAME_NAME, item_table, world,
                         quantity_overrides={name: 0 for name in SHRINK_REGION_IDS})


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
