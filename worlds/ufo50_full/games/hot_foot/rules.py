from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, JUMPING, STARS

if TYPE_CHECKING:
    from ... import UFO50World


# (needs Jumping, needs Stars) per gated location
_LOC_REQS: dict[str, tuple[bool, bool]] = {
    "Game 3":     (True, False),
    "Game 4":     (True, False),
    "Game 5":     (True, True),
    "Final Game": (True, True),
    "Gift":       (True, False),
    "Gold":       (True, True),
    "Cherry":     (True, True),
}


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    jumping = f"{GAME_NAME} - {JUMPING}"
    stars = f"{GAME_NAME} - {STARS}"

    regions["Menu"].connect(regions["The Tournament"])

    # Game 1 / Game 2 / 10 Points -> nothing (sphere 1)
    for name, (needs_jump, needs_stars) in _LOC_REQS.items():
        reqs: list[str] = []
        if needs_jump:
            reqs.append(jumping)
        if needs_stars:
            reqs.append(stars)
        set_rule(world.get_location(f"{GAME_NAME} - {name}"),
                 lambda state, r=tuple(reqs): all(state.has(item, player) for item in r))
