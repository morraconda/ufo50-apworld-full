from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Pilot Quest"
REGION = "Pilot Quest"

# Simple implementation -- every location is a one-off build / pickup / boss kill, all
# sphere 1 (no item gating anywhere in this game).
#
# id offset layout inside Pilot Quest's 1000-id block:
#      1..4   Silo <n> Built / Silo <n> Upgraded   (o37_Game.silo1 / silo2, 0->1->2)
#     11..16  Workbench <1..6>                      (o37_Game.benches[0..5])
#     21..26  House <n> Built / Upgrade 1 / Upgrade 2  (o37_Game.house1 / house2, 0->1->2->3)
#     31..33  Ship Part <1..3>                      (o37_Game.shipPart1 / 2 / 3)
#     41      Letter                                (o37_Game.tLetter, saved as "letter")
#     42      Blaster                               (o37_Game.gun)
#     50      Big Borlg                             (o37_eBossBorlg death)
#     51      Unktomi                               (o37_eUnktomi death)
#     61..66  <Dr Lumin shop upgrade>              (o37_Game.shopBought[0..5]; the 6
#             scr37_ResetData shopItems: Metal Yoyo / Fertilizer / Big Silos /
#             Stamin Pill / Wizard Yoyo / Ship Fuel)
#     71..79  Chest <1..9>                          (the 9 o37_KeyItemGen nodes, n = 0..8)
#     81..84  Teleporter <1..4>                     (o37_Game.teleporter[0..3])
#    200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry -- vanilla scrWin(GARDEN/GOLD/CHERRY_WIN)

NUM_SILOS = 2
NUM_WORKBENCHES = 6
NUM_HOUSES = 2
NUM_SHIP_PARTS = 3
NUM_CHESTS = 9
NUM_TELEPORTERS = 4

# Dr. Lumin's shop, in shopBought[0..5] order (scr37_ResetData); offsets 61..66.
LUMIN_UPGRADES: tuple[str, ...] = (
    "Metal Yoyo", "Fertilizer", "Big Silos", "Stamin Pill", "Wizard Yoyo", "Ship Fuel",
)
NUM_LUMIN_UPGRADES = len(LUMIN_UPGRADES)


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_SILOS + 1):
        table[f"Silo {n} Built"] = LocationInfo((n - 1) * 2 + 1, REGION)
        table[f"Silo {n} Upgraded"] = LocationInfo((n - 1) * 2 + 2, REGION)
    for n in range(1, NUM_WORKBENCHES + 1):
        table[f"Workbench {n}"] = LocationInfo(10 + n, REGION)
    for n in range(1, NUM_HOUSES + 1):
        table[f"House {n} Built"] = LocationInfo(20 + (n - 1) * 3 + 1, REGION)
        table[f"House {n} Upgrade 1"] = LocationInfo(20 + (n - 1) * 3 + 2, REGION)
        table[f"House {n} Upgrade 2"] = LocationInfo(20 + (n - 1) * 3 + 3, REGION)
    for n in range(1, NUM_SHIP_PARTS + 1):
        table[f"Ship Part {n}"] = LocationInfo(30 + n, REGION)
    table["Letter"] = LocationInfo(41, REGION)
    table["Blaster"] = LocationInfo(42, REGION)
    table["Big Borlg"] = LocationInfo(50, REGION)
    table["Unktomi"] = LocationInfo(51, REGION)
    for n, name in enumerate(LUMIN_UPGRADES, start=1):
        table[name] = LocationInfo(60 + n, REGION)
    for n in range(1, NUM_CHESTS + 1):
        table[f"Chest {n}"] = LocationInfo(70 + n, REGION)
    for n in range(1, NUM_TELEPORTERS + 1):
        table[f"Teleporter {n}"] = LocationInfo(80 + n, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# every location is reachable from the start -- no item gating anywhere in this game
sphere_1_locs: list[str] = list(location_table.keys())


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
    groups[f"{GAME_NAME} - Chests"] = {
        f"{GAME_NAME} - Chest {n}" for n in range(1, NUM_CHESTS + 1)
    }
    groups[f"{GAME_NAME} - Teleporters"] = {
        f"{GAME_NAME} - Teleporter {n}" for n in range(1, NUM_TELEPORTERS + 1)
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
