from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event
from .items import GAME_NAME, PLUS_15, TIER1

if TYPE_CHECKING:
    from ... import UFO50World


REGION = "The Village"
ENDGAME = "Endgame"     # Gold / Cherry -- behind round 10's requirements

# Devilition is a 10-round survival puzzle (o05_Game, `turn` 1..10). Each "Round n"
# location is sent when round n is cleared.
NUM_ROUNDS = 10
ROUND_NAMES: tuple[str, ...] = tuple(f"Round {n}" for n in range(1, NUM_ROUNDS + 1))

# Villager (townie) count checks. Each is "tied to" a round -- its logic is that
# round's requirements. villager count -> round.
VILLAGER_ROUND: dict[int, int] = {3: 1, 4: 2, 5: 4, 6: 6}

# id offset layout inside Devilition's 1000-id block:
#     1..10   Round <n>
#    11..14   <n> Villagers   (offset = 8 + n, n = 3..6)
#    15       "0=0"           (cleared a round with 0 villagers alive)
#   100/101/102   Tier 1 Pieces / +15 Pieces / +5 Pieces
#   997/998/999   Gift / Gold / Cherry

PYRRHIC_LOC = "0=0"     # beat a round with 0 villagers left

TIER1_FROM_ROUND = 4     # rounds >= this also need Tier 1 Pieces


def round_requirements(n: int) -> list[tuple[str, int]]:
    """(item, count) requirements to reach/clear round n: (n-1) "+15 Pieces", plus
    "Tier 1 Pieces" from round 4 on. Round 1 has none."""
    reqs: list[tuple[str, int]] = []
    if n - 1 > 0:
        reqs.append((PLUS_15, n - 1))
    if n >= TIER1_FROM_ROUND:
        reqs.append((TIER1, 1))
    return reqs


def villager_loc_name(v: int) -> str:
    return f"{v} Villagers"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n, name in enumerate(ROUND_NAMES, start=1):
        table[name] = LocationInfo(n, REGION)
    for v in VILLAGER_ROUND:
        table[villager_loc_name(v)] = LocationInfo(8 + v, REGION)
    table[PYRRHIC_LOC] = LocationInfo(15, REGION)
    table["Gift"] = LocationInfo(997, REGION)
    table["Gold"] = LocationInfo(998, ENDGAME)
    table["Cherry"] = LocationInfo(999, ENDGAME)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items: round 1, the villager check tied to round 1, "0=0"
# (Gift is level-5 logic; Gold/Cherry are level-10)
sphere_1_locs: list[str] = ["Round 1", villager_loc_name(3), PYRRHIC_LOC]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Rounds"] = {f"{GAME_NAME} - {name}" for name in ROUND_NAMES}
    groups[f"{GAME_NAME} - Villagers"] = {f"{GAME_NAME} - {villager_loc_name(v)}"
                                          for v in VILLAGER_ROUND}
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
