"""Cartridge Item Chains -- a game's Cartridge is folded into one of its own items.

Each game's ``items.py`` names that item in ``cartridge_item`` (``"N/A"`` = no chain).
With the option on, every copy of it is renamed ``"<Game> - Cartridge / <item>"``, one
extra copy replaces the game's Cartridge (two for a single-copy item, the last one a
spare that does nothing -- see ``chain_pool``), and the first copy received counts as the
Cartridge (no gameplay benefit) while every later copy counts as the original item.
Logic sees the same split: ``collect``/``remove`` turn the chained item into virtual
counts of ``"<Game> Cartridge"`` and ``"<Game> - <item>"``, so no rule changes.

Chained ids sit in their own namespace so the mod can decode them without slot_data:
``BASE_ID + (CHAIN_SUBGAME_OFFSET + game)*1000 + <item's own offset>``, i.e. subgame
``100 + game``, item id = the original item's offset.
"""

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Item, ItemClassification as IC

from .constants import BASE_ID, game_ids, get_game_base_id

if TYPE_CHECKING:
    from . import UFO50World

NO_CARTRIDGE_ITEM = "N/A"
CHAIN_SUBGAME_OFFSET = 100


def chain_item_name(game_name: str, item: str) -> str:
    return f"{game_name} - Cartridge / {item}"


def build_chains(games: dict) -> dict[str, tuple[str, str]]:
    """``{chained item name: (game name, original "<Game> - <item>" name)}`` for every
    game whose ``items.cartridge_item`` isn't ``"N/A"``. Static -- ignores yaml options."""
    chains = {}
    for game_name, game in games.items():
        item = game.items.cartridge_item
        if item == NO_CARTRIDGE_ITEM:
            continue
        original = f"{game_name} - {item}"
        if original not in game.items.get_items():
            raise ValueError(f"{game_name}: cartridge_item {item!r} is not one of its items")
        chains[chain_item_name(game_name, item)] = (game_name, original)
    return chains


def chain_item_ids(games: dict, chains: dict[str, tuple[str, str]]) -> dict[str, int]:
    ids = {}
    for name, (game_name, original) in chains.items():
        offset = games[game_name].items.get_items()[original] - get_game_base_id(game_name)
        ids[name] = BASE_ID + (CHAIN_SUBGAME_OFFSET + game_ids[game_name]) * 1000 + offset
    return ids


def active_chains(world: "UFO50World", chains: dict[str, tuple[str, str]],
                  precollected_cartridges: set[str]) -> dict[str, str]:
    """``{game name: chained item name}`` for this slot. Empty when the option is off;
    skips games that aren't included or whose Cartridge is already in start inventory
    (the chain's first copy would otherwise be a wasted second Cartridge)."""
    if not world.options.cartridge_item_chains:
        return {}
    return {game_name: name for name, (game_name, _) in chains.items()
            if game_name in world.included_games and game_name not in precollected_cartridges}


def create_chain_item(world: "UFO50World", name: str) -> Item:
    return Item(name, IC.progression | IC.useful, world.item_name_to_id[name], world.player)


def chain_pool(world: "UFO50World", game_name: str, chained_name: str,
               chains: dict[str, tuple[str, str]], pool: list[Item]) -> list[Item]:
    """Pull every copy of the game's ``cartridge_item`` out of ``pool`` (in place) and
    return one more chained copy than were removed -- the extra one replaces the
    Cartridge. A single-copy item gets two extra instead (3 total: Cartridge, the item,
    then a spare that does nothing), so the item itself isn't always the last one found."""
    original = chains[chained_name][1]
    removed = [item for item in pool if item.name == original]
    pool[:] = [item for item in pool if item.name != original]
    extra = 2 if len(removed) == 1 else 1
    return [create_chain_item(world, chained_name) for _ in range(len(removed) + extra)]


def on_collect(state: CollectionState, player: int, chains: dict[str, tuple[str, str]],
               item: Item) -> None:
    """Call after the base ``collect`` counted ``item``: first copy -> Cartridge,
    later copies -> the original item."""
    if item.name not in chains:
        return
    game_name, original = chains[item.name]
    first = state.prog_items[player][item.name] == 1
    state.add_item(f"{game_name} Cartridge" if first else original, player)


def on_remove(state: CollectionState, player: int, chains: dict[str, tuple[str, str]],
              item: Item) -> None:
    """Call after the base ``remove`` uncounted ``item``; mirrors ``on_collect``."""
    if item.name not in chains:
        return
    game_name, original = chains[item.name]
    last = state.prog_items[player][item.name] == 0
    state.remove_item(f"{game_name} Cartridge" if last else original, player)
