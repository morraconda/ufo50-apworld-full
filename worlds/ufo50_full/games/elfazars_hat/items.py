from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Elfazar's Hat"

# Elfazar's Hat is a top-down 8-direction shooter (o31_Player, rm31_Elfazar_lv1..5).
# The player aims where they move (dirAim = scr8dir(...), GML angles 0/45/90/.../315)
# and can dash (fire2pressed -> STATE_TORNADO). The mod starts you able to shoot UP
# (dirAim == 90) only, and locks the other seven aim directions plus the dash until
# their item is held -- which is what gates the region chain (see rules.py):
#   Shoot Right       (501)  dirAim == 0    \
#   Shoot Left        (502)  dirAim == 180   > the three non-up cardinals + Dash open
#   Shoot Down        (503)  dirAim == 270  /  the Cardinal Zone (stages 3 & 4)
#   Dash              (508)  fire2pressed  /
#   Shoot Up-Right    (504)  dirAim == 45   \
#   Shoot Up-Left     (505)  dirAim == 135   > the four diagonals open the Demon Tower
#   Shoot Down-Right  (506)  dirAim == 315   /  (stage 5, Gold, Cherry)
#   Shoot Down-Left   (507)  dirAim == 225  /
SHOOT_RIGHT = "Shoot Right"
SHOOT_LEFT = "Shoot Left"
SHOOT_DOWN = "Shoot Down"
SHOOT_UP_RIGHT = "Shoot Up-Right"
SHOOT_UP_LEFT = "Shoot Up-Left"
SHOOT_DOWN_RIGHT = "Shoot Down-Right"
SHOOT_DOWN_LEFT = "Shoot Down-Left"
DASH = "Dash"
FILLER = "Encouragement"

CARDINALS = (SHOOT_RIGHT, SHOOT_LEFT, SHOOT_DOWN, DASH)
DIAGONALS = (SHOOT_UP_RIGHT, SHOOT_UP_LEFT, SHOOT_DOWN_RIGHT, SHOOT_DOWN_LEFT)
ABILITIES = CARDINALS + DIAGONALS

# The nine hidden tickets (o31_Ticket): shoot one to unveil it, walk over it to bank
# it (global.g31_ticketsFound). Vanilla, bringing a ticket to the casino minigame is
# what fires the Gift/Garden goal, so the Gift location needs one Ticket item here.
TICKET = "Ticket"
TICKET_COUNT = 9


item_table: dict[str, ItemInfo] = {
    SHOOT_RIGHT: ItemInfo(501, IC.progression, 1),
    SHOOT_LEFT: ItemInfo(502, IC.progression, 1),
    SHOOT_DOWN: ItemInfo(503, IC.progression, 1),
    SHOOT_UP_RIGHT: ItemInfo(504, IC.progression, 1),
    SHOOT_UP_LEFT: ItemInfo(505, IC.progression, 1),
    SHOOT_DOWN_RIGHT: ItemInfo(506, IC.progression, 1),
    SHOOT_DOWN_LEFT: ItemInfo(507, IC.progression, 1),
    DASH: ItemInfo(508, IC.progression, 1),
    TICKET: ItemInfo(509, IC.progression, TICKET_COUNT),
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Abilities"] = {f"{GAME_NAME} - {n}" for n in ABILITIES}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 8 ability items + 9 Ticket items go in the pool; framework pads with Encouragement
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
