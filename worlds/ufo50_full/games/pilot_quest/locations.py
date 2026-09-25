from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event
from .items import NUM_SILOS, NUM_WORKBENCHES, NUM_SEEDS, LUMIN_UPGRADES

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"

# Regions (see regions.py): the Campsite (rm37_Incremental, the home base builds and
# the ship launch); the Wild Zone (rm37_Incremental2) split into Start / Bottom Left /
# Borlg Area / Left Side / Top / Right Side; and everything below room y 2160, reached through the
# dungeon doors, as Underground.
#
# id offset layout inside Pilot Quest's 1000-id block:
#      1..4   Silo <n> Built / Silo <n> Upgraded   (o37_Game.silo1 / silo2, 0->1->2)
#     11..16  Workbench <1..6>                      (o37_Game.benches[0..5])
#     21..26  House <n> Built / Upgrade 1 / Upgrade 2  (o37_Game.house1 / house2, 0->1->2->3)
#     31..33  Ship Part <1..3>                      (o37_Game.shipPart1 / 2 / 3)
#     41      Letter                                (picking up npcGropp's letter)
#     42      Blaster                               (picking up npcGrull's gun; needs the Letter item)
#     50      Big Borlg                             (o37_eBossBorlg death)
#     51      Unktomi                               (o37_eUnktomi death)
#     61..65  <Dr Lumin shop upgrade>              (o37_Game.shopBought[0..4]: Metal Yoyo /
#             Fertilizer / Big Silos / Stamin Pill / Wizard Yoyo. Ship Fuel,
#             shopBought[5], stays vanilla)
#     74..80  <Area> Chest <n>                      (o37_KeyItemGen nodes 3..8 at 71 + node n,
#             plus the fixed o37_envChest at 80; see CHESTS. Nodes 0..2 always hold the
#             ship parts -- keyItem[0..2] are shuffled among themselves -- so 71..73 are
#             unused: Ship Part 1..3 cover them)
#     81..84  <Area> Teleporter Statue              (buying the statue of teleporter[0..3])
#     91..97  <n> Zoldnak(s)                        (holding n Zoldnaks at once, n in ZOLDNAK_THRESHOLDS)
#    171..181 <n> Ingot(s)                          (holding n ingots in the Campsite, n in INGOT_THRESHOLDS)
#    111..116 Seed <1..6>                           (buying the n-th seed at the tree)
#    161..166 <n> Moon Drops                        (holding n drops in the Campsite, n in
#             DROP_THRESHOLDS)
#    191..194 <n> Research                          (holding n science in the Campsite)
#    195..198 <n> Silk                              (holding n silk in the Campsite; n in
#             RESOURCE_THRESHOLDS for both)
#    121..123 Dungeon Trader <1..3>                 (the one-time Zoldnak trade at the three
#             dungeon spots that spawn a scorpion in vanilla)
#    131..153 <Enemy>                               (killing one of that enemy type; ENEMIES
#             order, gated in rules.py to the regions it appears in)
#   997/998/999   Gift / Gold / Cherry -- vanilla scrWin(GARDEN/GOLD/CHERRY_WIN)

CAMPSITE = "Campsite"
START = "Start"
BOTTOM_LEFT = "Bottom Left"
BORLG = "Borlg Area"
LEFT = "Left Side"
TOP = "Top"
RIGHT = "Right Side"
UNDERGROUND = "Underground"

NUM_HOUSES = 2
NUM_SHIP_PARTS = 3
NUM_DUNGEON_TRADERS = 3

# the 7 Wild Zone chests: location name -> (id offset, region). 74..79 are the
# o37_KeyItemGen nodes 3..8 (71 + node n; the Gear or a plain chest), 80 is the one
# fixed o37_envChest.
CHESTS: dict[str, tuple[int, str]] = {
    "Borlg Area Chest": (74, BORLG),     # n3 (1232, 240)
    "Left Teleporter Chest": (75, LEFT),     # n4 (1312, 800)
    "Middle Chest": (76, RIGHT),     # n5 (2512, 960)
    "Bottom Left Chest":  (77, BOTTOM_LEFT),  # n6 (288, 1888), behind Tree 1 / Tree 3
    "Top Right Chest 2": (78, RIGHT),     # n7 (4032, 784)
    "Bottom Right Chest": (79, RIGHT),     # n8 (3712, 2032)
    "Top Right Chest 1": (80, RIGHT),     # o37_envChest (3824, 336)
}

# Zoldnak ladder, offsets 91..97; each rung needs ceil(sqrt(n)) Wild Zone areas (rules.py)
ZOLDNAK_THRESHOLDS: tuple[int, ...] = (1, 3, 5, 10, 15, 20, 25)


def zoldnak_location(n: int) -> str:
    return f"{n} Zoldnak" if n == 1 else f"{n} Zoldnaks"


