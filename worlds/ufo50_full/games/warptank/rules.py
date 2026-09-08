from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, COFFEE, COFFEE_FOR_FINAL

if TYPE_CHECKING:
    from ... import UFO50World

coffee = f"{GAME_NAME} - {COFFEE}"


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


# hub tier region -> the Capsule Gate item that opens the wall into it. Mirrors the
# vanilla `o16_Mecho` walls (trig 1 / 4 / 9 / 14; the three `o16_MechoE` shortcut
# walls, vanilla-keyed to sectors 18/19/20, ride Capsule Gate 3). The chain is
# monotonic: reaching a later tier implies every earlier one.
_CHAIN_GATE: dict[str, str] = {
    "Hub - Gate 1": "Capsule Gate 1",
    "Hub - Gate 4": "Capsule Gate 2",
    "Hub - Gate 9": "Capsule Gate 3",
    "Hub - Gate 14": "Capsule Gate 4",
}
_HUB_CHAIN: list[str] = ["Station Hub", "Hub - Gate 1", "Hub - Gate 4", "Hub - Gate 9", "Hub - Gate 14"]


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["Station Hub"])

    for prev, nxt in zip(_HUB_CHAIN, _HUB_CHAIN[1:]):
        gate = _g(_CHAIN_GATE[nxt])
        regions[prev].connect(regions[nxt],
                              rule=lambda state, gg=gate: state.has(gg, player))

    # Final Sector: the last Mecho wall AND a coffee bridge long enough to cross (23).
    # Both goal locations (Gold/Cherry) live in that region, so no extra per-location rule.
    regions["Hub - Gate 14"].connect(
        regions["Final Sector"],
        rule=lambda state: (state.has(_g("Capsule Gate 5"), player)
                            and state.has(coffee, player, COFFEE_FOR_FINAL)))
