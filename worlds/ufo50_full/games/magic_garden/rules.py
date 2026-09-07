from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Magic Garden"

POTION = f"{GAME_NAME} - Progressive Potion"
OPPY = f"{GAME_NAME} - +1 Starting Red Oppy"

# A run starts with one red oppy and no potions. "Progressive Potion" x4 unlock
# progressively stronger brews; "+1 Starting Red Oppy" x4 each add an oppy to the
# field at the start of a run. "Cloverana's Love" is the (nothing) filler item.
#
# Tiers:
#   sphere 1                                : Garden, 15 Oppies Saved
#   any non-filler location (>=1 potion or  : 30 Oppies Saved, 1000 Score
#                         >=1 starting oppy)
#   >=1 potion AND (>=2 starting oppy OR    : 50 Oppies Saved, 8x Multiplier,
#                   all 4 potions)            5000 Score
#   all 4 potions                          : 100 Oppies Saved, 150 Oppies Saved,
#                                            10000 Score, Gold, Cherry

_SPHERE_TWO_LOCS = ("30 Oppies Saved", "1000 Score")
_MID_TIER_LOCS = ("50 Oppies Saved", "8x Multiplier", "5000 Score")
_TOP_TIER_LOCS = ("100 Oppies Saved", "150 Oppies Saved", "10000 Score", "Gold", "Cherry")


def potions(state: CollectionState, player: int) -> int:
    return state.count(POTION, player)


def starting_oppies(state: CollectionState, player: int) -> int:
    return state.count(OPPY, player)


def any_progression(state: CollectionState, player: int) -> bool:
    return state.has_any((POTION, OPPY), player)


def has_all_potions(state: CollectionState, player: int) -> bool:
    return potions(state, player) >= 4


def mid_tier(state: CollectionState, player: int) -> bool:
    return potions(state, player) >= 1 and (starting_oppies(state, player) >= 2 or has_all_potions(state, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["Field"])

    for loc_name in _SPHERE_TWO_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: any_progression(state, player))

    for loc_name in _MID_TIER_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: mid_tier(state, player))

    for loc_name in _TOP_TIER_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: has_all_potions(state, player))
