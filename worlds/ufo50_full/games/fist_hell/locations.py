from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Fist Hell"

# Fist Hell is a 5-"scare" beat-em-up (o09__Game, `currLevel` 1..5). Names are the
# scare subtitles (ext/ENGLISH/9_Text.json level_1..5).
LEVEL_NAMES: tuple[str, ...] = (
    "Southside",
    "Ride or Die",
    "The Darkwoods",
    "Boardwalk Bash",
    "Paradiso",
)
NUM_LEVELS = len(LEVEL_NAMES)

# Checks per scare (besides the clear):
#   - "<scare> - Bill <n>": a $5 bill (o09_iCash01) hidden in a breakable. From a full
#     rm09_FistHell parse: 2 / 3 / 3 / 1 / 0 per scare (nine total).
#   - "<scare> - Watch": the $10 dropped by that scare's one killable o09_eUFO. Scares
#     1-4 have a UFO (scr09_LevelGen sectors 2 / 9 / 151 / 24); Paradiso has none.
# Coins ($1, from trash cans / crates) are NOT checks -- they just give cash in-game.
BILLS_PER_LEVEL: tuple[int, ...] = (2, 3, 3, 1, 0)
SCARES_WITH_UFO = 4

# id offset layout inside Fist Hell's 1000-id block (level_id(level, slot) = level*10 + slot):
#    L0        <scare name>          slot 0  -- scare L cleared
#    L1..Lb    <scare name> - Bill <n>
#    L(b+1)    <scare name> - Watch  (scares 1-4)
#   101..103   Jay / Victor / Amy unlock items
#   200 $1 (fill name)   201 $5 (cash/bill, x9)   202 $10 (watch, x4)
#   997/998/999   Gift / Gold / Cherry
#
# Each scare is its own region; a further scare needs $20 more than the last (rules.py).
# Gift is sent on reaching scare 3 -> "Ride or Die" region. Gold/Cherry are the vanilla
# sector-33 endings -> "Paradiso".


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for scare, name in enumerate(LEVEL_NAMES, start=1):
        table[name] = LocationInfo(level_id(scare, 0), name)
        bills = BILLS_PER_LEVEL[scare - 1]
        for n in range(1, bills + 1):
            table[f"{name} - Bill {n}"] = LocationInfo(level_id(scare, n), name)
        if scare <= SCARES_WITH_UFO:
            table[f"{name} - Watch"] = LocationInfo(level_id(scare, bills + 1), name)
    table["Gift"] = LocationInfo(997, "Ride or Die")
    table["Gold"] = LocationInfo(998, "Paradiso")
    table["Cherry"] = LocationInfo(999, "Paradiso")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# with no items only Southside is reachable -- its clear, two bills and watch
sphere_1_locs: list[str] = [
    "Southside", "Southside - Bill 1", "Southside - Bill 2", "Southside - Watch",
]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Scares"] = {f"{GAME_NAME} - {name}" for name in LEVEL_NAMES}
    money: set[str] = set()
    for scare, name in enumerate(LEVEL_NAMES, start=1):
        money.update(f"{GAME_NAME} - {name} - Bill {n}"
                     for n in range(1, BILLS_PER_LEVEL[scare - 1] + 1))
        if scare <= SCARES_WITH_UFO:
            money.add(f"{GAME_NAME} - {name} - Watch")
    groups[f"{GAME_NAME} - Money"] = money
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
