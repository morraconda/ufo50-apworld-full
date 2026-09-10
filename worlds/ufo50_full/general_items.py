from .constants import game_ids, BASE_ID

cartridge_items: dict[str, int] = {f"{name} Cartridge": BASE_ID + num for name, num in game_ids.items()
                                   if name != "Main Menu"}
cartridge_item_group: dict[str, set[str]] = {"Cartridges": {name for name in cartridge_items.keys()}}

# Meta items (traps, and any future cross-game items) live in a reserved "subgame 51"
# id block so they never collide with a real game's 1000-id block or with the
# cartridge items (which sit in subgame 0 as ids 1..50). The mod flags subgame 51 as
# always-included and dispatches these by (subgame 51, offset) -- see Archipelago_Traps.yaml.
META_BASE_ID: int = BASE_ID + 51 * 1000

CONTROLS_SWAP_TRAP: str = "Controls Swap Trap"

trap_items: dict[str, int] = {
    CONTROLS_SWAP_TRAP: META_BASE_ID + 1,  # swaps A <-> B for 30 seconds of play
}
trap_item_group: dict[str, set[str]] = {"Traps": set(trap_items.keys())}

# Pure-logic gating items: when "Defer No Logic Games" is on, every game whose checks
# are all reachable at boot has its cartridge boot gated behind holding all three of
# these. They do nothing in-game (the mod ignores unknown subgame-51 items); they only
# exist so the filler-free "no logic" games can't sit on the start of the critical path.
LOGIC_GATE_COUNT: int = 3
logic_gate_items: dict[str, int] = {
    f"Artificial Logic Gate {n}": META_BASE_ID + 1 + n for n in range(1, LOGIC_GATE_COUNT + 1)
}
logic_gate_item_group: dict[str, set[str]] = {"Logic Gates": set(logic_gate_items.keys())}
