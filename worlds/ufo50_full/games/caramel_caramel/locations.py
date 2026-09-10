from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Caramel Caramel"
UNIT = "Level"
REGION = "The Shoot"

# Level display names by normalizedLevel 1..6 (the same numbering scr46_SaveGame
# uses for highestLevel), from ext/ENGLISH/46_Text.json "level_1".."level_7".
# The one-off PROLOGUE (room level 5) normalizes back to 1, so it is not its own
# location; FINALE (room level 6) is normalizedLevel 6.
LEVEL_NAMES: tuple[str, ...] = (
    "Snack Planet",
    "Orb Shower A",
    "Ghost Planet",
    "Orb Shower B",
    "Dino Planet",
    "Finale",
)
NUM_LEVEL = len(LEVEL_NAMES)

# Two named bosses, defeated (their enemy object's Destroy at life < 1):
#   Cookie -> o46_eBella ; Toad -> o46_eToadead
BOSS_NAMES: tuple[str, ...] = ("Cookie", "Toad")

# The three planet levels (Snack / Ghost / Dino) each hide one photographable letter
# (global.g46_letters[0..2]) -- together they spell "UFO". Photographing one sends
# "<planet> - '<letter>'".
LETTER_LEVELS: tuple[tuple[str, str], ...] = (
    ("Snack Planet", "U"),
    ("Ghost Planet", "F"),
    ("Dino Planet", "O"),
)

# id offset layout inside Caramel Caramel's 1000-id block:
#     1..3         Cookie / Toad / Complete Prologue  (game-wide milestones)
#   level_id(n,0)  <level name>   (CLEARED normalizedLevel n: 10 / 20 / .. / 60)
#   level_id(n,1)  <planet> - '<letter>'  (photographed that level's hidden letter --
#                  Snack n=1 -> 11 / Ghost n=3 -> 31 / Dino n=5 -> 51)
#   200            Encouragement (filler, never granted)
#   997/998/999    Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _norm_level(planet: str) -> int:
    """normalizedLevel (1..6) for a planet name -- its 1-indexed position in LEVEL_NAMES."""
    return LEVEL_NAMES.index(planet) + 1


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for i, name in enumerate(BOSS_NAMES, start=1):
        table[name] = LocationInfo(i, REGION)
    table["Prologue"] = LocationInfo(3, REGION)
    for n, name in enumerate(LEVEL_NAMES, start=1):
        table[name] = LocationInfo(level_id(n, 0), REGION)
    for planet, letter in LETTER_LEVELS:
        table[f"{planet} - '{letter}'"] = LocationInfo(level_id(_norm_level(planet), 1), REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items: the Prologue and the Snack Planet letter you can photograph
# without killing anything. Everything else needs the Shooting item (rules.py).
sphere_1_locs: list[str] = ["Prologue", "Snack Planet - 'U'"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    groups[f"{GAME_NAME} - Bosses"] = {f"{GAME_NAME} - {name}" for name in BOSS_NAMES}
    groups[f"{GAME_NAME} - Letters"] = {
        f"{GAME_NAME} - {planet} - '{letter}'" for planet, letter in LETTER_LEVELS
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
