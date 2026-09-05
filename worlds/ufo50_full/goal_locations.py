"""Shared handling for the per-game Garden / Gold / Cherry goal locations.

Every game's ``location_table`` ends with ``"Garden"``, ``"Gold"``, ``"Cherry"``.
Their treatment is identical across games, so ``create_locations`` should route them
through the helpers here instead of copy-pasting the block:

    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if skip_cherry_location_if_disabled(world, GAME_NAME, loc_name):
            break
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            break
        # ... normal location creation ...
"""

from typing import TYPE_CHECKING

from BaseClasses import Region, Location, Item, ItemClassification
from worlds.generic.Rules import add_rule

if TYPE_CHECKING:
    from . import UFO50World


def cherry_enabled(world: "UFO50World", game_name: str) -> bool:
    """Whether this game has the Cherry goal turned on for this slot."""
    return game_name in world.options.cherry_allowed_games


def skip_cherry_location_if_disabled(world: "UFO50World", game_name: str, loc_name: str) -> bool:
    """The Cherry location does not exist for a game whose Cherry goal is off.

    Garden / Gold / Cherry are always the last entries in a ``location_table``, so the
    caller can ``break`` on a truthy return.
    """
    return loc_name == "Cherry" and not cherry_enabled(world, game_name)


def is_completion_event_location(world: "UFO50World", game_name: str, loc_name: str) -> bool:
    """Whether ``loc_name`` should be replaced with this game's ``"Completed <game>"``
    event: true when ``game_name`` is one of the slot's goal games and ``loc_name`` is
    its goal location -- the Cherry location when the Cherry goal is enabled, otherwise
    the Gold location. Goal locations are last in the table, so the caller can ``break``
    after handling one.
    """
    if game_name not in world.goal_games:
        return False
    goal_loc_name = "Cherry" if cherry_enabled(world, game_name) else "Gold"
    return loc_name == goal_loc_name


def place_completion_event(world: "UFO50World", game_name: str, loc_name: str, region: Region) -> None:
    """Put a locked ``"Completed <game>"`` event at ``loc_name`` and require it for
    ``"Completed All Games"``. Only call this when
    ``is_completion_event_location(world, game_name, loc_name)`` is true.
    """
    event = Location(world.player, f"{game_name} - {loc_name}", None, region)
    event.place_locked_item(Item(f"Completed {game_name}", ItemClassification.progression, None, world.player))
    add_rule(world.get_location("Completed All Games"),
             lambda state, gn=game_name: state.has(f"Completed {gn}", world.player))
    region.locations.append(event)
