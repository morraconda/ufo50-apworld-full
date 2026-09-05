"""Shared boilerplate for the per-game modules under ``games/``.

The world class calls ``get_items`` / ``get_item_groups`` / ``create_item`` /
``create_items`` / ``get_filler_item_name`` on ``<game>.items``, ``get_locations`` /
``get_location_groups`` / ``create_locations`` on ``<game>.locations``, and
``create_regions_and_rules`` on ``<game>.regions`` -- by name, so each game keeps thin
wrappers with those exact signatures and delegates the mechanical parts here.
"""

from typing import TYPE_CHECKING, Callable, NamedTuple, Optional

from BaseClasses import Item, ItemClassification as IC, Region

from .constants import get_game_base_id

if TYPE_CHECKING:
    from . import UFO50World

# a location/item table value -- the helpers only read the attributes named here
TableFilter = Callable[[str, object], bool]


class ItemInfo(NamedTuple):
    """Default ``item_table`` value. Games that need extra fields (e.g. Porgy's
    ``group``) keep their own class; the helpers only read ``id_offset`` /
    ``classification`` / ``quantity``.
    """
    id_offset: int
    classification: IC
    quantity: int = 1


# --- per-level id layout ----------------------------------------------------------

MAX_LEVELS = 50
IDS_PER_LEVEL = 10


def level_id(level: int, slot: int = 0) -> int:
    """Standard id offset for a game whose checks/items are grouped by level.

    ``offset = level * 10 + slot``: level 1 owns offsets 10..19, level 2 owns
    20..29, ... level 50 owns 500..509. Offsets 0..9 stay free for game-wide items,
    and 997/998/999 are the goal locations.

    ``level`` is 1-indexed (1..50); ``slot`` is 0-indexed (0..9) -- one slot per
    check type / item type on that level (e.g. Rail Heist: 0 Clear, 1 Angel, 2 Devil;
    Mortol: 0 level clear, 1..8 life pickups).
    """
    if not 1 <= level <= MAX_LEVELS:
        raise ValueError(f"level {level} out of range 1..{MAX_LEVELS}")
    if not 0 <= slot < IDS_PER_LEVEL:
        raise ValueError(f"slot {slot} out of range 0..{IDS_PER_LEVEL - 1}")
    return level * IDS_PER_LEVEL + slot


# --- items -------------------------------------------------------------------------

def get_items(game_name: str, item_table: dict) -> dict[str, int]:
    """``{"<game> - <item>": id}`` for the whole table -- static, ignores yaml options."""
    base_id = get_game_base_id(game_name)
    return {f"{game_name} - {name}": data.id_offset + base_id for name, data in item_table.items()}


def game_item_groups(game_name: str, item_table: dict) -> dict[str, set[str]]:
    """The required ``{game_name: {every item}}`` group. Merge any game-specific groups
    into the returned dict.
    """
    return {game_name: {f"{game_name} - {name}" for name in item_table}}


def create_item(game_name: str, item_table: dict, item_name: str, world: "UFO50World",
                item_class: IC = None) -> Item:
    """Build one ``Item``. ``item_name`` may be bare or ``"<game> - <name>"``."""
    if item_name.startswith(f"{game_name} - "):
        item_name = item_name.split(" - ", 1)[1]
    data = item_table[item_name]
    return Item(f"{game_name} - {item_name}", item_class or data.classification,
                get_game_base_id(game_name) + data.id_offset, world.player)


def create_items(game_name: str, item_table: dict, world: "UFO50World",
                 quantity_overrides: Optional[dict[str, int]] = None) -> list[Item]:
    """The item pool: ``data.quantity`` copies of each item, with ``quantity_overrides``
    (e.g. ``{"Some Item": 0}``) applied on top.
    """
    quantities = {name: data.quantity for name, data in item_table.items()}
    if quantity_overrides:
        quantities.update(quantity_overrides)
    return [create_item(game_name, item_table, name, world)
            for name, qty in quantities.items() for _ in range(qty)]


# --- locations ---------------------------------------------------------------------

def get_locations(game_name: str, location_table: dict,
                  include: Optional[TableFilter] = None) -> dict[str, int]:
    """``{"<game> - <loc>": id}`` for the table. ``include(name, data)`` can drop
    entries (Vainger uses it to skip its ``id_offset is None`` event locations).
    """
    base_id = get_game_base_id(game_name)
    return {f"{game_name} - {name}": data.id_offset + base_id
            for name, data in location_table.items()
            if include is None or include(name, data)}


def game_location_groups(game_name: str, location_table: dict,
                         include: Optional[TableFilter] = None) -> dict[str, set[str]]:
    """The required ``{game_name: {every location}}`` group. Merge any game-specific
    groups into the returned dict.
    """
    return {game_name: {f"{game_name} - {name}" for name, data in location_table.items()
                        if include is None or include(name, data)}}


# --- regions ---------------------------------------------------------------------

def build_regions(world: "UFO50World", game_name: str, region_names: list[str],
                  create_locations: Callable, create_rules: Optional[Callable] = None,
                  *, prefix_keys: bool = False) -> dict[str, Region]:
    """Create one ``Region`` per name (each titled ``"<game> - <name>"``), run
    ``create_locations`` then ``create_rules`` over the dict, and return it. With
    ``prefix_keys`` the dict is keyed ``"<game> - <name>"`` rather than the bare name.
    """
    def key(name: str) -> str:
        return f"{game_name} - {name}" if prefix_keys else name

    regions = {key(name): Region(f"{game_name} - {name}", world.player, world.multiworld)
               for name in region_names}
    create_locations(world, regions)
    if create_rules is not None:
        create_rules(world, regions)
    return regions
