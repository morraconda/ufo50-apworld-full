from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 3"

# Campanella 3 is a five-stage rail shmup (o08_Mas). The o08_Ufo has two weapons: a
# forward pellet shot (fire1 -> o08_UfoShot, mirrored by Isabell) and an aimed beam
# (fire2 -> o08_UfoBeam, direction = dirAim: 0 right / 90 up / 180 left / 270 down).
# The mod disables each direction until its item is held, which gates the region chain
# (see rules.py):
#   Forward Shot   (511)  fire1 pellet -- needed past Stage A's waves (everything but A1-4)
#   Upward Beam    (512)  fire2 beam, dirAim == 90  -- Eggsaber, Queen Zu, all of world E
#   Right Beam     (513)  fire2 beam, dirAim == 0   \
#   Left Beam      (514)  fire2 beam, dirAim == 180  > all three needed for Gold / Cherry
#   Down Beam      (515)  fire2 beam, dirAim == 270 /
FORWARD_SHOT = "Forward Shot"
UPWARD_BEAM = "Upward Beam"
RIGHT_BEAM = "Right Beam"
LEFT_BEAM = "Left Beam"
DOWN_BEAM = "Down Beam"
FILLER = "Encouragement"

WEAPONS = (FORWARD_SHOT, UPWARD_BEAM, RIGHT_BEAM, LEFT_BEAM, DOWN_BEAM)


item_table: dict[str, ItemInfo] = {
    FORWARD_SHOT: ItemInfo(511, IC.progression, 1),
    UPWARD_BEAM: ItemInfo(512, IC.progression, 1),
    RIGHT_BEAM: ItemInfo(513, IC.progression, 1),
    LEFT_BEAM: ItemInfo(514, IC.progression, 1),
    DOWN_BEAM: ItemInfo(515, IC.progression, 1),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Weapons"] = {f"{GAME_NAME} - {n}" for n in WEAPONS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # the 5 weapon items go in the pool; the framework pads the rest with Encouragement
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
