from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import MAX_CHARGE, MAX_FISH, NUM_UPGRADES

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Waldorf's Journey"

# The checks are cumulative counts, split evenly across three tiers. Tier N needs
# N-1 copies of BOTH Progressive Max Charge and Progressive Max Fish.
# Chests: 1-2 / 3-4 / 5-6.  Signs: 1-4 / 5-7 / 8-10 (the extra sign goes to tier 1).
CHEST_TIERS: list[range] = [range(1, 3), range(3, 5), range(5, 7)]
SIGN_TIERS: list[range] = [range(1, 5), range(5, 8), range(8, 11)]


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    regions["Menu"].connect(regions["Island"])
    player = world.player
    charge, fish = f"{GAME_NAME} - {MAX_CHARGE}", f"{GAME_NAME} - {MAX_FISH}"

    def needs(n: int):
        return lambda state: state.has(charge, player, n) and state.has(fish, player, n)

    for tier, (chests, signs) in enumerate(zip(CHEST_TIERS, SIGN_TIERS)):
        if tier == 0:
            continue
        for n in chests:
            set_rule(world.get_location(f"{GAME_NAME} - Chest {n}"), needs(tier))
        for n in signs:
            set_rule(world.get_location(f"{GAME_NAME} - Sign {n}"), needs(tier))

    # Gold / Cherry need every upgrade.
    for goal in ("Gold", "Cherry"):
        set_rule(world.get_location(f"{GAME_NAME} - {goal}"), needs(NUM_UPGRADES))
