from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Warptank"

# id offset layout inside Warptank's 1000-id block:
#   100 + s      <Sector> Sector            (cleared sector s, s = o16_Mas.lv* index 0..30)
#   140 + s      <Sector> Sector - Coffee   (banked that sector's coffee on the way out)
#   400 + k      Tank Colour <A..E>         (swapped to tank colour k at its pit stop)
#   410 + n      Talk to <npc>              (finished npc n's dialogue, n = o16_Npc.num 1..10)
#   430          Enter the Cafe             (talked to the barista, npc 4)
#   997/998/999  Gift / Gold / Cherry

# (sector index, display name, has a collectible coffee)
# indices/names/coffee flags are from gml_Object_o16_Mas_Create_0 (lvName / lvHasCoffee).
SECTORS: list[tuple[int, str, bool]] = [
    (0, "Crust", True), (1, "Yard", True), (2, "Piston", True), (3, "Jr", True), (4, "Bomb", True),
    (5, "Meal", True), (6, "Stare", True), (7, "Healing", True), (8, "Tower", True), (9, "Mazurka", True),
    (10, "Nest", True), (11, "Orb", False), (12, "Form", True), (13, "Sore", True), (15, "Deep", True),
    (16, "Nugget", True), (17, "Garl", False), (18, "Axon", True), (19, "Sacrum", True), (20, "Dyad", True),
    (23, "Port", True), (24, "Shock", True), (25, "Soft", True), (26, "Kraft", False), (27, "Guide", True),
    (28, "Riot", True), (30, "Final", False),
]

TANK_COLOURS: list[str] = ["A", "B", "C", "D", "E"]  # o16_Tank.mySprite 0..4

# o16_Npc.num -> display name (npc_* string keys in the game text)
NPCS: dict[int, str] = {
    1: "the Crane Fisher", 2: "the Sports Car", 3: "the Smelly Truck", 4: "the Barista",
    5: "the Traveller", 6: "the Shadow", 7: "the Brain", 8: "the Tank Friend",
    9: "the Little Guy", 10: "the Pig Man",
}

# which hub region each sector's locations live in. The region entry rules (rules.py)
# gate these on the matching "Mecho Gate <n>" item, one per vanilla o16_Mecho wall.
_SECTOR_REGION: dict[int, str] = {
    **{s: "Station Hub" for s in (0, 1, 2, 3, 4)},
    **{s: "Hub - Gate 1" for s in (5, 6, 7, 8)},
    **{s: "Hub - Gate 4" for s in (9, 10, 11, 12, 13)},
    **{s: "Hub - Gate 9" for s in (15, 16, 17, 18, 19)},
    **{s: "Hub - Gate 14" for s in (20, 23, 24, 25, 26, 27, 28)},
    30: "Final Sector",
}
_COLOUR_REGION: dict[int, str] = {0: "Station Hub", 1: "Station Hub", 2: "Hub - Gate 1",
                                  3: "Hub - Gate 4", 4: "Hub - Gate 9"}
_NPC_REGION: dict[int, str] = {1: "Station Hub", 2: "Station Hub", 3: "Station Hub",
                               4: "Hub - Gate 1", 5: "Hub - Gate 4", 6: "Hub - Gate 4",
                               7: "Hub - Gate 9", 8: "Hub - Gate 9",
                               9: "Hub - Gate 14", 10: "Hub - Gate 14"}


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for s, name, has_coffee in SECTORS:
        table[f"{name} Sector"] = LocationInfo(100 + s, _SECTOR_REGION[s])
    for s, name, has_coffee in SECTORS:
        if has_coffee:
            table[f"{name} Sector - Coffee"] = LocationInfo(140 + s, _SECTOR_REGION[s])
    for k, letter in enumerate(TANK_COLOURS):
        table[f"Tank Colour {letter}"] = LocationInfo(400 + k, _COLOUR_REGION[k])
    for n, who in NPCS.items():
        table[f"Talk to {who}"] = LocationInfo(410 + n, _NPC_REGION[n])
    table["Enter the Cafe"] = LocationInfo(430, "Hub - Gate 1")
    table["Gift"] = LocationInfo(997, "Hub - Gate 9")
    table["Gold"] = LocationInfo(998, "Final Sector")
    table["Cherry"] = LocationInfo(999, "Final Sector")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# locations reachable before any Mecho Gate opens
sphere_1_locs: list[str] = [name for name, data in location_table.items()
                            if data.region_name == "Station Hub"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Sectors"] = {f"{GAME_NAME} - {name} Sector" for _, name, _ in SECTORS}
    groups[f"{GAME_NAME} - Coffee"] = {f"{GAME_NAME} - {name} Sector - Coffee"
                                       for _, name, has_coffee in SECTORS if has_coffee}
    groups[f"{GAME_NAME} - Tank Colours"] = {f"{GAME_NAME} - Tank Colour {letter}" for letter in TANK_COLOURS}
    groups[f"{GAME_NAME} - NPCs"] = {f"{GAME_NAME} - Talk to {who}" for who in NPCS.values()}
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
