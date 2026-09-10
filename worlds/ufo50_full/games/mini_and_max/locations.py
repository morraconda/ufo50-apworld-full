from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import game_location_groups
from ...goal_locations import is_completion_event_location, place_completion_event
from .items import GAME_NAME, SHRINK_REGION_NAMES

if TYPE_CHECKING:
    from ... import UFO50World


# id offset layout inside Mini & Max's 1000-id block:
#   401..450       "<n> Shinies"   (global.mmStars >= n; offset = 400 + n // 20)
#   997/998/999    Gift / Gold / Cherry
#
# NPC-quest locations are DISABLED for now -- the only checks are the 50 shiny
# thresholds plus Gift / Gold / Cherry. The 50 thresholds are gated on the upgrade
# count (rules.py: 2 upgrades per 100 shinies).
#
# Regions: "Menu", "Hub", the 23 shrink regions (still built so the precollected gate
# items + the mod's ap41_micro_access line up, and so quests can be re-attached later),
# "Ending" (Gold) and "Cherry Ending".


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


# one AP region per shrink region, in the row-major order of items.SHRINK_REGION_IDS
SHRINK_REGIONS: list[str] = list(SHRINK_REGION_NAMES)

# --- shiny thresholds --------------------------------------------------------
SHINY_STEP = 20
SHINY_MAX = 1000
# how many upgrades a "<n> Shinies" check needs: 2 per full 100 shinies (so 20/40/60/80
# are free, 100 needs 2, 200 needs 4, ... 1000 needs 20), capped at the pool total.
SHINY_UPGRADES_PER_100 = 2
SHINY_THRESHOLDS: tuple[int, ...] = tuple(range(SHINY_STEP, SHINY_MAX + 1, SHINY_STEP))


def shiny_loc_name(n: int) -> str:
    return f"{n} Shinies"


def shiny_offset(n: int) -> int:
    return 400 + n // SHINY_STEP


def shiny_upgrades_needed(n: int) -> int:
    """Upgrades required for the '<n> Shinies' check (uncapped)."""
    return (n // 100) * SHINY_UPGRADES_PER_100


def _build_location_table() -> dict[str, LocationInfo]:
    table: dict[str, LocationInfo] = {}
    for n in SHINY_THRESHOLDS:
        table[shiny_loc_name(n)] = LocationInfo(shiny_offset(n), "Hub")
    table["Gift"] = LocationInfo(997, "Hub")
    table["Gold"] = LocationInfo(998, "Ending")
    # Cherry ending is the time-reversal ending set up at the Clock (o41_ClockKeeper,
    # EVENT_CHERRY_QUEST) -- "Cherry Ending" hangs off "Ending" (the full kit) and adds
    # a can_reach("Clock") rule.
    table["Cherry"] = LocationInfo(999, "Cherry Ending")
    return table


location_table: dict[str, LocationInfo] = _build_location_table()

# reachable with no items: Gift + the shiny thresholds that need 0 upgrades
sphere_1_locs: list[str] = [
    "Gift",
    *(shiny_loc_name(n) for n in SHINY_THRESHOLDS if shiny_upgrades_needed(n) == 0),
]


def get_locations() -> dict[str, int]:
    base_id = get_game_base_id(GAME_NAME)
    return {f"{GAME_NAME} - {name}": data.id_offset + base_id
            for name, data in location_table.items()}


def get_location_groups() -> dict[str, set[str]]:
    groups = game_location_groups(GAME_NAME, location_table)
    groups[f"{GAME_NAME} - Shinies"] = {f"{GAME_NAME} - {shiny_loc_name(n)}"
                                        for n in SHINY_THRESHOLDS}
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
