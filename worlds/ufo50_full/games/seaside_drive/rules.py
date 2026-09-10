from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, PROG_CHARGE

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    charge = f"{GAME_NAME} - {PROG_CHARGE}"

    regions["Menu"].connect(regions["The Drive"])

    # Stage 1 / Stage 2 / Gift are sphere 1. Stage 3 needs 2 Progressive Max Charge,
    # Stage 4 and Gold need 3, Cherry needs all 4.
    for name, needed in {"Stage 3": 2, "Stage 4": 3, "Gold": 3, "Cherry": 4}.items():
        set_rule(world.get_location(f"{GAME_NAME} - {name}"),
                 lambda state, k=needed: state.has(charge, player, k))
