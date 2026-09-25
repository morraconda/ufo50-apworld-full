from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, ENERGY_CUBE, ITEM_SLOT, ZOLDATH_ITEMS
from .locations import (NUM_RANDOM_CHECKS, MAP_TYPES, PIECES_PER_MAP, map_piece_name,
                         ALL_RESOURCE_THRESHOLDS, ANY_RESOURCE_THRESHOLDS,
                         all_resource_name, any_resource_name)

if TYPE_CHECKING:
    from ... import UFO50World


START_HEALTH = 3

_hp = f"{GAME_NAME} - {ENERGY_CUBE}"
_slot = f"{GAME_NAME} - {ITEM_SLOT}"
_translator = f"{GAME_NAME} - Progressive Translator"
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

    # tier 1: nothing required (sphere 1)
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: 1 item slot + 4 items  -> Random Check 9-10, Overworld Map Piece, Gift
    def tier2(state: CollectionState) -> bool:
        return _slots(state, player) >= 1 and _items(state, player) >= 4

    # tier 3: 5 health + 2 item slots + 6 items + Translator -> Trade Map Piece
    def tier3(state: CollectionState) -> bool:
        return (_health(state, player) >= 5 and _slots(state, player) >= 2
                and _items(state, player) >= 6
                and state.has(_translator, player))

    # tier 4: 7 health + 2 item slots + 7 items -> Dungeon Map Piece
    def tier4(state: CollectionState) -> bool:
        return (_health(state, player) >= 7 and _slots(state, player) >= 2
                and _items(state, player) >= 7)

    # tier 5: 8 health + 2 item slots + all 8 items -> Gold / Cherry
    def tier5(state: CollectionState) -> bool:
        return (_health(state, player) >= 8 and _slots(state, player) >= 2
                and _items(state, player) >= len(ZOLDATH_ITEMS))

    # Random Checks by tier: 1-5 tier1, 6-10 tier2.
    for n in range(1, 6):
        rule(f"Random Check {n}", tier1)
    for n in range(6, NUM_RANDOM_CHECKS + 1):
        rule(f"Random Check {n}", tier2)
    rule("Gift", tier2)

    # One map pickup per type (unlocking its pieces one at a time across runs); every
    # piece of a type gates at that pickup's tier.
    map_rule = {"Overworld": tier2, "Trade": tier3, "Dungeon": tier4}
    for mt in MAP_TYPES:
        for p in range(1, PIECES_PER_MAP[mt] + 1):
            rule(map_piece_name(mt, p), map_rule[mt])

    # Resource ladders, by tier.
    all_resource_tier = {1: tier2, 3: tier2, 5: tier3, 10: tier3, 20: tier4, 31: tier5}
    for n in ALL_RESOURCE_THRESHOLDS:
        rule(all_resource_name(n), all_resource_tier[n])

    any_resource_tier = {3: tier1, 5: tier1, 10: tier1, 20: tier2, 30: tier3, 40: tier3, 50: tier4, 63: tier4}
    for n in ANY_RESOURCE_THRESHOLDS:
        rule(any_resource_name(n), any_resource_tier[n])

    rule("Gold", tier5)
    rule("Cherry", tier5)
