from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Party House"


class Guest(NamedTuple):
    """One of the 43 unlockable guests. ``id`` is the vanilla o36_Game ``CHAR_*``
    type value (11..44 standard, 50..58 prestige); the AP item id/offset is the
    1-based position in ``GUESTS``. ``cost`` is the popularity price to add the
    guest. ``money_score`` / ``pop_score`` / ``util_score`` rate how much the guest
    contributes to cash / popularity / utility (used by ``rules._achieved``). Every
    field after ``cost`` defaults to its zero value and is only passed on a ``GUESTS``
    entry when non-zero/``True``: the score ints (may be negative), then the bools
    ``is_trouble`` (base troublemaker), ``is_star`` (carries prestige -- a "star
    guest"), ``is_flag`` (raises a flag)."""
    name: str
    id: int
    cost: int
    money_score: int = 0
    pop_score: int = 0
    util_score: int = 0
    is_trouble: bool = False
    is_star: bool = False
    is_flag: bool = False


# Rolodex order: the 34 standard characters (CHAR_START..CHAR_END = 11..44) then the 9
# prestige characters (CHAR_PRESTIGE_START..CHAR_PRESTIGE_END = 50..58). The 3 starter
# types (Old Friend / Rich Pal / Wild Buddy) are NOT items -- you always have them.
# Names are the in-game card names (ext/ENGLISH/36_Text.json), de-abbreviated;
# cost/is_trouble/is_star are read from scr36_CreateCard.
GUESTS: list[Guest] = [
    Guest("Dancer", 11, cost=7),
    Guest("Hippy", 12, cost=4, is_flag=True),
    Guest("Cute Dog", 13, cost=7, pop_score=1, is_flag=True),
    Guest("Security", 14, cost=4, util_score=1),
    Guest("Wrestler", 15, cost=9, pop_score=1, util_score=1),
    Guest("Watch Dog", 16, cost=4, pop_score=1, util_score=1),
    Guest("Spy", 17, cost=8, money_score=2, util_score=1),
    Guest("Driver", 18, cost=3, util_score=2),
    Guest("Private I.", 19, cost=4, util_score=2),
    Guest("Grillmaster", 20, cost=5, pop_score=1, util_score=1),
    Guest("Athlete", 21, cost=6, money_score=1, util_score=1),
    Guest("Mr. Popular", 22, cost=5, pop_score=2, util_score=-1),
    Guest("Celebrity", 23, cost=11, money_score=3, pop_score=1, util_score=-1),
    Guest("Comedian", 24, cost=5, pop_score=3),
    Guest("Photographer", 25, cost=5, money_score=1, pop_score=2),
    Guest("Caterer", 26, cost=5, pop_score=2),
    Guest("Ticket Taker", 27, cost=4, money_score=1),
    Guest("Auctioneer", 28, cost=9, money_score=3),
    Guest("Monkey", 29, cost=3, pop_score=2, is_trouble=True),
    Guest("Rock Star", 30, cost=5, money_score=2, pop_score=2, is_trouble=True),
    Guest("Gangster", 31, cost=6, money_score=4, is_trouble=True),
    Guest("Gambler", 32, cost=7, money_score=3, pop_score=1, is_trouble=True),
    Guest("Werewolf", 33, cost=5, pop_score=1),
    Guest("Mascot", 34, cost=5, pop_score=1),
    Guest("Introvert", 35, cost=4, pop_score=1),
    Guest("Counselor", 36, cost=7, is_flag=True),
    Guest("Stylist", 37, cost=7, pop_score=2),
    Guest("Bartender", 38, cost=11, money_score=4),
    Guest("Writer", 39, cost=8, pop_score=3),
    Guest("Social Climber", 40, cost=12, pop_score=3),
    Guest("Cupid", 41, cost=8, util_score=3),
    Guest("Magician", 42, cost=5, util_score=1),
    Guest("Greeter", 43, cost=5, pop_score=1),
    Guest("Cheerleader", 44, cost=5, util_score=2),
    Guest("Alien", 50, cost=40, is_star=True),
    Guest("Dinosaur", 51, cost=25, is_trouble=True, is_star=True),
    Guest("Leprechaun", 52, cost=50, money_score=2, is_star=True),
    Guest("Genie", 53, cost=55, util_score=2, is_star=True),
    Guest("Mermaid", 54, cost=35, util_score=-1, is_star=True),
    Guest("Dragon", 55, cost=30, util_score=-2, is_star=True),
    Guest("Ghost", 56, cost=45, util_score=1, is_star=True),
    Guest("Unicorn", 57, cost=45, is_star=True, is_flag=True),
    Guest("Superhero", 58, cost=50, pop_score=1, is_star=True),
]
NUM_GUESTS = len(GUESTS)
assert NUM_GUESTS == 43

