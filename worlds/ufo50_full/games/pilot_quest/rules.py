from itertools import permutations
from math import ceil, log2, sqrt
from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region

from worlds.generic.Rules import add_rule, set_rule
from .items import (TELEPORTERS, NUM_SILOS, NUM_WORKBENCHES, NUM_SEEDS, SCIENCE_UPGRADES,
                    SILK_UPGRADES)
from .locations import NUM_HOUSES, DROP_THRESHOLDS, drop_location, RESOURCE_THRESHOLDS, research_location, silk_location, ENEMIES, ZOLDNAK_THRESHOLDS, zoldnak_location, INGOT_THRESHOLDS, ingot_location, CAMPSITE, START, BOTTOM_LEFT, BORLG, LEFT, TOP, RIGHT, UNDERGROUND

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"

# region -> the teleporter pad inside it (Start has none)
_PADS: dict[str, str] = {
    LEFT: "Left Side Teleporter",
    BORLG: "Borlg Area Teleporter",
    RIGHT: "Right Side Teleporter",
    TOP: "Top Teleporter",
}
assert set(_PADS.values()) == set(TELEPORTERS)

# (region a, region b, block): removing the block joins a and b, both ways
_BLOCK_EDGES: tuple[tuple[str, str, str], ...] = (
    (START, BORLG, "Start-Borlg Area Gate"),
    (START, BOTTOM_LEFT, "Left Side Tree 4"),
    (START, BOTTOM_LEFT, "Left Side Bushes"),
    (BOTTOM_LEFT, LEFT, "Left Side Tree 2"),
    (START, RIGHT, "Start-Right Side Bushes (Upper)"),
    (START, RIGHT, "Start-Right Side Bushes (Lower)"),
    (BORLG, TOP, "Borlg Area-Top Bones"),
    (LEFT, BORLG, "Left Side-Borlg Area Bones"),
    (LEFT, TOP, "Left Side-Top Bones"),
)

# Seed n costs 10 * 4^(n-1) Moon Drops (o37_Tree): 10, 40, 160, 640, 2560, 10240.
# The drop cap is 2500 * (1 + cap steps), one step per Progressive Resource Cap (up to 4)
# so seed 5 needs 1 step and seed 6 needs 4. Seed n (3+) needs n - 2 Moon Drop plants
# to earn its price.
_SEED_CAP_STEPS: dict[int, int] = {5: 1, 6: 4}
_CAP_ITEMS: tuple[str, ...] = ("Progressive Resource Cap",)

# the Ship Fuel (vanilla purchase: 1000 science + 1000 ingots, science needs the Gear) is
# expected once every resource's income is x8, i.e. 3 of each x2 item
_SHIP_FUEL_DOUBLERS = 3
_DOUBLERS: tuple[str, ...] = ("x2 Ingots", "x2 Research", "x2 Silk")

# what each Campsite upgrade costs: location -> (ingots, science, silk). Ship Fuel (the
# vanilla purchase Gold / Cherry need) is 1000 ingots + 1000 science.
_UPGRADE_COSTS: dict[str, tuple[int, int, int]] = {
    **{f"Silo {n} Built": (50, 0, 0) for n in range(1, NUM_SILOS + 1)},
    **{f"Silo {n} Upgraded": (200, 0, 0) for n in range(1, NUM_SILOS + 1)},
    **{f"Workbench {n}": (5, 0, 0) for n in range(1, NUM_WORKBENCHES + 1)},
    **{f"House {n} Built": (5, 0, 0) for n in range(1, NUM_HOUSES + 1)},
    **{f"House {n} Upgrade 1": (20, 0, 0) for n in range(1, NUM_HOUSES + 1)},
    **{f"House {n} Upgrade 2": (100, 0, 0) for n in range(1, NUM_HOUSES + 1)},
    "Metal Yoyo": (150, 0, 0),
    "Fertilizer": (0, 100, 0),
    "Big Silos": (200, 0, 150),
    "Stamin Pill": (100, 300, 100),
    "Wizard Yoyo": (0, 500, 200),
    "Gold": (1000, 1000, 0),
    "Cherry": (1000, 1000, 0),
}
# base caps (scr37_ResetData *MaxBase): ingots 250, science 300, silk 50; each cap step
# (Progressive Resource Cap) adds another base
_BASE_CAPS: tuple[int, int, int] = (250, 300, 50)
# x2 items expected before a cost, per resource: ceil(log2(amount / 20)), at most 4
_MAX_DOUBLERS = 4