# Ingot ladder, offsets 171..181; requirements in rules.py
INGOT_THRESHOLDS: tuple[int, ...] = (1, 2, 3, 4, 5, 10, 25, 50, 100, 250, 500)


def ingot_location(n: int) -> str:
    return f"{n} Ingot" if n == 1 else f"{n} Ingots"


# one check per enemy type: name -> regions it appears in (from the room placements --
# Underground is room y >= 2160). Offsets 131.. in this order; the mod's kill hook lists
# the objects in the same order. Big Borlg and Unktomi have their own checks.
ENEMIES: dict[str, tuple[str, ...]] = {
    "Beetle":     (LEFT, TOP, BORLG),                    # o37_eBeetle
    "Bomber":     (LEFT, RIGHT, BORLG, UNDERGROUND),     # o37_eBomber
    "Borlg":      (START,),                              # o37_eBorlg (also elsewhere)
    "Big Mech":   (UNDERGROUND,),                        # o37_eBossMech
    "Mech Baby":  (UNDERGROUND,),                        # o37_eBossMechBaby (Big Mech spawns them)
    "Big Plant":  (UNDERGROUND,),                        # o37_eBossPlant
    "Flower":     (UNDERGROUND,),                        # o37_eFlower (Big Plant's seeds grow them)
    "Big Zuzu":   (UNDERGROUND,),                        # o37_eBossZuzu
    "Crab":       (START,),                              # o37_eCrab (mostly Right Side)
    "Crab 2":     (RIGHT,),                              # o37_eCrab2
    "Drip":       (UNDERGROUND,),                        # o37_eDrip
    "Dripper":    (UNDERGROUND,),                        # o37_eDripper
    "Fish":       (START,),                              # o37_eFish (from o37_eFishGen)
    "Fly":        (LEFT, BOTTOM_LEFT, BORLG, UNDERGROUND),  # o37_eFly
    "Scorpion":   (START,),                              # o37_eScorp
    "Shrum":      (BOTTOM_LEFT, LEFT, UNDERGROUND),      # o37_eShrum
    "Snake":      (UNDERGROUND,),                        # o37_eSnake
    "Spider":     (RIGHT,),                              # o37_eSpider
    "Spider 2":   (UNDERGROUND,),                        # o37_eSpider2
    "Tank":       (UNDERGROUND,),                        # o37_eTank
    "Worm":       (UNDERGROUND,),                        # o37_eWorm
    "Twister":    (LEFT, TOP, BORLG),                    # o37_eTwister (spawned in areas 11-13)
    # o37_eDarkPilot, once all 3 ship parts are in; sent on his first defeat (the first
    # of his taunt-and-teleport knockdowns), not the final kill -- keep him last
    "Nozzlo":     (UNDERGROUND,),
}

# Moon Drop ladder, offsets 161..166; requirements in rules.py
DROP_THRESHOLDS: tuple[int, ...] = (100, 500, 1000, 2500, 5000, 10000)


def drop_location(n: int) -> str:
    return f"{n} Moon Drops"


# research / silk ladders, offsets 191..194 / 195..198; requirements in rules.py
RESOURCE_THRESHOLDS: tuple[int, ...] = (10, 50, 100, 250)


def research_location(n: int) -> str:
    return f"{n} Research"


def silk_location(n: int) -> str:
    return f"{n} Silk"


