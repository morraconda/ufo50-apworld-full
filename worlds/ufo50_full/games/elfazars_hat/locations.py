from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
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
# Stage IV (Grand Palace) -- each ticket's own name says which stage it's in. Each is
# its own independent location (not a cumulative ladder): every o31_Ticket ranks itself
# 1..3 among its room's 3 tickets by (y, x) on its own first Step (apRank), and the mod
# sends that specific ticket's location on pickup -- see the id layout below. Stage I is
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
    "Tree",         # Stage I   (White Pea)      mini-boss  -- o31_eTank
    "Josie",        # Stage I   (White Pea)      boss       -- o31_eSlorp
    "Train",        # Stage II  (Train)          stage clear (no boss) -- o31_TrainMas
    "Tank",         # Stage III (Frostin Town)   mini-boss  -- o31_ePlo
    "Nan Noon",     # Stage III (Frostin Town)   boss       -- o31_eWozart
    "Necromancer",  # Stage IV  (Grand Palace)   mini-boss  -- o31_eNecrom
    "Grib",         # Stage IV  (Grand Palace)   mini-boss  -- o31_eGryb
    "Elfazar",      # Stage IV  (Grand Palace)   boss       -- o31_eElfazarHum
    "Zalfador",     # Stage V   (Demon Tower)    boss       -- o31_eZalfadorHead
    "Zalcore",      # Stage V   (Demon Tower)    true final boss (no-continue) -- o31_eZalCoreEnd
)
NON_BOSS_LOCATIONS: frozenset[str] = frozenset({"Train"})

# Every boss/mini-boss and every ticket belongs to one of the 5 stages (the ticket's own
# name says which). "Level" = stage number 1..5 for game_helpers.level_id.
LOCATION_STAGE: dict[str, int] = {
    "Tree": 1, "Josie": 1,
    "Train": 2,
    "Tank": 3, "Nan Noon": 3,
    "Necromancer": 4, "Grib": 4, "Elfazar": 4,
    "Zalfador": 5, "Zalcore": 5,
}
TICKET_STAGE: dict[str, int] = {
    **{name: 1 for name in TICKETS[:3]},
    **{name: 3 for name in TICKETS[3:6]},
    **{name: 4 for name in TICKETS[6:9]},
}

# id offset layout inside Elfazar's Hat's 1000-id block, via game_helpers.level_id
# (offset = level * 10 + slot, level = stage 1..5): each stage's bosses take slots
# 0.., in LOCATIONS play order, then that stage's tickets (if any) take the slots
# right after:
#    10/11        Tree / Josie                      (Stage I)
#    12/13/14     White Pea Ticket 1/2/3             (Stage I, after the 2 bosses)
#    20           Train                              (Stage II)
#    30/31        Tank / Nan Noon                     (Stage III)
#    32/33/34     Frostin Town Ticket 1/2/3          (Stage III, after the 2 bosses)
#    40/41/42     Necromancer / Grib / Elfazar        (Stage IV)
#    43/44/45     Grand Palace Ticket 1/2/3          (Stage IV, after the 3 bosses)
#    50/51        Zalfador / Zalcore                  (Stage V)
#   200      Encouragement (filler)
#   501..508 Shoot Down/Left/Right + 4 diagonals + Dash (see items.py)
#   509      Ticket (x9)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    slot: dict[int, int] = {}
    for name in LOCATIONS:
        stage = LOCATION_STAGE[name]
        table[name] = LocationInfo(level_id(stage, slot.get(stage, 0)), _LOC_REGION[name])
        slot[stage] = slot.get(stage, 0) + 1
    for name in TICKETS:
        stage = TICKET_STAGE[name]
        table[name] = LocationInfo(level_id(stage, slot.get(stage, 0)), _LOC_REGION[name])
        slot[stage] = slot.get(stage, 0) + 1
    table["Gift"] = LocationInfo(997, R_GIFT)
    table["Gold"] = LocationInfo(998, R_TOWER)
    table["Cherry"] = LocationInfo(999, R_TOWER)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items -- shooting up is free.
# Josie and White Pea Ticket 3 need a leftward shot; Train needs Shoot Down.
sphere_1_locs: list[str] = ["Tree", *TICKETS[:2]]


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