def _cap_steps(cost: tuple[int, int, int]) -> int:
    """Cap steps needed to hold every resource of ``cost`` at once."""
    return max(0, *(ceil(amount / base) - 1 for amount, base in zip(cost, _BASE_CAPS)))


def _doublers(amount: int) -> int:
    """x2 items of a resource expected before spending ``amount`` of it: 0.._MAX_DOUBLERS."""
    return min(_MAX_DOUBLERS, max(0, ceil(log2(amount / 20)))) if amount else 0


# the Wild Zone areas; each has a dungeon door, and which interior a door leads to is
# reshuffled every run (scr37_ResetData dunLoc), so the Underground needs all of them
_WILD_ZONE: tuple[str, ...] = (START, BORLG, LEFT, TOP, RIGHT)


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    regions["Menu"].connect(regions[CAMPSITE])
    # logic expects meat (the Meat Shack) and a Moon Drop plant before the Wild Zone
    regions[CAMPSITE].connect(regions[START], f"{GAME_NAME} - {CAMPSITE} -> {START}",
                              lambda state: state.has_all((_g("Meat Shack"), _g("Seed")),
                                                          player))
    regions[START].connect(regions[CAMPSITE])

    for a, b, block in _BLOCK_EDGES:
        item = _g(block)
        regions[a].connect(regions[b], f"{GAME_NAME} - {a} -> {b} ({block})",
                           lambda state, item=item: state.has(item, player))
        regions[b].connect(regions[a], f"{GAME_NAME} - {b} -> {a} ({block})",
                           lambda state, item=item: state.has(item, player))

    # standing on an active pad warps to any other active pad: from a region you can
    # reach, with its pad and the destination's pad both switched on
    for src, dst in permutations(_PADS, 2):
        pads = (_g(_PADS[src]), _g(_PADS[dst]))
        regions[src].connect(regions[dst], f"{GAME_NAME} - {src} -> {dst} (Teleporter)",
                             lambda state, pads=pads: state.has_all(pads, player))

    wild_zone = [regions[name] for name in _WILD_ZONE]

    def reaches_wild_zone(state: CollectionState) -> bool:
        return all(state.can_reach(region) for region in wild_zone)

    underground = regions[START].connect(regions[UNDERGROUND],
                                         f"{GAME_NAME} - {START} -> {UNDERGROUND}",
                                         reaches_wild_zone)
    for region in wild_zone:
        world.multiworld.register_indirect_condition(region, underground)

    # the Zoldnak ladder: n Zoldnaks needs ceil(sqrt(n)) of the Wild Zone areas reachable
    for n in ZOLDNAK_THRESHOLDS:
        set_rule(world.get_location(_g(zoldnak_location(n))),
                 lambda state, need=ceil(sqrt(n)):
                 sum(state.can_reach(region) for region in wild_zone) >= need)

    # the ingot ladder (ingots held at once in the Campsite): every rung needs a Friend
    # working a Workbench, the same x2 Ingots as spending that many ingots would (25 -> 1,
    # 50 -> 2, 100 -> 3, 250 / 500 -> 4), and the ingot cap to hold them (500 -> 1 step)
    cap_items = tuple(_g(item) for item in _CAP_ITEMS)
    for n in INGOT_THRESHOLDS:
        set_rule(world.get_location(_g(ingot_location(n))),
                 lambda state, k=_doublers(n), steps=_cap_steps((n, 0, 0)):
                 state.has_all((_g("Friend"), _g("Workbench")), player)
                 and state.has(_g("x2 Ingots"), player, k)
                 and sum(state.count(item, player) for item in cap_items) >= steps)

    # Seeds: 1-2 are free, seed n (3-6) needs n - 2 Moon Drop plants, 5-6 need
    # the drop cap
    for n in range(3, NUM_SEEDS + 1):
        set_rule(world.get_location(_g(f"Seed {n}")),
                 lambda state, n=n, steps=_SEED_CAP_STEPS.get(n, 0):
                 state.has(_g("Seed"), player, n - 2)
                 and sum(state.count(item, player) for item in cap_items) >= steps)

    # the Moon Drop ladder (drops held in the Campsite): rung k needs ceil(k / 2) Seeds and
    # the drop cap to hold that many (2500 per cap step)
    for k, n in enumerate(DROP_THRESHOLDS, start=1):
        set_rule(world.get_location(_g(drop_location(n))),
                 lambda state, seeds=ceil(k / 2), steps=max(0, ceil(n / 2500) - 1):
                 state.has(_g("Seed"), player, seeds)
                 and sum(state.count(item, player) for item in cap_items) >= steps)

    # Grull only hands over the Blaster for the Letter item
    set_rule(world.get_location(_g("Blaster")), lambda state: state.has(_g("Letter"), player))

    # an enemy's check needs any region it appears in
    for name, where in ENEMIES.items():
        if where != (START,):
            set_rule(world.get_location(_g(name)),
                     lambda state, where=tuple(regions[r] for r in where):
                     any(state.can_reach(region) for region in where))

    # upgrading a silo needs Big Silos to offer it (building it first is covered by the
    # upgrade's own ingot costs below, which are stricter than the build's)
    for n in range(1, NUM_SILOS + 1):
        set_rule(world.get_location(_g(f"Silo {n} Upgraded")),
                 lambda state: state.has(_g("Big Silos"), player))

    # anything that costs science can only be bought with the Gear, anything that costs
    # silk only with Unktomi
    for name in dict.fromkeys(SCIENCE_UPGRADES + SILK_UPGRADES):
        needs = tuple(_g(item) for item, upgrades in (("Gear", SCIENCE_UPGRADES),
                                                      ("Unktomi", SILK_UPGRADES))
                      if name in upgrades)
        set_rule(world.get_location(_g(name)),
                 lambda state, needs=needs: state.has_all(needs, player))

    # launching the ship (Gold / Cherry) needs the ship parts, picked up in the Underground,
    # and the Ship Fuel upgrade
    underground_region = regions[UNDERGROUND]
    doublers = tuple(_g(item) for item in _DOUBLERS)

    def has_ship_fuel(state: CollectionState) -> bool:
        return (state.has(_g("Gear"), player)
                and all(state.has(item, player, _SHIP_FUEL_DOUBLERS) for item in doublers))

    for loc in regions[CAMPSITE].locations:
        if loc.name in (_g("Gold"), _g("Cherry")):
            set_rule(loc, lambda state: state.can_reach(underground_region) and has_ship_fuel(state))

    # every Campsite upgrade, by what it costs (added on top of the rules above):
    #   ingots        -> the Wild Zone (Start reachable), a Friend and a Workbench
    #   science/silk  -> 2 Friends
    #   each resource -> ceil(log2(amount / 20)) of its x2 item (capped at 4)
    #   any           -> enough cap steps to hold the whole price
    start = regions[START]
    campsite = {loc.name: loc for loc in regions[CAMPSITE].locations}

    def add_cost_rules(loc, cost: tuple[int, int, int]) -> None:
        ingots, science, silk = cost
        if ingots:
            add_rule(loc, lambda state: state.can_reach(start)
                     and state.has_all((_g("Friend"), _g("Workbench")), player))
        if science or silk:
            add_rule(loc, lambda state: state.has(_g("Friend"), player, 2))
        for doubler, amount in zip(_DOUBLERS, cost):
            if _doublers(amount):
                add_rule(loc, lambda state, item=_g(doubler), k=_doublers(amount):
                         state.has(item, player, k))
        steps = _cap_steps(cost)
        if steps:
            add_rule(loc, lambda state, steps=steps:
                     sum(state.count(item, player) for item in cap_items) >= steps)

    for name, cost in _UPGRADE_COSTS.items():
        add_cost_rules(campsite[_g(name)], cost)

    # the research / silk ladders (held in the Campsite): each rung is gated like an upgrade
    # costing that much, plus what produces it -- the Gear (research) or Unktomi (silk)
    for n in RESOURCE_THRESHOLDS:
        for name, cost, source in ((research_location(n), (0, n, 0), "Gear"),
                                   (silk_location(n), (0, 0, n), "Unktomi")):
            loc = campsite[_g(name)]
            add_rule(loc, lambda state, source=_g(source): state.has(source, player))
            add_cost_rules(loc, cost)

    # Cherry also needs all 4 cap steps (both silos, both resource caps) and a strong weapon
    # (the Wizard Yoyo or the Blaster)
    add_rule(campsite[_g("Cherry")],
             lambda state: sum(state.count(item, player) for item in cap_items) >= 4
             and state.has_any((_g("Wizard Yoyo"), _g("Blaster")), player))

    # the Bottom Left Chest (KeyItemGen n6) sits in its own pocket, opened by Tree 1 or
    # Tree 3
    set_rule(world.get_location(_g("Bottom Left Chest")),
             lambda state: state.has_any((_g("Left Side Tree 1"), _g("Left Side Tree 3")), player))
