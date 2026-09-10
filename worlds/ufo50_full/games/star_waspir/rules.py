from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, SHOOTING
from .locations import NUM_WAVE, UNIT

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    shooting = f"{GAME_NAME} - {SHOOTING}"

    regions["Menu"].connect(regions["Sortie"])

    # Wave 1 is sphere 1; every other check (Wave 2..5, Gift, Gold, Cherry) needs the
    # Shooting item -- without it the mod destroys player shots and auto-clears wave 1.
    gated = [f"{UNIT} {n}" for n in range(2, NUM_WAVE + 1)] + ["Gift", "Gold", "Cherry"]
    for name in gated:
        set_rule(world.get_location(f"{GAME_NAME} - {name}"),
                 lambda state: state.has(shooting, player))
