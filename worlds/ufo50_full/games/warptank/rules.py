from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, COFFEE, COFFEE_FOR_FINAL

if TYPE_CHECKING:
    from ... import UFO50World

coffee = f"{GAME_NAME} - {COFFEE}"


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


# Hub topology (parent region, child region, the Capsule Gate item that opens the wall
# between them; item names use the vanilla `o16_Mecho` trig thresholds). Not a straight
# chain: the Hub branches to tiers 1 and 4; tier 4 branches to 9 and 14; tier 14 leads
# to Gate 22 (which holds only the goal). Tiers 1 and 9 are dead-end branches. The three
# `o16_MechoE` shortcut walls (vanilla-keyed to sectors 18/19/20) ride the "9 Capsule Gate".
_HUB_EDGES: list[tuple[str, str, str]] = [
    ("Hub",     "Gate 1",  "1 Capsule Gate"),
    ("Hub",     "Gate 4",  "4 Capsule Gate"),
    ("Gate 4",  "Gate 9",  "9 Capsule Gate"),
    ("Gate 4",  "Gate 14", "14 Capsule Gate"),
    ("Gate 14", "Gate 22", "22 Capsule Gate"),
]


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["Hub"])

    for parent, child, gate in _HUB_EDGES:
        g = _g(gate)
        regions[parent].connect(regions[child],
                                rule=lambda state, gg=g: state.has(gg, player))

    # The final sector sits in Gate 4, but reaching it in-game also needs a coffee bridge
    # long enough to cross (23) -- so its clear check carries that as an extra rule.
    set_rule(world.get_location(_g("Final Sector")),
             lambda state: state.has(coffee, player, COFFEE_FOR_FINAL))

    # Gold/Cherry live in the Gate 22 region (behind "22 Capsule Gate"), so no per-
    # location rule -- and crucially NOT gated on the coffee bridge / the final sector.
