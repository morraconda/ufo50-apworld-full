from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Velgress"

# The upgrades the Cavian's shop sells. In o15_Game the shuffled shopItems slots map
# to internal counters: values 0/1 -> iRecov, 2/3 -> iGun, 4/5 -> iFoot, 6 -> iMagnet,
# 7 -> iLightning, 8 -> iJump. Recovery / Power / Lightfoot each have two tiers, so
# their items stack x2; Magnet / Lightning are one-shot.
#
# Vanilla starts you with a mid-air jump (o15_Player.doubleJump = 1 + iJump) and the
# shop's jump slot bumps that to a triple jump. Here the mod drops the base to a single
# jump (doubleJump = iJump) and "Progressive Jump" is an x3 progression item -- each copy
# grants one extra mid-air jump. You need one to reach floor 2 and two to reach floor 3
# (rules.py), so it is the one upgrade that actually gates logic; the rest are `useful`.
PROGRESSIVE_JUMP = "Progressive Jump"
UPGRADES: dict[str, tuple[int, int]] = {
    "Recovery": (101, 2),
    "Power": (102, 2),
    "Lightfoot": (103, 2),
    "Magnet": (104, 1),
    "Lightning": (105, 1),
    PROGRESSIVE_JUMP: (106, 3),
}

# "Progressive Gun" stacks on top of the shop's Power (iGun) upgrades -- the mod adds
# get_item_count(107) into iGun, so each copy is another +1 shot damage. x3, progression;
# only Gift and Cherry require it (rules.py).
PROGRESSIVE_GUN = "Progressive Gun"

FILLER = "+5 Coins"  # mod adds 5 to the per-climb coin float per copy received


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(offset, IC.progression if name == PROGRESSIVE_JUMP else IC.useful, qty)
       for name, (offset, qty) in UPGRADES.items()},
    PROGRESSIVE_GUN: ItemInfo(107, IC.progression, 3),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Upgrades"] = {f"{GAME_NAME} - {name}" for name in UPGRADES}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 11 upgrade copies + Progressive Gun into the pool; framework pads with "+5 Coins".
    # The 3rd Progressive Gun only matters for the Cherry check (Gift / Level 2 need
    # just one), so drop it when this game has no Cherry -- otherwise the pool would be
    # one item bigger than the (now Cherry-less) location count.
    overrides = None
    if GAME_NAME not in world.options.cherry_enabled_games.value:
        overrides = {PROGRESSIVE_GUN: 2}
    return _create_items(GAME_NAME, item_table, world, overrides)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
