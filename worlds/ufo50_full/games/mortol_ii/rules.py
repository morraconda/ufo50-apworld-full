from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import DOOR_NAMES

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

WARRIOR = f"{GAME_NAME} - Warrior"
SCOUT = f"{GAME_NAME} - Scout"
ENGINEER = f"{GAME_NAME} - Engineer"
BOMBER = f"{GAME_NAME} - Bomber"

# --- predicates -----------------------------------------------------------------
# Shorthand from the spec (2026-09-07: every former "(ws) = Warrior or Scout" was
# narrowed to Scout only, so `scout` replaces `ws` everywhere):
#   scout = Scout                   (eb)  = Engineer or Bomber
#   (wse) = Warrior, Scout or Engineer
#   e / b / s / w alone            = that specific guise
#   dN    = Door number N (DOOR_NAMES[N-1])       dN-M  = Doors N..M
#   blue/yellow/green              = that colour's Switch Block item


def has(state: CollectionState, player: int, item: str) -> bool:
    return state.has(item, player)


def scout(state: CollectionState, player: int) -> bool:
    return state.has(SCOUT, player)


def eb(state: CollectionState, player: int) -> bool:
    return state.has_any((ENGINEER, BOMBER), player)


def wse(state: CollectionState, player: int) -> bool:
    return state.has_any((WARRIOR, SCOUT, ENGINEER), player)


def door(state: CollectionState, player: int, n: int) -> bool:
    return state.has(f"{GAME_NAME} - {DOOR_NAMES[n - 1]}", player)


def doors(state: CollectionState, player: int, lo: int, hi: int) -> bool:
    return state.has_all(tuple(f"{GAME_NAME} - {DOOR_NAMES[n - 1]}" for n in range(lo, hi + 1)), player)


def switch_blocks(state: CollectionState, player: int, *colors: str) -> bool:
    return state.has_all(tuple(f"{GAME_NAME} - {c} Switch Block" for c in colors), player)


def _key_i(state: CollectionState, player: int) -> bool:
    # Spike Key (and Blobus Key): s + d14  /  w + b + d14  /  w + s + d11  /  s + e
    return (
        (has(state, player, SCOUT) and door(state, player, 14))
        or (has(state, player, WARRIOR) and has(state, player, BOMBER) and door(state, player, 14))
        or (has(state, player, WARRIOR) and has(state, player, SCOUT) and door(state, player, 11))
        or (scout(state, player) and has(state, player, ENGINEER))
    )


def beat_the_game(state: CollectionState, player: int) -> bool:
    # s + (eb) + d1-8   /   s + b + d1-4
    return (
        (scout(state, player) and eb(state, player) and doors(state, player, 1, 8))
        or (scout(state, player) and has(state, player, BOMBER) and doors(state, player, 1, 4))
    )


# --- per-location access rules -------------------------------------------------
# keyed by the bare location name. The key names (vanilla A..Q in parens) come from
# the annotated map; the only logic change is (ws) -> s (Scout only).
LOCATION_RULES: dict[str, Callable[[CollectionState, int], bool]] = {
    "Goober Key": lambda s, p: True,                                         # A: Always
    "Face Key": wse,                                                         # B: (wse)
    "Croc Key": wse,                                                         # C: (wse)
    "Caged Key": lambda s, p: has(s, p, ENGINEER),                           # D: e
    "Bottom-left Key": lambda s, p: wse(s, p) and has(s, p, BOMBER),         # E: (wse) + b
    "Limbo Key": lambda s, p: (has(s, p, WARRIOR) and has(s, p, ENGINEER))   # F: w + e
                              or (scout(s, p) and has(s, p, BOMBER)),        #    / s + b
    "Maze Key": scout,                                                       # G: s
    "Subsurface Key": lambda s, p: has(s, p, SCOUT) or (has(s, p, WARRIOR) and eb(s, p)),  # H: s / w + (eb)
    "Spike Key": _key_i,                                                     # I
    "Switch Stair Key": lambda s, p: scout(s, p) or (has(s, p, ENGINEER) and switch_blocks(s, p, "Blue", "Yellow", "Green")),  # J
    "Blobus Key": _key_i,                                                    # K: same as Spike Key
    "Gorgon Stair Key": scout,                                              # L: s
    "Worm Key": lambda s, p: scout(s, p) and (door(s, p, 12) or has(s, p, ENGINEER)),  # M: s + d12 / s + e
    "Branch Key": scout,                                                     # N: s
    "Castle Key 1": lambda s, p: scout(s, p) and has(s, p, ENGINEER),        # O: s + e
    "Castle Key 2": lambda s, p: scout(s, p) and has(s, p, ENGINEER),        # P: s + e
    "Top-right Key": lambda s, p: scout(s, p) and has(s, p, BOMBER),         # Q: s + b
    "Blue Switch": wse,                                                      # (wse)
    "Yellow Switch": scout,                                                  # s
    "Green Switch": lambda s, p: scout(s, p) and eb(s, p),                   # s + (eb)
    "Boss 1": scout,                                                         # s
    "Boss 2": scout,                                                         # s
    "Boss 3": scout,                                                         # s
}


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    regions["Menu"].connect(regions["Ruins"])

    for loc_name, rule in LOCATION_RULES.items():
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, r=rule: r(state, player))

    for goal in ("Gold", "Cherry"):
        set_rule(world.get_location(f"{GAME_NAME} - {goal}"),
                 lambda state: beat_the_game(state, player))
