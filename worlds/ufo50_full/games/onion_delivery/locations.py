from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups, level_id
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Onion Delivery"
UNIT = "Day"
NUM_DAY = 7   # the seven-day week (o32_Mas.dayNumber 0..6)
NUM_ONION = 10   # onions on the day's counter (o32_Mas.onionsDelivered[dayNumber])
REGION = "The Route"

# id offset layout inside Onion Delivery's 1000-id block, via game_helpers.level_id
# (offset = level * 10 + slot):
#    10..70   Day <n>   (finished day n; level_id(n, 0))
#   101..103 Throttle / Handbrake / Progressive Top Speed (items)
#   111..120 <n> Onion(s)  (n onions on the counter in a single day; 110 + n)
#   131..155 <stop>   (made a delivery to that stop; 130 + o32_CPoint.num 1..25)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


ONION_BASE = 110
DELIVERY_BASE = 130

# delivery stops by o32_CPoint.num (checkpointName_NN in the game's text). num 0,
# Onion & Sons, is the depot you return to at day end, not a delivery.
DELIVERY_STOPS: dict[int, str] = {
    1: "Onion Park",
    2: "Laydon Papers",
    3: "Savage Sin Inc",
    4: "Quartin Heights",
    5: "Neptude Parking",
    6: "24/7 Juicery",
    7: "Enforce HQ",
    8: "Jurli's",
    9: "Locker B",
    10: "Tetra Park",
    11: "Kylar Projects",
    12: "Slime Factory",
    13: "Uncle Pepper",
    14: "Howl Cemetary",
    15: "The Clumps",
    16: "Slime Refinery",
    17: "City Hall",
    18: "Dyanna Law",
    19: "Central Storage",
    20: "Big Oil Theater",
    21: "Cheap Storage",
    22: "Big Machines",
    23: "Onion Academy",
    24: "Efran Meats",
    25: "Burlett Bakery",
}
SPHERE_1_STOPS: tuple[str, ...] = ("Burlett Bakery", "Onion Park", "Laydon Papers",
                                   "Cheap Storage", "24/7 Juicery")


def onion_loc_name(n: int) -> str:
    return f"{n} Onion" if n == 1 else f"{n} Onions"


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_DAY + 1):
        table[f"{UNIT} {n}"] = LocationInfo(level_id(n, 0), REGION)
    for n in range(1, NUM_ONION + 1):
        table[onion_loc_name(n)] = LocationInfo(ONION_BASE + n, REGION)
    for num, stop in DELIVERY_STOPS.items():
        table[stop] = LocationInfo(DELIVERY_BASE + num, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, REGION)
    table["Cherry"] = LocationInfo(999, REGION)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# tier 1 in rules.py
sphere_1_locs: list[str] = ([onion_loc_name(n) for n in range(1, 6)]
                            + [f"{UNIT} {n}" for n in range(1, 3)] + list(SPHERE_1_STOPS)
                            + ["Gift"])


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - {UNIT}s"] = {f"{GAME_NAME} - {UNIT} {n}" for n in range(1, NUM_DAY + 1)}
    groups[f"{GAME_NAME} - Onions"] = {f"{GAME_NAME} - {onion_loc_name(n)}" for n in range(1, NUM_ONION + 1)}
    groups[f"{GAME_NAME} - Deliveries"] = {f"{GAME_NAME} - {stop}" for stop in DELIVERY_STOPS.values()}
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
