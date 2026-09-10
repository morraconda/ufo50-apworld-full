from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Quibble Race"

# region layout:
#   Racing        -- Won <n> Bets (1..15) + Gold (Gold needs no items)
#   Bred Champion  -- Gift  (needs the Breeder item: vanilla GARDEN_WIN fires when a
#                    non-AI player's sponsored quibble wins a race)
#   Cash Empire    -- Cherry (needs all ten shop / thug items)
RACING = "Racing"
BRED = "Bred Champion"
EMPIRE = "Cash Empire"

NUM_RACES = 15

# id offset layout inside Quibble Race's 1000-id block:
#      1..15  Won <n> Bets   (mod counts races where player 0 bet on the winner)
#    200      Encouragement (filler, never granted)
#   997/998/999   Gift / Gold / Cherry


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in range(1, NUM_RACES + 1):
        table[f"Won {n} Bets"] = LocationInfo(n, RACING)
    table["Gift"] = LocationInfo(997, BRED)
    table["Gold"] = LocationInfo(998, RACING)
    table["Cherry"] = LocationInfo(999, EMPIRE)
    return table


location_table: dict[str, LocationInfo] = _build_location_table()


def races_items_needed(n: int) -> int:
    """Items that must be in logic to expect the player to have won ``n`` races."""
    return n // 3


# reachable with no items: Won 1 / 2 Bets (floor(n/3) == 0) and Gold (no item gate)
sphere_1_locs: list[str] = [f"Won {n} Bets" for n in range(1, NUM_RACES + 1)
                            if races_items_needed(n) == 0] + ["Gold"]


def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Won Bets"] = {
        f"{GAME_NAME} - Won {n} Bets" for n in range(1, NUM_RACES + 1)
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
