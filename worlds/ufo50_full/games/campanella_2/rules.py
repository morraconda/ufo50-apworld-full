from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState

from .items import MAX_HP, MAX_FUEL, COIN_MULT

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 2"

# A run starts with these; every received item raises them.
BASE_MAX_HP = 5
BASE_MAX_FUEL = 700
HP_PER_ITEM = 1
FUEL_PER_ITEM = 100

# World A (Burrows) is sphere 1. Each later world needs a bigger loadout to survive:
#   (max HP, max fuel, number of +20% Coin Multiplier items)
WORLD_REQUIREMENTS: dict[str, tuple[int, int, int]] = {
    "B": (8, 800, 0),     # 3x HP, 1x Fuel
    "C": (10, 1000, 1),   # 5x HP, 3x Fuel, coin multiplier >= x1.2
    "D": (12, 1200, 2),   # 7x HP, 5x Fuel, coin multiplier >= x1.4
}
WORLD_CHAIN: list[str] = ["A", "B", "C", "D"]


def _max_hp(state: CollectionState, player: int) -> int:
    return BASE_MAX_HP + HP_PER_ITEM * state.count(f"{GAME_NAME} - {MAX_HP}", player)


def _max_fuel(state: CollectionState, player: int) -> int:
    return BASE_MAX_FUEL + FUEL_PER_ITEM * state.count(f"{GAME_NAME} - {MAX_FUEL}", player)


def _meets(state: CollectionState, player: int, hp: int, fuel: int, coin_items: int) -> bool:
    return (_max_hp(state, player) >= hp
            and _max_fuel(state, player) >= fuel
            and state.count(f"{GAME_NAME} - {COIN_MULT}", player) >= coin_items)


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["A"])

    # A -> B -> C -> D: each requirement strictly dominates the previous, so the chain
    # is monotonic (reaching D implies B and C were satisfied).
    for prev, nxt in zip(WORLD_CHAIN, WORLD_CHAIN[1:]):
        hp, fuel, coin_items = WORLD_REQUIREMENTS[nxt]
        regions[prev].connect(
            regions[nxt],
            rule=lambda state, _hp=hp, _fuel=fuel, _coins=coin_items:
            _meets(state, player, _hp, _fuel, _coins))
