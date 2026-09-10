from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .locations import GAME_NAME, LEVEL_NAMES, NUM_LEVELS, RANKS, level_name, rank_region

if TYPE_CHECKING:
    from ... import UFO50World


TURN_TIME = f"{GAME_NAME} - +1s Turn Time"
PROMOTION = f"{GAME_NAME} - Promotion"

# The campaign is a linear chain gated by "+1s Turn Time": reaching level N needs
# min(N, ENOUGH_TIME) of them. From level PROMO_LEVEL on you also need the (single)
# Promotion.
PROMO_LEVEL = 7

# The ranked ladder is separate from the campaign and open from the start; from rank
# PROMO_RANK on each milestone also needs the Promotion.
PROMO_RANK = 50

# The base turn timer is 4s and logic assumes every campaign level (and Cherry) is
# beatable at 12s total -- the 4s base plus ENOUGH_TIME "+1s Turn Time" items -- given
# a Promotion. There are 11 "+1s Turn Time" in the pool, so 3 are surplus.
ENOUGH_TIME = 8


def _turn_time(state: CollectionState, player: int) -> int:
    return state.count(TURN_TIME, player)


def _promoted(state: CollectionState, player: int) -> bool:
    return state.has(PROMOTION, player)


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # campaign: Menu -> level 1 -> level 2 -> ... -> level NUM_LEVELS
    for n in range(1, NUM_LEVELS + 1):
        source = regions["Menu"] if n == 1 else regions[level_name(n - 1)]
        needs_promo = n >= PROMO_LEVEL
        source.connect(
            regions[level_name(n)],
            rule=lambda state, lv=min(n, ENOUGH_TIME), promo=needs_promo:
            _turn_time(state, player) >= lv and (not promo or _promoted(state, player)))

    # ranked ladder: Menu -> Rank 10 -> Rank 20 -> ... -> Rank 100 (open from the start,
    # only Promotion-gated from rank 50)
    for i, r in enumerate(RANKS):
        source = regions["Menu"] if i == 0 else regions[rank_region(RANKS[i - 1])]
        needs_promo = r >= PROMO_RANK
        source.connect(
            regions[rank_region(r)],
            rule=lambda state, promo=needs_promo: not promo or _promoted(state, player))

    # Cherry location (vanilla scrWin(2)) additionally needs the whole campaign beaten,
    # not just rank 100 -- same bar as the deepest campaign level.
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: _turn_time(state, player) >= ENOUGH_TIME and _promoted(state, player))
