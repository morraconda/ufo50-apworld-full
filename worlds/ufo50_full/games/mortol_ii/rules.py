from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

WARRIOR = f"{GAME_NAME} - Warrior"
SCOUT = f"{GAME_NAME} - Scout"
ENGINEER = f"{GAME_NAME} - Engineer"
BOMBER = f"{GAME_NAME} - Bomber"

# --- predicates -----------------------------------------------------------------
# Shorthand from the spec:
#   (ws)  = Warrior or Scout        (eb)  = Engineer or Bomber
#   (wse) = Warrior, Scout or Engineer
#   e / b / s / w alone            = that specific guise
#   dN    = Door N                 dN-M  = Doors N..M
#   blue/yellow/green              = that colour's Switch Block item


def has(state: CollectionState, player: int, item: str) -> bool:
    return state.has(item, player)


def ws(state: CollectionState, player: int) -> bool:
    return state.has_any((WARRIOR, SCOUT), player)


def eb(state: CollectionState, player: int) -> bool:
    return state.has_any((ENGINEER, BOMBER), player)


def wse(state: CollectionState, player: int) -> bool:
    return state.has_any((WARRIOR, SCOUT, ENGINEER), player)


def door(state: CollectionState, player: int, n: int) -> bool:
    return state.has(f"{GAME_NAME} - Door {n}", player)


def doors(state: CollectionState, player: int, lo: int, hi: int) -> bool:
    return state.has_all(tuple(f"{GAME_NAME} - Door {n}" for n in range(lo, hi + 1)), player)


def switch_blocks(state: CollectionState, player: int, *colors: str) -> bool:
    return state.has_all(tuple(f"{GAME_NAME} - {c} Switch Block" for c in colors), player)


def _key_i(state: CollectionState, player: int) -> bool:
    # I (and K): s + d14  /  w + b + d14  /  w + s + d11  /  (ws) + e
    return (
        (has(state, player, SCOUT) and door(state, player, 14))
        or (has(state, player, WARRIOR) and has(state, player, BOMBER) and door(state, player, 14))
        or (has(state, player, WARRIOR) and has(state, player, SCOUT) and door(state, player, 11))
        or (ws(state, player) and has(state, player, ENGINEER))
    )


def beat_the_game(state: CollectionState, player: int) -> bool:
    # (ws) + (eb) + d1-8   /   (ws) + b + d1-4
    return (
        (ws(state, player) and eb(state, player) and doors(state, player, 1, 8))
        or (ws(state, player) and has(state, player, BOMBER) and doors(state, player, 1, 4))
    )


# --- per-location access rules -------------------------------------------------
# keyed by the bare location name (Key <letter>, <Colour> Switch, Boss <n>)
LOCATION_RULES: dict[str, Callable[[CollectionState, int], bool]] = {
    "Key A": lambda s, p: True,                                              # Always
    "Key B": wse,                                                            # (wse)
    "Key C": wse,                                                            # (wse)
    "Key D": lambda s, p: has(s, p, ENGINEER),                               # e
    "Key E": lambda s, p: wse(s, p) and has(s, p, BOMBER),                   # (wse) + b
    "Key F": lambda s, p: (has(s, p, WARRIOR) and has(s, p, ENGINEER))       # w + e
                          or (ws(s, p) and has(s, p, BOMBER)),               # / (ws) + b
    "Key G": ws,                                                             # (ws)
    "Key H": lambda s, p: has(s, p, SCOUT) or (has(s, p, WARRIOR) and eb(s, p)),  # s / w + (eb)
    "Key I": _key_i,
    "Key J": lambda s, p: ws(s, p) or (has(s, p, ENGINEER) and switch_blocks(s, p, "Blue", "Yellow", "Green")),
    "Key K": _key_i,                                                         # same as I
    "Key L": ws,                                                             # (ws)
    "Key M": lambda s, p: ws(s, p) and (door(s, p, 12) or has(s, p, ENGINEER)),  # (ws) + d12 / (ws) + e
    "Key N": ws,                                                             # (ws)
    "Key O": lambda s, p: ws(s, p) and has(s, p, ENGINEER),                  # (ws) + e
    "Key P": lambda s, p: ws(s, p) and has(s, p, ENGINEER),                  # (ws) + e
    "Key Q": lambda s, p: ws(s, p) and has(s, p, BOMBER),                    # (ws) + b
    "Blue Switch": wse,                                                      # (wse)
    "Yellow Switch": ws,                                                     # (ws)
    "Green Switch": lambda s, p: ws(s, p) and eb(s, p),                     # (ws) + (eb)
    "Boss 1": ws,                                                            # (ws)
    "Boss 2": ws,                                                            # (ws)
    "Boss 3": ws,                                                            # (ws)
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
