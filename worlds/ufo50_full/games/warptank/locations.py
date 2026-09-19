from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# id offset layout inside Warptank's 1000-id block:
#   10..270  <Sector> Sector            via game_helpers.level_id (offset = level * 10 +
#            slot); "level" = 1-based position in SECTORS below, which is exactly the
#            order the vanilla SLIM-TANK level-select terminal cheat lists them in
#            (game_cheat_16_1 -> o16_Mas_Create_0's levelSelector[] build, sector index
#            ascending 0..30 skipping unused rooms) -- 1st Crust, 2nd Yard, ..., 26th
#            Riot; Final isn't in that terminal listing but sorts last by index anyway,
#            so it lands as level 27, after Riot.
#     level_id(n, 0)   <Sector> Sector           (cleared that sector)
#     level_id(n, 1)   <Sector> Sector - Coffee  (banked that sector's coffee on the way out)
#   0..9     Pink/Gray/Orange/Red Tank, <npc> NPC -- not tied to any one sector (the pit
#            stops and NPCs live in the hub itself, gated by hub tier, not by sector), so
#            they're flat offsets in the 0..9 band level_id reserves for that: Tank
#            Colours 0..3 (pit stop num - 1), NPCs 4..9 (3 + npc num)
#   997/998/999  Gift / Gold / Cherry

class Sector(NamedTuple):
    index: int         # o16_Mas.lv* index (also the vanilla sector number)
    name: str          # display name (from lvName in gml_Object_o16_Mas_Create_0)
    has_coffee: bool   # lvHasCoffee -- whether this sector has a collectible coffee
    region: str        # hub tier its locations live behind


class Npc(NamedTuple):
    num: int           # o16_Npc.num
    name: str
    region: str        # hub tier its location lives behind


class TankColour(NamedTuple):
    num: int           # o16_Pitstop.num / o16_Tank.mySprite value
    name: str
    region: str


SECTORS: list[Sector] = [
    Sector(0,  "Crust",   True,  "Hub"),
    Sector(1,  "Yard",    True,  "Hub"),
    Sector(2,  "Piston",  True,  "Hub"),
    Sector(3,  "Jr",      True,  "Gate 1"),
    Sector(4,  "Bomb",    True,  "Gate 1"),
    Sector(5,  "Meal",    True,  "Gate 1"),
    Sector(6,  "Stare",   True,  "Gate 4"),
    Sector(7,  "Healing", True,  "Gate 4"),
    Sector(8,  "Tower",   True,  "Gate 4"),
    Sector(9,  "Mazurka", True,  "Gate 4"),
    Sector(10, "Nest",    True,  "Gate 4"),
    Sector(11, "Orb",     False, "Gate 4"),
    Sector(12, "Form",    True,  "Gate 9"),
    Sector(13, "Sore",    True,  "Gate 9"),
    Sector(15, "Deep",    True,  "Gate 9"),
    Sector(16, "Nugget",  True,  "Gate 9"),
    Sector(17, "Garl",    False, "Gate 14"),
    Sector(18, "Axon",    True,  "Gate 14"),
    Sector(19, "Sacrum",  True,  "Gate 14"),
    Sector(20, "Dyad",    True,  "Gate 14"),
    Sector(23, "Port",    True,  "Gate 14"),
    Sector(24, "Shock",   True,  "Gate 14"),
    Sector(25, "Soft",    True,  "Gate 14"),
    Sector(26, "Kraft",   False, "Gate 14"),
    Sector(27, "Guide",   True,  "Gate 14"),
    Sector(28, "Riot",    True,  "Gate 14"),
    Sector(30, "Final",   False, "Gate 4"),   # in Gate 4; rules.py adds the coffee-bridge rule
]

# 4 of the 5 pit stops are checks -- the pit stop's num turns the tank that colour.
TANK_COLOURS: list[TankColour] = [
    TankColour(1, "Pink Tank",   "Gate 4"),
    TankColour(2, "Gray Tank",   "Gate 9"),
    TankColour(3, "Orange Tank", "Gate 14"),
    TankColour(4, "Red Tank",    "Gate 14"),
]

# NPCs 5 / 6 flank the Barista in the cafe (5 = left "Wow! Yahoo!", 6 = right, the
# snail) -- confirm the nums in-game if a check fires on the wrong one.
NPCS: list[Npc] = [
    Npc(1, "Crane Fisher", "Gate 9"),
    Npc(2, "Sports Car",   "Gate 4"),
    Npc(3, "Smelly Truck", "Gate 9"),
    Npc(4, "Barista",      "Gate 14"),
    Npc(5, "Wow! Yahoo!",  "Gate 14"),
    Npc(6, "Snail",        "Gate 14"),
]


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for level, sec in enumerate(SECTORS, start=1):
        table[f"{sec.name} Sector"] = LocationInfo(level_id(level, 0), sec.region)
        if sec.has_coffee:
            table[f"{sec.name} Sector - Coffee"] = LocationInfo(level_id(level, 1), sec.region)
    for tc in TANK_COLOURS:
        table[tc.name] = LocationInfo(tc.num - 1, tc.region)
    for npc in NPCS:
        table[f"{npc.name} NPC"] = LocationInfo(3 + npc.num, npc.region)
    table["Gift"] = LocationInfo(997, "Gate 14")
    table["Gold"] = LocationInfo(998, "Gate 22")     # own region behind "22 Capsule Gate", separate from the Final Sector
    table["Cherry"] = LocationInfo(999, "Gate 22")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# locations reachable before any Mecho Gate opens
sphere_1_locs: list[str] = [name for name, data in location_table.items()
                            if data.region_name == "Hub"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Sectors"] = {f"{GAME_NAME} - {s.name} Sector" for s in SECTORS}
    groups[f"{GAME_NAME} - Coffee"] = {f"{GAME_NAME} - {s.name} Sector - Coffee"
                                       for s in SECTORS if s.has_coffee}
    groups[f"{GAME_NAME} - Tank Colours"] = {f"{GAME_NAME} - {tc.name}" for tc in TANK_COLOURS}
    groups[f"{GAME_NAME} - NPCs"] = {f"{GAME_NAME} - {n.name} NPC" for n in NPCS}
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