# The guests each fixed scenario's shop offers (from scr36_SetupScenarios), 13 apiece.
# Random Scenario (the 6th) has a randomised pool, so it has no fixed list.
SCENARIO_GUESTS: dict[str, list[str]] = {
    "Alien Invitation": [
        "Alien", "Auctioneer", "Security", "Driver", "Rock Star", "Dancer", "Comedian",
        "Monkey", "Ticket Taker", "Caterer", "Watch Dog", "Hippy", "Mr. Popular",
    ],
    "High or Low": [
        "Wrestler", "Grillmaster", "Gangster", "Spy", "Cute Dog", "Private I.", "Mascot",
        "Writer", "Social Climber", "Introvert", "Gambler", "Superhero", "Mermaid",
    ],
    "Best Wishes": [
        "Photographer", "Stylist", "Hippy", "Celebrity", "Counselor", "Bartender",
        "Athlete", "Cheerleader", "Wrestler", "Monkey", "Rock Star", "Dinosaur", "Genie",
    ],
    "A Magical Night": [
        "Spy", "Private I.", "Photographer", "Comedian", "Ticket Taker", "Caterer",
        "Gangster", "Security", "Athlete", "Stylist", "Cute Dog", "Dragon", "Leprechaun",
    ],
    "Money Management": [
        "Gambler", "Werewolf", "Celebrity", "Cupid", "Introvert", "Auctioneer",
        "Social Climber", "Dancer", "Watch Dog", "Greeter", "Magician", "Unicorn", "Ghost",
    ],
}

_guest_names = {g.name for g in GUESTS}
assert all(name in _guest_names for names in SCENARIO_GUESTS.values() for name in names)

MAX_TROUBLE = "+1 Max Trouble"
SHOP_STOCK = "+1 Shop Stock"
MAX_POPULARITY = "+5 Max Popularity"
MAX_CASH = "+2 Max Cash"
DAY = "+1 Day"
START_POPULARITY = "+1 Starting Popularity"
START_CASH = "+1 Starting Cash"

# The two "starting" items double as this game's filler.
FILLER_NAMES: tuple[str, ...] = (START_POPULARITY, START_CASH)

# id offset layout inside Party House's 1000-id block (game-wide items live in 1..99,
# below scenario 1's 100-id block):
#    1..43   the 43 unlockable guests (GUESTS order): Dancer .. Superhero
#   44       +1 Max Trouble      (x4)
#   45       +1 Shop Stock       (x4)
#   46       +5 Max Popularity   (x18)
#   47       +2 Max Cash         (x14)
#   48       +1 Day              (x25)
#   49       +1 Starting Popularity (x10, also filler)
#   50       +1 Starting Cash    (x10, also filler)
#   locations: see locations.py; 997/998/999 = Gift / Gold / Cherry
item_table: dict[str, ItemInfo] = {
    **{g.name: ItemInfo(i, IC.progression, 1) for i, g in enumerate(GUESTS, start=1)},
    MAX_TROUBLE: ItemInfo(44, IC.progression, 4),
    SHOP_STOCK: ItemInfo(45, IC.progression, 4),
    MAX_POPULARITY: ItemInfo(46, IC.progression, 18),
    MAX_CASH: ItemInfo(47, IC.progression, 14),
    DAY: ItemInfo(48, IC.progression, 25),
    START_POPULARITY: ItemInfo(49, IC.progression, 10),
    START_CASH: ItemInfo(50, IC.progression, 10),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Guests"] = {f"{GAME_NAME} - {g.name}" for g in GUESTS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # 43 guests + the capacity/head-start items (128 total); the framework pads the
    # rest with filler, which is "+1 Starting Popularity" or "+1 Starting Cash".
    return _create_items(GAME_NAME, item_table, world)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - " + world.random.choice(FILLER_NAMES)
