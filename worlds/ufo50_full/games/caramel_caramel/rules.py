from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, SHOOTING
from .locations import location_table, sphere_1_locs

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    shooting = f"{GAME_NAME} - {SHOOTING}"

    regions["Menu"].connect(regions["The Shoot"])

    # Sphere 1: the Prologue + the two Snack Planet photo collectibles. Everything else
    # (all level clears, both bosses, the Ghost/Dino letters & wrenches, Gift/Gold/Cherry)
    # needs the Shooting item -- without it the mod destroys player shots so you can
    # photograph but never kill anything.
    sphere1 = set(sphere_1_locs)
    for loc_name in location_table:
        if loc_name in sphere1:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: state.has(shooting, player))
