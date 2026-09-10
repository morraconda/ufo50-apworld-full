from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, SHURIKEN, SHURIKEN_COUNT
from .locations import SCORE_STEP, NUM_STEPS, shuriken_needed

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    shuriken = f"{GAME_NAME} - {SHURIKEN}"

    regions["Menu"].connect(regions["The Run"])

    # Gold / Cherry sit in "Deep Run", behind every Shuriken (you cannot shoot without
    # one, and beating the game needs the full arsenal).
    regions["The Run"].connect(
        regions["Deep Run"],
        rule=lambda state: state.has(shuriken, player, SHURIKEN_COUNT))

    # Score milestones: 5,000 is free (pickups / bonuses, no shooting); every 10,000
    # above that needs one more Shuriken, capped at the 5 in the pool.
    for n in range(1, NUM_STEPS + 1):
        need = min(shuriken_needed(n * SCORE_STEP), SHURIKEN_COUNT)
        if need <= 0:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {n * SCORE_STEP} Points"),
                 lambda state, k=need: state.has(shuriken, player, k))