# teleporter[n] (offset 81 + n) -> its region; the location is "<region> Teleporter Statue"
TELEPORTER_REGIONS: tuple[str, ...] = (LEFT, BORLG, RIGHT, TOP)


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_SILOS + 1):
        table[f"Silo {n} Built"] = LocationInfo((n - 1) * 2 + 1, CAMPSITE)
        table[f"Silo {n} Upgraded"] = LocationInfo((n - 1) * 2 + 2, CAMPSITE)
    for n in range(1, NUM_WORKBENCHES + 1):
        table[f"Workbench {n}"] = LocationInfo(10 + n, CAMPSITE)
    for n in range(1, NUM_HOUSES + 1):
        table[f"House {n} Built"] = LocationInfo(20 + (n - 1) * 3 + 1, CAMPSITE)
        table[f"House {n} Upgrade 1"] = LocationInfo(20 + (n - 1) * 3 + 2, CAMPSITE)
        table[f"House {n} Upgrade 2"] = LocationInfo(20 + (n - 1) * 3 + 3, CAMPSITE)
    for n in range(1, NUM_SHIP_PARTS + 1):
        table[f"Ship Part {n}"] = LocationInfo(30 + n, UNDERGROUND)
    table["Letter"] = LocationInfo(41, UNDERGROUND)
    table["Blaster"] = LocationInfo(42, UNDERGROUND)
    table["Big Borlg"] = LocationInfo(50, BORLG)
    table["Unktomi"] = LocationInfo(51, RIGHT)
    for n, name in enumerate(LUMIN_UPGRADES, start=1):
        table[name] = LocationInfo(60 + n, CAMPSITE)
    for name, (offset, region) in CHESTS.items():
        table[name] = LocationInfo(offset, region)
    for n, region in enumerate(TELEPORTER_REGIONS, start=1):
        table[f"{region} Teleporter Statue"] = LocationInfo(80 + n, region)
    for n, threshold in enumerate(ZOLDNAK_THRESHOLDS, start=1):
        table[zoldnak_location(threshold)] = LocationInfo(90 + n, START)
    for n, threshold in enumerate(INGOT_THRESHOLDS, start=1):
        table[ingot_location(threshold)] = LocationInfo(170 + n, CAMPSITE)
    for n in range(1, NUM_SEEDS + 1):
        table[f"Seed {n}"] = LocationInfo(110 + n, CAMPSITE)
    for n, threshold in enumerate(DROP_THRESHOLDS, start=1):
        table[drop_location(threshold)] = LocationInfo(160 + n, CAMPSITE)
    for n, threshold in enumerate(RESOURCE_THRESHOLDS):
        table[research_location(threshold)] = LocationInfo(191 + n, CAMPSITE)
        table[silk_location(threshold)] = LocationInfo(195 + n, CAMPSITE)
    for n in range(1, NUM_DUNGEON_TRADERS + 1):
        table[f"Dungeon Trader {n}"] = LocationInfo(120 + n, UNDERGROUND)
    # each enemy sits in Start (the Wild Zone entry); rules.py gates it on its regions
    for n, name in enumerate(ENEMIES):
        table[name] = LocationInfo(131 + n, START)
    table["Gift"] = LocationInfo(997, RIGHT)          # fires on the Unktomi kill
    # the ship launch; its Underground (ship parts) requirement is in rules.py
    table["Gold"] = LocationInfo(998, CAMPSITE)
    table["Cherry"] = LocationInfo(999, CAMPSITE)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# only the first two Seeds (bought with Moon Drops) are free: every ingot upgrade
# needs a Friend + Workbench + the Wild Zone, and everything else needs other items
sphere_1_locs: list[str] = [f"Seed {n}" for n in range(1, 3)]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Silos"] = {
        f"{GAME_NAME} - Silo {n} {w}" for n in range(1, NUM_SILOS + 1) for w in ("Built", "Upgraded")
    }
    groups[f"{GAME_NAME} - Workbenches"] = {
        f"{GAME_NAME} - Workbench {n}" for n in range(1, NUM_WORKBENCHES + 1)
    }
    groups[f"{GAME_NAME} - Houses"] = {
        f"{GAME_NAME} - House {n} {w}"
        for n in range(1, NUM_HOUSES + 1) for w in ("Built", "Upgrade 1", "Upgrade 2")
    }
    groups[f"{GAME_NAME} - Ship Parts"] = {
        f"{GAME_NAME} - Ship Part {n}" for n in range(1, NUM_SHIP_PARTS + 1)
    }
    groups[f"{GAME_NAME} - Dr Lumin Upgrades"] = {
        f"{GAME_NAME} - {name}" for name in LUMIN_UPGRADES
    }
    groups[f"{GAME_NAME} - Chests"] = {f"{GAME_NAME} - {name}" for name in CHESTS}
    groups[f"{GAME_NAME} - Zoldnaks"] = {
        f"{GAME_NAME} - {zoldnak_location(n)}" for n in ZOLDNAK_THRESHOLDS
    }
    groups[f"{GAME_NAME} - Ingots"] = {
        f"{GAME_NAME} - {ingot_location(n)}" for n in INGOT_THRESHOLDS
    }
    groups[f"{GAME_NAME} - Seeds"] = {
        f"{GAME_NAME} - Seed {n}" for n in range(1, NUM_SEEDS + 1)
    }
    groups[f"{GAME_NAME} - Research"] = {
        f"{GAME_NAME} - {research_location(n)}" for n in RESOURCE_THRESHOLDS
    }
    groups[f"{GAME_NAME} - Silk"] = {f"{GAME_NAME} - {silk_location(n)}" for n in RESOURCE_THRESHOLDS}
    groups[f"{GAME_NAME} - Moon Drops"] = {
        f"{GAME_NAME} - {drop_location(n)}" for n in DROP_THRESHOLDS
    }
    groups[f"{GAME_NAME} - Dungeon Traders"] = {
        f"{GAME_NAME} - Dungeon Trader {n}" for n in range(1, NUM_DUNGEON_TRADERS + 1)
    }
    groups[f"{GAME_NAME} - Enemies"] = {f"{GAME_NAME} - {name}" for name in ENEMIES}
    groups[f"{GAME_NAME} - Teleporters"] = {
        f"{GAME_NAME} - {region} Teleporter Statue" for region in TELEPORTER_REGIONS
    }
    return groups


def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    base_id = get_game_base_id(GAME_NAME)
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            continue

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", base_id + loc_data.id_offset, region)
        region.locations.append(loc)
