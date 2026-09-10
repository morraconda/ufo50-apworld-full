from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    # simple implementation: every location (silos, workbenches, houses, ship parts,
    # letter, blaster, bosses, Dr Lumin upgrades, chests, teleporters, Gift/Gold/Cherry)
    # is sphere 1 -- no item gating
    regions["Menu"].connect(regions["Pilot Quest"])
