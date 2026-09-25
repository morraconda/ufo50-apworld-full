from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .items import THROTTLE, HANDBRAKE, TOP_SPEED
from .locations import NUM_DAY, NUM_ONION, onion_loc_name, DELIVERY_STOPS, SPHERE_1_STOPS

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Onion Delivery"

_throttle = f"{GAME_NAME} - {THROTTLE}"
_handbrake = f"{GAME_NAME} - {HANDBRAKE}"
_top_speed = f"{GAME_NAME} - {TOP_SPEED}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["The Route"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # tier 1: nothing required (sphere 1) -> Onions 1-5, Day 1-2, the 5 SPHERE_1_STOPS
    # (Burlett Bakery, Onion Park, Laydon Papers, Cheap Storage, 24/7 Juicery), Gift
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: Throttle + 2 Progressive Top Speed -> Onions 6-7, Day 3-4, every other stop
    def tier2(state: CollectionState) -> bool:
        return state.has(_throttle, player) and state.has(_top_speed, player, 2)

    # tier 3: Throttle + Handbrake + 4 Progressive Top Speed -> Onions 8-10, Day 5-7, Gold, Cherry
    def tier3(state: CollectionState) -> bool:
        return state.has_all((_throttle, _handbrake), player) and state.has(_top_speed, player, 4)

    onion_tier = {range(1, 6): tier1, range(6, 8): tier2, range(8, NUM_ONION + 1): tier3}
    for onions, tier in onion_tier.items():
        for n in onions:
            rule(onion_loc_name(n), tier)

    for stop in DELIVERY_STOPS.values():
        rule(stop, tier1 if stop in SPHERE_1_STOPS else tier2)

    day_tier = {range(1, 3): tier1, range(3, 5): tier2, range(5, NUM_DAY + 1): tier3}
    for days, tier in day_tier.items():
        for n in days:
            rule(f"Day {n}", tier)

    rule("Gift", tier1)
    rule("Gold", tier3)
    rule("Cherry", tier3)
