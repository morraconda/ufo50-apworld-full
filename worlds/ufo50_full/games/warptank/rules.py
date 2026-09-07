from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, CAPSULE, COFFEE, COFFEE_FOR_FINAL

if TYPE_CHECKING:
    from ... import UFO50World

capsule = f"{GAME_NAME} - {CAPSULE}"
coffee = f"{GAME_NAME} - {COFFEE}"

# hub region -> Capsule count needed to enter it. Mirrors the vanilla `o16_Mecho`
# gates, which open at a cumulative sector-clear count of 1 / 4 / 9 / 14 / 22 (the
# three `o16_MechoE` shortcut walls, vanilla-keyed to sectors 18/19/20, are folded
# into the >= 9 tier). The chain is monotonic: reaching a later tier implies every
# earlier one.
_CAPSULE_GATE: dict[str, int] = {
    "Hub - Gate 1": 1,
    "Hub - Gate 4": 4,
    "Hub - Gate 9": 9,
    "Hub - Gate 14": 14,
}
_HUB_CHAIN: list[str] = ["Station Hub", "Hub - Gate 1", "Hub - Gate 4", "Hub - Gate 9", "Hub - Gate 14"]

# Final Sector: the trig=22 Mecho wall AND a coffee bridge long enough to cross.
CAPSULE_FOR_FINAL = 22


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions["Station Hub"])

    for prev, nxt in zip(_HUB_CHAIN, _HUB_CHAIN[1:]):
        need = _CAPSULE_GATE[nxt]
        regions[prev].connect(regions[nxt],
                              rule=lambda state, n=need: state.has(capsule, player, n))

    # Reaching the Final Sector is all that gates Gold and Cherry -- both goal locations
    # live in that region, so no extra per-location rule is needed.
    regions["Hub - Gate 14"].connect(
        regions["Final Sector"],
        rule=lambda state: (state.has(capsule, player, CAPSULE_FOR_FINAL)
                            and state.has(coffee, player, COFFEE_FOR_FINAL)))
