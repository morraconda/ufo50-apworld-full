from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .locations import GAME_NAME, LEVEL_NAMES, NUM_LEVELS, RANKS, level_name, rank_region

if TYPE_CHECKING:
    from ... import UFO50World


TURN_TIME = f"{GAME_NAME} - +1s Turn Time"
PROMOTION = f"{GAME_NAME} - Promotion"

# The campaign is a linear chain gated by "+1s Turn Time": reaching level N needs N
# of them. From level PROMO_LEVEL on you also need the (single) Promotion.
PROMO_LEVEL = 7

# The ranked ladder is separate from the campaign and open from the start; from rank
# PROMO_RANK on each milestone also needs the Promotion.
PROMO_RANK = 50

# Escape hatch: with a 15s turn timer (the 4s base plus ENOUGH_TIME "+1s Turn Time"
# items) and a Promotion, logic assumes every campaign level is beatable regardless
# of the per-level turn-time count -- so everything is reachable.
ENOUGH_TIME = 11


def _turn_time(state: CollectionState, player: int) -> int:
    return state.count(TURN_TIME, player)


def _promoted(state: CollectionState, player: int) -> bool:
    return state.has(PROMOTION, player)


def _anything(state: CollectionState, player: int) -> bool:
    return _turn_time(state, player) >= ENOUGH_TIME and _promoted(state, player)


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # campaign: Menu -> level 1 -> level 2 -> ... -> level NUM_LEVELS
    for n in range(1, NUM_LEVELS + 1):
        source = regions["Menu"] if n == 1 else regions[level_name(n - 1)]
        needs_promo = n >= PROMO_LEVEL
        source.connect(
            regions[level_name(n)],
            rule=lambda state, lv=n, promo=needs_promo:
            (_turn_time(state, player) >= lv and (not promo or _promoted(state, player)))
            or _anything(state, player))

    # ranked ladder: Menu -> Rank 10 -> Rank 20 -> ... -> Rank 100 (already looser than
    # the escape hatch, so no _anything clause needed here)
    for i, r in enumerate(RANKS):
        source = regions["Menu"] if i == 0 else regions[rank_region(RANKS[i - 1])]
        needs_promo = r >= PROMO_RANK
        source.connect(
            regions[rank_region(r)],
            rule=lambda state, promo=needs_promo: not promo or _promoted(state, player))

    # Cherry check (vanilla scrWin(2)) additionally needs the whole campaign beaten, not
    # just rank 100.
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: (_turn_time(state, player) >= NUM_LEVELS and _promoted(state, player))
             or _anything(state, player))
