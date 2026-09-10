from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Combatants"


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


FOLLOW = _g("Follow")
HOLD = _g("Hold")
INSTINCT = _g("Instinct")
SOLDIER_FOLLOW = _g("Soldier Follow")
SOLDIER_HOLD = _g("Soldier Hold")
PRODUCE_WORKERS = _g("Produce Workers")
PRODUCE_SOLDIERS = _g("Produce Soldiers")

# any one of the four Follow / Hold abilities (worker or soldier flavour)
_FOLLOW_HOLD_ANY = frozenset({FOLLOW, HOLD, SOLDIER_FOLLOW, SOLDIER_HOLD})


def _follow_any(state: "CollectionState", player: int) -> bool:
    return state.has_any((FOLLOW, SOLDIER_FOLLOW), player)


def _full_kit(state: "CollectionState", player: int) -> bool:
    return (state.has(FOLLOW, player) and state.has(HOLD, player)
            and state.has(PRODUCE_WORKERS, player) and state.has(PRODUCE_SOLDIERS, player)
            and state.has(INSTINCT, player))


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    # First Blood / Ambush -> nothing (left unruled, sphere 1)
    mission_rules = {
        "Skirmish":    lambda state: state.has_any(_FOLLOW_HOLD_ANY, player),
        "Surprise":    lambda state: state.has(FOLLOW, player),
        "Commando":    lambda state: _follow_any(state, player),
        "Commando 2":  lambda state: _follow_any(state, player),
        "Pincered":    lambda state: state.has(PRODUCE_SOLDIERS, player) and _follow_any(state, player),
        "Spidernest":  lambda state: state.has(PRODUCE_SOLDIERS, player) and _follow_any(state, player),
        "Open Field":   lambda state: _full_kit(state, player),
        "The Push":     lambda state: _full_kit(state, player),
        "Deathsdoor":   lambda state: _full_kit(state, player),
        "This Is It":   lambda state: _full_kit(state, player),
        "Nemuru's Way": lambda state: _full_kit(state, player),
    }
    for name, rule in mission_rules.items():
        set_rule(world.get_location(_g(name)), rule)

    regions["Menu"].connect(regions["The Campaign"])
    # Gift = kill a spider -> the Spidernest kit (produce soldiers + a Follow order)
    regions["The Campaign"].connect(
        regions["Spider Hunt"],
        rule=lambda state: state.has(PRODUCE_SOLDIERS, player) and _follow_any(state, player))
    # Gold = beat "This Is It"; Cherry = clear all 12 -- both need the full kit
    regions["The Campaign"].connect(regions["Final Assault"], rule=lambda state: _full_kit(state, player))
    regions["The Campaign"].connect(regions["Total Victory"], rule=lambda state: _full_kit(state, player))
