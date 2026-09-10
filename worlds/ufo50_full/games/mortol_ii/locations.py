from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Mortol II"

# 17 key pickups, 3 coloured switches, 3 bosses.
# KEY_NAMES is in the vanilla A..Q order (offset = index + 1). The names were changed
# 2026-09 to match the annotated map; the per-key access rules (rules.LOCATION_RULES)
# are unchanged -- the region graph only ADDS restrictions on top.
#   A Goober · B Face · C Croc · D Caged · E Bottom-left · F Limbo · G Maze
#   H Subsurface · I Spike · J Switch Stair · K Blobus · L Gorgon Stair · M Worm
#   N Branch · O Castle 1 · P Castle 2 · Q Top-right
KEY_NAMES = (
    "Goober Key", "Face Key", "Croc Key", "Caged Key", "Bottom-left Key",
    "Limbo Key", "Maze Key", "Subsurface Key", "Spike Key", "Switch Stair Key",
    "Blobus Key", "Gorgon Stair Key", "Worm Key", "Branch Key", "Castle Key 1",
    "Castle Key 2", "Top-right Key",
)
SWITCH_COLORS = ("Blue", "Yellow", "Green")
NUM_BOSSES = 3

# The 4 giant worms (o01_eCentipedeHead) -- being eaten by one is a check.
WORM_NAMES = (
    "Large Castle Worm",
    "Small Castle Worm",
    "Ruins Worm",
    "Sewer Worm",
)

# id offset layout inside Mortol II's 1000-id block:
#    1..17   the 17 keys, in KEY_NAMES order
#   21..23   Blue / Yellow / Green Switch
#   31..33   Boss 1 .. Boss 3
#   41..44   the 4 worms, in WORM_NAMES order (eaten by o01_eCentipedeHead)
#   998/999  Gold / Cherry  (both = "beat the game"; this game has no Gift prize)

# Which map area (region, see regions.py) each location sits in. Best-guess from the
# annotated map + the location names. "Start" is the small unlabelled area between Tree
# and Spawning Cave. Empty map regions (Treetop / Entrance / Cave Side Cling) are pure
# traversal nodes.
LOCATION_REGIONS: dict[str, str] = {
    "Goober Key": "Start",
    "Face Key": "Spawning Cave",
    "Croc Key": "Tree",
    "Caged Key": "Left Cave",
    "Bottom-left Key": "Left Cave",
    "Limbo Key": "Deep Cave",
    "Maze Key": "Sewers",
    "Subsurface Key": "Deep Cave",
    "Spike Key": "Lower Ruins",
    "Switch Stair Key": "Upper Ruins",
    "Blobus Key": "Sewers",
    "Gorgon Stair Key": "Lower Ruins",
    "Worm Key": "Lower Castle",
    "Branch Key": "Tree",
    "Castle Key 1": "Upper Castle",
    "Castle Key 2": "Upper Castle",
    "Top-right Key": "Castle Roof",
    "Blue Switch": "Upper Ruins",
    "Yellow Switch": "Lower Ruins",
    "Green Switch": "Lower Ruins",
    "Boss 1": "Arena",
    "Boss 2": "Lower Castle",
    "Boss 3": "Final Corridor",
    "Large Castle Worm": "Lower Castle",
    "Small Castle Worm": "Lower Castle",
    "Ruins Worm": "Lower Ruins",
    "Sewer Worm": "Sewers",
    "Gold": "Ending",
    "Cherry": "Cherry Ending",   # Ending + 49 more lives
}


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, "LocationInfo"]:
    table: dict[str, LocationInfo] = {}
    for offset, name in enumerate(KEY_NAMES, start=1):
        table[name] = LocationInfo(offset, LOCATION_REGIONS[name])
    for offset, color in enumerate(SWITCH_COLORS, start=21):
        name = f"{color} Switch"
        table[name] = LocationInfo(offset, LOCATION_REGIONS[name])
    for n in range(1, NUM_BOSSES + 1):
        name = f"Boss {n}"
        table[name] = LocationInfo(30 + n, LOCATION_REGIONS[name])
    for offset, name in enumerate(WORM_NAMES, start=41):
        table[name] = LocationInfo(offset, LOCATION_REGIONS[name])
    # goal locations last so create_locations' Cherry/Gold handling can break out safely
    table["Gold"] = LocationInfo(998, LOCATION_REGIONS["Gold"])
    table["Cherry"] = LocationInfo(999, LOCATION_REGIONS["Cherry"])
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# "Goober Key" (vanilla Key A) is the only location reachable with no items ("Always"
# rule, in the free "Start" region).
sphere_1_locs: list[str] = ["Goober Key"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Keys"] = {f"{GAME_NAME} - {name}" for name in KEY_NAMES}
    groups[f"{GAME_NAME} - Switches"] = {f"{GAME_NAME} - {c} Switch" for c in SWITCH_COLORS}
    groups[f"{GAME_NAME} - Bosses"] = {f"{GAME_NAME} - Boss {n}" for n in range(1, NUM_BOSSES + 1)}
    groups[f"{GAME_NAME} - Worms"] = {f"{GAME_NAME} - {name}" for name in WORM_NAMES}
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
