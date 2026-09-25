from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .items import MAX_CHARGE, MAX_FISH, MAX_PUFFIN

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"

_upgrades = tuple(f"{GAME_NAME} - {name}" for name in (MAX_CHARGE, MAX_FISH, MAX_PUFFIN))


def _upgrades_each(state: CollectionState, player: int, n: int) -> bool:
    return all(state.has(item, player, n) for item in _upgrades)


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["Island"])

    def rule(loc_name: str, fn) -> None:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"), fn)

    # The numbered checks are cumulative counts across runs. Each tier needs copies of
    # EACH of Progressive Max Charge, Progressive Max Fish and +1 Max Puffin.
    # tier 1: nothing required (sphere 1) -> Sign / Weather Vane 1-3, Gift
    def tier1(state: CollectionState) -> bool:
        return True

    # tier 2: 1 of each upgrade -> Sign / Weather Vane 4-6, Chest 1-2
    def tier2(state: CollectionState) -> bool:
        return _upgrades_each(state, player, 1)

    # tier 3: 2 of each upgrade -> Sign / Weather Vane 7-10, Chest 3-4, Gold
    def tier3(state: CollectionState) -> bool:
        return _upgrades_each(state, player, 2)

    # tier 4: 3 of each upgrade -> Chest 5-6, Cherry
    def tier4(state: CollectionState) -> bool:
        return _upgrades_each(state, player, 3)

    # Signs and Weather Vanes share a ladder: 1-3 tier1, 4-6 tier2, 7-10 tier3.
    count_tier = {range(1, 4): tier1, range(4, 7): tier2, range(7, 11): tier3}
    for counts, tier in count_tier.items():
        for n in counts:
            rule(f"Sign {n}", tier)
            rule(f"Weather Vane {n}", tier)

    # Chests by tier: 1-2 tier2, 3-4 tier3, 5-6 tier4 (no chest is free).
    chest_tier = {range(1, 3): tier2, range(3, 5): tier3, range(5, 7): tier4}
    for chests, tier in chest_tier.items():
        for n in chests:
            rule(f"Chest {n}", tier)

    rule("Gift", tier1)
    rule("Gold", tier3)
    rule("Cherry", tier4)
