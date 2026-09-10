from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Combatants"
CAMPAIGN = "The Campaign"

# Combatants is a real-time strategy campaign of 12 missions + the hidden "Nemuru's
# Way" (o25__Game, `mapComplete[i]` for map node `indexNum` 0..12; node 12 is the
# invisible bonus node). Each location is sent when that mission's node is cleared;
# missions can be tackled in branching order, so no cumulative sweep is needed -- the
# mod just watches the array.
#
# offset == map node indexNum + 1, so the ids are unchanged from the old "Mission N"
# layout; only the display names now use the real `mapN_name` strings.
MISSION_NAMES: tuple[str, ...] = (
    "First Blood",    # indexNum 0  -> offset 1
    "Skirmish",       # indexNum 1  -> offset 2
    "Surprise",       # indexNum 2  -> offset 3
    "Pincered",       # indexNum 3  -> offset 4
    "Ambush",         # indexNum 4  -> offset 5
    "Spidernest",     # indexNum 5  -> offset 6
    "Commando",       # indexNum 6  -> offset 7
    "The Push",       # indexNum 7  -> offset 8
    "Deathsdoor",     # indexNum 8  -> offset 9
    "This Is It",     # indexNum 9  -> offset 10  (vanilla Gold trigger)
    "Open Field",     # indexNum 10 -> offset 11
    "Commando 2",     # indexNum 11 -> offset 12
    "Nemuru's Way",   # indexNum 12 -> offset 13  (hidden bonus node; same reqs as This Is It)
)

# id offset layout inside Combatants's 1000-id block:
#     1..13   <mission name>   (offset = map node indexNum + 1)
#   200       Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry (in gated regions, see rules.py)


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for i, name in enumerate(MISSION_NAMES, start=1):
        table[name] = LocationInfo(i, CAMPAIGN)
    table["Gift"] = LocationInfo(997, "Spider Hunt")
    table["Gold"] = LocationInfo(998, "Final Assault")
    table["Cherry"] = LocationInfo(999, "Total Victory")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no abilities: First Blood and Ambush (rules.py leaves them unruled)
sphere_1_locs: list[str] = ["First Blood", "Ambush"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Missions"] = {f"{GAME_NAME} - {name}" for name in MISSION_NAMES}
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
