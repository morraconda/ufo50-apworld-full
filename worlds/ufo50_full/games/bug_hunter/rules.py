from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, MODULES, SHOP_SLOTS, MAX_ENERGY
from .locations import ENERGY_CHECKS, STARTING_MAX_ENERGY

if TYPE_CHECKING:
    from ... import UFO50World


_hand_items = tuple(f"{GAME_NAME} - {name}" for name in MODULES)
_shop_items = tuple(f"{GAME_NAME} - {name}" for name in SHOP_SLOTS)
_max_energy = f"{GAME_NAME} - {MAX_ENERGY}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # job 1's 2 / 4 / 6 kills are sphere 1
    regions["Menu"].connect(regions["Warmup"])
    # beating job 1 (and its 8 / 10 / 20 kills, Gift) needs Module 6 + Module 7
    regions["Warmup"].connect(regions["Job 1"],
                              rule=lambda state: state.has_all(_hand_items, player))
    # anything past job 1 (Gold, Cherry) also needs any 2 of Shop Slot 1..3
    regions["Job 1"].connect(regions["The Hunt"],
                             rule=lambda state: state.has_from_list_unique(_shop_items, player, 2))

    # <X> Energy needs an energy cap of at least X (5 + one per +1 Max Energy); 1..5 are
    # sphere 1
    regions["Menu"].connect(regions["Energy"])
    for x in range(STARTING_MAX_ENERGY + 1, ENERGY_CHECKS + 1):
        world.get_location(f"{GAME_NAME} - {x} Energy").access_rule = (
            lambda state, need=x - STARTING_MAX_ENERGY: state.has(_max_energy, player, need))
