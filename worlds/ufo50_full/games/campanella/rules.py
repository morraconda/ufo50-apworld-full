from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, HALF_LIFE, LEFT_THRUSTER
from .locations import NUM_STAGES, SCORE_MAX_K, stage_name, coffee_currstages

if TYPE_CHECKING:
    from ... import UFO50World


START_LIVES = 3
GIFT_LIVES = 15   # vanilla global.g03_gardenThresh

# The "1 life per level / per 1000 points" gate is capped here -- past this the
# requirement stays flat -- so the 1/2 Life pool (which needs 2x the items) does not
# blow past the shared multiworld item budget.
LIFE_CAP = 20

# Left Thruster is NOT required for these -- everything else needs it (rules per the
# game's difficulty: only a few World A stages can be flown right/up only).
#   stages: A-1, A-2, A-4, A-Bonus, A-6  (currStage 0, 1, 3, 4, 5)
#   coffee: only the A-1 coffee   /   points: only the 1000 mark
NO_LT_STAGES: frozenset[int] = frozenset({0, 1, 3, 4, 5})

# Coffees on these stages are fully sphere 1 (no life, no Left Thruster): A-1, A-2, A-4.
FREE_COFFEE_STAGES: frozenset[int] = frozenset({0, 1, 3})

_half = f"{GAME_NAME} - {HALF_LIFE}"
_lt = f"{GAME_NAME} - {LEFT_THRUSTER}"


def _lives(state: CollectionState, player: int) -> int:
    # each 1/2 Life is worth half a life -- two make one
    return START_LIVES + state.count(_half, player) // 2


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["Space"])

    def gate(loc_name: str, need_lives: int, need_lt: bool) -> None:
        n = min(need_lives, LIFE_CAP)
        if need_lt:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, n=n: _lives(state, player) >= n and state.has(_lt, player))
        else:
            set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                     lambda state, n=n: _lives(state, player) >= n)

    # stage clears: currStage s -> needs s+1 lives; LT unless it's one of the World A freebies
    for s in range(NUM_STAGES):
        gate(stage_name(s), s + 1, s not in NO_LT_STAGES)

    # coffees: A-1/A-2/A-4 are free; the rest need their stage's lives; LT unless A-1
    for s in coffee_currstages():
        if s in FREE_COFFEE_STAGES:
            continue
        gate(f"{stage_name(s)} - Coffee", s + 1, s != 0)

    # point thresholds: k*1000 -> needs k lives; LT unless it's the 1000 mark
    for k in range(1, SCORE_MAX_K + 1):
        gate(f"{k * 1000} Points", k, k != 1)

    # Gift = 15 spare ships (no LT needed -- it is just a life count). Gold (clear E-Boss)
    # and Cherry (all 40 coffees) both need the full 50-life climb and the Left Thruster.
    gate("Gift", GIFT_LIVES, False)
    gate("Gold", NUM_STAGES, True)
    gate("Cherry", NUM_STAGES, True)
