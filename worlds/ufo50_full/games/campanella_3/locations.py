from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Campanella 3"
UNIT = "Stage"

# Weapon-gated regions (see rules.py / items.py). Forward Shot is needed past Stage A's
# waves; the Upward Beam past Stage D's boss (Eggsaber) and Stage E; the Sideways Beam
# for the Gold/Cherry goals.
R_STAGE_A = "Stage A"
R_ARMED = "Armed"
R_UP_ARMED = "Up Armed"
R_FULLY_ARMED = "Fully Armed"

# Campanella 3 (o08_Mas, global.gv08_stage 0..4) is five stages, each four waves
# followed by a boss -- so every stage is five locations: "Stage <L>-1".."Stage <L>-4"
# then the boss by name. Stage letters + boss names from ext/ENGLISH/8_Text.json
# ("stageText_<s>_0" / "stageText_<s>_2").
STAGES: tuple[tuple[str, str], ...] = (
    ("A", "Galbrain"),
    ("B", "Robopoke"),
    ("C", "Joe Pulp"),
    ("D", "Eggsaber"),
    ("E", "Queen Zu"),
)
NUM_STAGE = len(STAGES)

# id offset layout inside Campanella 3's 1000-id block:
#     stage s (0..4), wave w (1..4):  offset = s * 5 + w    -> 1..4, 6..9, 11..14, ...
#     stage s boss:                   offset = s * 5 + 5    -> 5, 10, 15, 20, 25
#   200      Encouragement (filler)
#   511/512/513   Forward Shot / Upward Beam / Sideways Beam (see items.py)
#   997/998/999   Gift / Gold / Cherry


def _region_for(letter: str, is_boss: bool) -> str:
    if letter == "A" and not is_boss:
        return R_STAGE_A
    if letter == "E" or (letter == "D" and is_boss):
        return R_UP_ARMED
    return R_ARMED


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for s, (letter, boss) in enumerate(STAGES):
        for w in range(1, 5):
            table[f"{UNIT} {letter}-{w}"] = LocationInfo(s * 5 + w, _region_for(letter, False))
        table[boss] = LocationInfo(s * 5 + 5, _region_for(letter, True))
    table["Gift"] = LocationInfo(997, R_ARMED)
    table["Gold"] = LocationInfo(998, R_FULLY_ARMED)
    table["Cherry"] = LocationInfo(999, R_FULLY_ARMED)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# only Stage A's four waves need no weapon
sphere_1_locs: list[str] = [f"{UNIT} A-{w}" for w in range(1, 5)]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    unit_locs = {name for name in location_table if name not in ("Gift", "Gold", "Cherry")}
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {name}" for name in unit_locs}
    for s, (letter, boss) in enumerate(STAGES):
        stage_locs = {f"{GAME_NAME} - {UNIT} {letter}-{w}" for w in range(1, 5)}
        stage_locs.add(f"{GAME_NAME} - {boss}")
        groups[f"{GAME_NAME} - {UNIT} {letter}"] = stage_locs
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
