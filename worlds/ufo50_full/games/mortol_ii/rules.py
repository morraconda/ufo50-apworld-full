from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

from .items import (DOOR_NAMES, LIFE_PICKUP, LIFE_PICKUP_VALUE, FILLER, FILLER_VALUE)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# --- lives -------------------------------------------------------------------
# A second dimension on top of the item gates. `lives(state)` = STARTING_LIVES (30) +
# 10 per "+10 Lives" received (+ 5 per "+5 Lives", but that is filler so it never counts
# in logic). Each region has a hardcoded life requirement; an edge into it also needs
# `lives(state) >= that`. With 30 base you now need 2 "+10 Lives" to reach "Ending" (50)
# and all 7 to reach "Cherry Ending" (99).
STARTING_LIVES = 30
LIFE_PICKUP_ITEM = f"{GAME_NAME} - {LIFE_PICKUP}"    # "+10 Lives" (progression, x7)
LIFE_FILLER_ITEM = f"{GAME_NAME} - {FILLER}"         # "+5 Lives" (filler, uncounted)

REGION_LIVES: dict[str, int] = {
    "Menu": 0,
    "Start": 0,
    "Tree": 10,
    "Spawning Cave": 10,
    "Entrance": 10,
    "Treetop": 20,
    "Left Cave": 20,
    "Upper Ruins": 20,
    "Upper Castle": 20,
    "Lower Ruins": 30,
    "Castle Roof": 30,
    "Lower Castle": 30,
    "Sewers": 40,
    "Arena": 40,
    "Final Corridor": 40,
    "Deep Cave": 50,
    "Cave Side Cling": 50,
    "Ending": 50,
    "Cherry Ending": 99,     # 49 more than Ending
}


def lives(state: CollectionState, player: int) -> int:
    return (STARTING_LIVES
            + LIFE_PICKUP_VALUE * state.count(LIFE_PICKUP_ITEM, player)
            + FILLER_VALUE * state.count(LIFE_FILLER_ITEM, player))

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


def ws(state: CollectionState, player: int) -> bool:
    return state.has_any((WARRIOR, SCOUT), player)


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
    "Large Castle Worm": lambda s, p: scout(s, p) and (has(s, p, ENGINEER) or door(s, p, 12)),  # s + (e | d12)
    "Small Castle Worm": lambda s, p: scout(s, p) and (has(s, p, ENGINEER) or door(s, p, 12)),  # s + (e | d12)
    "Ruins Worm": lambda s, p: ws(s, p) and has(s, p, ENGINEER) and has(s, p, BOMBER),          # ws + e + b
    "Sewer Worm": lambda s, p: ws(s, p) and eb(s, p),                                           # ws + (eb)
}


# --- region graph -------------------------------------------------------------
# (parent, child, rule) edges over the annotated-map regions. rule is a
# (state, player) predicate or None for a free edge. Everything hangs off "Start"
# (the small unlabelled area between Tree and Spawning Cave). These only ADD
# gating -- the per-location LOCATION_RULES above still apply.


def _region_edges() -> list[tuple[str, str, Callable[[CollectionState, int], bool] | None]]:
    b = lambda s, p: has(s, p, BOMBER)
    return [
        ("Menu", "Start", None),
        ("Start", "Tree", None),
        ("Start", "Spawning Cave", None),
        ("Start", "Entrance", scout),
        ("Tree", "Treetop", lambda s, p: scout(s, p) and door(s, p, 9)),   # scout + Tree Door
        ("Tree", "Entrance", scout),
        ("Spawning Cave", "Left Cave", eb),
        ("Spawning Cave", "Upper Ruins", scout),
        ("Entrance", "Upper Ruins", None),
        ("Entrance", "Upper Castle", lambda s, p: door(s, p, 11)),         # Castle Entry Door
        ("Upper Ruins", "Lower Ruins", scout),
        ("Lower Ruins", "Sewers", scout),
        ("Lower Ruins", "Arena", lambda s, p: scout(s, p) and b(s, p)),
        ("Sewers", "Deep Cave", scout),
        ("Sewers", "Left Cave", None),
        ("Arena", "Cave Side Cling", scout),
        ("Cave Side Cling", "Final Corridor", lambda s, p: scout(s, p) and b(s, p)),
        ("Upper Castle", "Castle Roof", lambda s, p: scout(s, p) and b(s, p)),
        ("Upper Castle", "Lower Castle", lambda s, p: door(s, p, 12)),     # Castle Door 1
        ("Lower Castle", "Final Corridor", lambda s, p: door(s, p, 13)),   # Castle Door 2
        ("Final Corridor", "Ending", beat_the_game),
        ("Ending", "Cherry Ending", None),   # gate is REGION_LIVES["Cherry Ending"] = 99
    ]


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    for parent, child, rule in _region_edges():
        need_lives = REGION_LIVES.get(child, 0)

        def _edge_rule(state, r=rule, nl=need_lives):
            if lives(state, player) < nl:
                return False
            return True if r is None else r(state, player)

        regions[parent].connect(regions[child], rule=_edge_rule)

    for loc_name, rule in LOCATION_RULES.items():
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 lambda state, r=rule: r(state, player))

    # Gold / Cherry sit in the "Ending" region (gated on beat_the_game via the
    # Final Corridor -> Ending edge), so they need no per-location rule.
