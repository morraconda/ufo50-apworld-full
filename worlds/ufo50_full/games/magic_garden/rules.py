from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Magic Garden"

POTION = f"{GAME_NAME} - Progressive Potion"
OPPY = f"{GAME_NAME} - +1 Starting Red Oppy"
POTION_TIME = f"{GAME_NAME} - Progressive Potion Time"
JUMP = f"{GAME_NAME} - Jump"

# A run starts with one red oppy and no potions. "Progressive Potion" x6 unlock
# progressively stronger brews (only 4 tiers, so copies 5-6 do nothing);
# "+1 Starting Red Oppy" x4 each add an oppy to the field at the start of a run;
# "Progressive Potion Time" x10 lengthen a potion's eating frenzy from 20 (on the
# in-game counter) by +5 each -- 6 copies = 50, just past vanilla's 48. Potion Time is
# also the filler item; copies beyond what logic needs are harmless. "Jump" x1 unlocks
# the jump button (only logically required for the top tier).
#
# Oppies-Saved checks sit every 10 from 10 to 200; each takes the tier of the next
# old checkpoint at or above it (the old ladder was 15 / 30 / 50 / 100 / 150).
#
# Tiers (potion-time counts ramp up so solo Magic Garden always has room to place them):
#   sphere 1                                : Gift, 10 Oppies Saved
#   >=1 potion or >=1 starting oppy         : 20 / 30 Oppies Saved
#   >=1 potion AND (>=2 starting oppy OR    : 40 / 50 Oppies Saved, 8x Multiplier,
#     all 4 potions)                          1000..5000 Score
#   all 4 potions AND >=2 potion time       : 60..100 Oppies Saved
#   all 4 potions AND >=6 potion time       : 110..200 Oppies Saved, 10000 / 15000 /
#     AND Jump                                20000 Score, Gold, Cherry

_SPHERE_TWO_LOCS = ("20 Oppies Saved", "30 Oppies Saved")
_MID_TIER_LOCS = ("40 Oppies Saved", "50 Oppies Saved", "8x Multiplier",
                  *(f"{n} Score" for n in range(1000, 5001, 1000)))
_HIGH_TIER_LOCS = tuple(f"{n} Oppies Saved" for n in range(60, 101, 10))
_TOP_TIER_LOCS = (*(f"{n} Oppies Saved" for n in range(110, 201, 10)), "10000 Score", "15000 Score", "20000 Score",
                  "Gold", "Cherry")

HIGH_TIER_POTION_TIME = 2
TOP_TIER_POTION_TIME = 6


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


def high_tier(state: CollectionState, player: int) -> bool:
    return has_all_potions(state, player) and state.has(POTION_TIME, player, HIGH_TIER_POTION_TIME)


def top_tier(state: CollectionState, player: int) -> bool:
    return (has_all_potions(state, player) and state.has(POTION_TIME, player, TOP_TIER_POTION_TIME)
            and state.has(JUMP, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["Field"])

    for loc_name in _SPHERE_TWO_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: any_progression(state, player))

    for loc_name in _MID_TIER_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: mid_tier(state, player))

    for loc_name in _HIGH_TIER_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: high_tier(state, player))

    for loc_name in _TOP_TIER_LOCS:
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state: top_tier(state, player))
