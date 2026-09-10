from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, ENERGY_CUBE, ITEM_SLOT, ZOLDATH_ITEMS
from .locations import MAP_TYPES, PIECES_PER_MAP, map_piece_name

if TYPE_CHECKING:
    from ... import UFO50World


START_HEALTH = 3

_hp = f"{GAME_NAME} - {ENERGY_CUBE}"
_slot = f"{GAME_NAME} - {ITEM_SLOT}"
_translator = f"{GAME_NAME} - Translator"
_equipment = tuple(f"{GAME_NAME} - {name}" for name in ZOLDATH_ITEMS)


def _health(state: CollectionState, player: int) -> int:
    return START_HEALTH + state.count(_hp, player)


def _slots(state: CollectionState, player: int) -> int:
    return state.count(_slot, player)


def _items(state: CollectionState, player: int) -> int:
    return sum(1 for e in _equipment if state.has(e, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["The Planet"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # tier 2: 1 item slot + 4 items  -> Random Check 7-9, Overworld Map Piece, Gift
    def tier2(state: CollectionState) -> bool:
        return _slots(state, player) >= 1 and _items(state, player) >= 4

    # tier 3: 5 health + 2 item slots + 6 items + Translator -> RC 10-12, Trade Map Piece
    def tier3(state: CollectionState) -> bool:
        return (_health(state, player) >= 5 and _slots(state, player) >= 2
                and _items(state, player) >= 6
                and state.has(_translator, player))

    # tier 4: 7 health + 2 item slots + 7 items -> RC 13-15, Dungeon Map Piece
    def tier4(state: CollectionState) -> bool:
        return (_health(state, player) >= 7 and _slots(state, player) >= 2
                and _items(state, player) >= 7)

    # goal: 8 health + 3 item slots + all 8 items -> Gold / Cherry
    def goal(state: CollectionState) -> bool:
        return (_health(state, player) >= 8 and _slots(state, player) >= 3
                and _items(state, player) >= len(ZOLDATH_ITEMS))

    # Random Checks by tier: 1-6 free (sphere 1), 7-9 tier2, 10-12 tier3, 13-15 tier4.
    # (Energy cubes past the 15th are just heals -- see the mod.)
    for n in range(7, 10):
        rule(f"Random Check {n}", tier2)
    rule("Gift", tier2)

    for n in range(10, 13):
        rule(f"Random Check {n}", tier3)

    for n in range(13, 16):
        rule(f"Random Check {n}", tier4)

    # One map pickup per type (unlocking its 3 pieces one at a time across runs); every
    # piece of a type gates at that pickup's tier.
    map_rule = {"Overworld": tier2, "Trade": tier3, "Dungeon": tier4}
    for mt in MAP_TYPES:
        for p in range(1, PIECES_PER_MAP + 1):
            rule(map_piece_name(mt, p), map_rule[mt])

    rule("Gold", goal)
    rule("Cherry", goal)
