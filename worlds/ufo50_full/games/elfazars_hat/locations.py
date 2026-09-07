from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Elfazar's Hat"

# Movement/aim-gated regions (see rules.py / items.py). You start able to shoot up and
# nothing else. Stages 3-4 need the dash + the other three cardinals; Stage 5 (and the
# Gold/Cherry goals) also need the four diagonals.
R_START = "Stages 1-2"
R_GIFT = "Ticket Gate"
R_CARDINAL = "Cardinal Zone"
R_TOWER = "Demon Tower"

_LOC_REGION: dict[str, str] = {
    "Tree": R_START, "Josie": R_START, "Train": R_START,
    "Tank": R_CARDINAL, "Nan Noon": R_CARDINAL, "Necromancer": R_CARDINAL,
    "Grib": R_CARDINAL, "Elfazar": R_CARDINAL,
    "Zalfador": R_TOWER, "Zalcore": R_TOWER,
}

# The nine tickets, three each in Stage I (White Pea), Stage III (Frostin Town) and
# Stage IV (Grand Palace). Sent cumulatively as global.g31_ticketsFound climbs (see the
# mod's o31_Player_Step_0 patch), so offset = 10 + ticketsFound in play order. Stage I is
# free (up-shot only); the Frostin Town / Grand Palace tickets need the full cardinal kit.
TICKETS: tuple[str, ...] = (
    "White Pea Ticket 1", "White Pea Ticket 2", "White Pea Ticket 3",
    "Frostin Town Ticket 1", "Frostin Town Ticket 2", "Frostin Town Ticket 3",
    "Grand Palace Ticket 1", "Grand Palace Ticket 2", "Grand Palace Ticket 3",
)
for _name in TICKETS[:3]:
    _LOC_REGION[_name] = R_START
for _name in TICKETS[3:]:
    _LOC_REGION[_name] = R_CARDINAL

# One location per boss fight, in play order across the 5 stages (rm31_Elfazar_lv1..5).
# Stage II (Train) has no boss -- its location is sent on clearing the stage instead.
# "Josie"/"Nan Noon"/"Elfazar"/"Zalfador"/"Zalcore" are the HUD boss names
# (ext/ENGLISH/31_Text.json "bossName1".."bossName5"); the mini-boss names
# ("Tree"/"Tank"/"Necromancer"/"Grib") have no in-game text and are the community
# names the user supplied.
LOCATIONS: tuple[str, ...] = (
    "Tree",         # 1   Stage I   (White Pea)      mini-boss  -- o31_eTank
    "Josie",        # 2   Stage I   (White Pea)      boss       -- o31_eSlorp
    "Train",        # 3   Stage II  (Train)          stage clear (no boss) -- o31_TrainMas
    "Tank",         # 4   Stage III (Frostin Town)   mini-boss  -- o31_ePlo
    "Nan Noon",     # 5   Stage III (Frostin Town)   boss       -- o31_eWozart
    "Necromancer",  # 6   Stage IV  (Grand Palace)   mini-boss  -- o31_eNecrom
    "Grib",         # 7   Stage IV  (Grand Palace)   mini-boss  -- o31_eGryb
    "Elfazar",      # 8   Stage IV  (Grand Palace)   boss       -- o31_eElfazarHum
    "Zalfador",     # 9   Stage V   (Demon Tower)    boss       -- o31_eZalfadorHead
    "Zalcore",      # 10  Stage V   (Demon Tower)    true final boss (no-continue) -- o31_eZalCoreEnd
)
NON_BOSS_LOCATIONS: frozenset[str] = frozenset({"Train"})

# id offset layout inside Elfazar's Hat's 1000-id block:
#     1..10  <boss name>       (offset = play-order position in LOCATIONS)
#    11..19  White Pea / Frostin Town / Grand Palace Ticket 1..3 (play order)
#   200      Encouragement (filler)
#   501..508 Shoot Down/Left/Right + 4 diagonals + Dash (see items.py)
#   509      Ticket (x9)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(LOCATIONS, start=1):
        table[name] = LocationInfo(n, _LOC_REGION[name])
    for n, name in enumerate(TICKETS, start=11):
        table[name] = LocationInfo(n, _LOC_REGION[name])
    table["Gift"] = LocationInfo(997, R_GIFT)
    table["Gold"] = LocationInfo(998, R_TOWER)
    table["Cherry"] = LocationInfo(999, R_TOWER)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items -- shooting up is free (the White Pea tickets included)
sphere_1_locs: list[str] = ["Tree", "Josie", *TICKETS[:3]]   # Train now needs Shoot Down


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Bosses"] = {
        f"{GAME_NAME} - {name}" for name in LOCATIONS if name not in NON_BOSS_LOCATIONS
    }
    groups[f"{GAME_NAME} - Tickets"] = {f"{GAME_NAME} - {name}" for name in TICKETS}
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
