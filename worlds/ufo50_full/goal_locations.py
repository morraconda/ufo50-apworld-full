"""Shared handling for the per-game Garden / Gold / Cherry goal locations.

Every game's ``location_table`` ends with ``"Garden"``, ``"Gold"``, ``"Cherry"``. All
three are always real, sendable checks; the only special case is the slot's goal
games, whose ``"Gold"`` location additionally carries a locked item. ``create_locations``
routes them through the helpers here instead of copy-pasting the block:

    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if is_goal_location(world, GAME_NAME, loc_name):
            place_goal_location(world, GAME_NAME, loc_name, region)
            continue
        # ... normal location creation ...

The goal is always the **Gold** condition. A slot's goal game still gets a *real,
sendable* Gold location (``<base> + 998``) rather than an addressless event: the client
has to be able to send that check so the multiworld records it and it survives a
reconnect. Gen must not put a randomized item there though -- the Gold location is only
reachable once the whole game is beaten, so it carries a locked filler item, exactly as
the old ``"Completed <game>"`` event did. ``"Completed All Games"`` is gated on being
able to reach each goal game's Gold location in ``UFO50World.create_regions``.

``is_completion_event_location`` / ``place_completion_event`` remain as aliases so the
per-game ``create_locations`` blocks don't all have to change.
"""

from typing import TYPE_CHECKING

from BaseClasses import Region, Location

from .constants import get_game_base_id

if TYPE_CHECKING:
    from . import UFO50World


# id offsets of the three goal locations inside a game's 1000-id block
GOAL_LOCATION_OFFSETS: dict[str, int] = {"Garden": 997, "Gold": 998, "Cherry": 999}


def is_goal_location(world: "UFO50World", game_name: str, loc_name: str) -> bool:
    """Whether ``loc_name`` is this game's goal location: true when ``game_name`` is one
    of the slot's goal games and ``loc_name`` is ``"Gold"``. The goal is always the
    Gold condition.
    """
    return game_name in world.goal_games and loc_name == "Gold"


def place_goal_location(world: "UFO50World", game_name: str, loc_name: str, region: Region) -> None:
    """Create this game's Gold location as a real (sendable) location with a locked
    filler item on it, and require reaching it for ``"Completed All Games"``.

    The address is kept so the client can send the check and the server records it
    (surviving a reconnect). The locked item keeps gen from trying to place progression
    behind a "beat the whole game" requirement. Only call this when
    ``is_goal_location(world, game_name, loc_name)`` is true.
    """
    loc = Location(world.player, f"{game_name} - {loc_name}",
                   get_game_base_id(game_name) + GOAL_LOCATION_OFFSETS[loc_name], region)
    loc.place_locked_item(world.create_item(world.get_filler_item_name()))
    region.locations.append(loc)


# --- backwards-compatible aliases (per-game create_locations still import these) -----
is_completion_event_location = is_goal_location
place_completion_event = place_goal_location
