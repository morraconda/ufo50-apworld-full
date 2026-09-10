from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME
from .locations import (NUM_ROUNDS, VILLAGER_ROUND, round_requirements,
                        villager_loc_name)

if TYPE_CHECKING:
    from ... import UFO50World


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["The Village"])

    def _rule(reqs):
        items = tuple((_g(name), cnt) for name, cnt in reqs)
        return lambda state: all(state.has(it, player, c) for it, c in items)

    # Round n: (n-1) "+15 Pieces", plus "Tier 1 Pieces" from round 4 on.
    for n in range(1, NUM_ROUNDS + 1):
        reqs = round_requirements(n)
        if reqs:
            set_rule(world.get_location(_g(f"Round {n}")), _rule(reqs))

    # "<v> Villagers" borrows its tied round's requirements.
    for v, r in VILLAGER_ROUND.items():
        reqs = round_requirements(r)
        if reqs:
            set_rule(world.get_location(_g(villager_loc_name(v))), _rule(reqs))

    # Gift is level-5 logic.
    set_rule(world.get_location(_g("Gift")), _rule(round_requirements(5)))

    # Gold / Cherry (in "Endgame") need everything round 10 needs.
    regions["The Village"].connect(regions["Endgame"], rule=_rule(round_requirements(NUM_ROUNDS)))
