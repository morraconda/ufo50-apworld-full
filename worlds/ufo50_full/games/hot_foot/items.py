from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Hot Foot"

# The 12 draftable athletes, in vanilla roster order (o43_Game `chars[1..12]`, from
# JON..JULIE). Item id offset = 100 + roster index. Names are the in-game display
# names (ext/ENGLISH/43_Text.json char keys). Every game is winnable with any team,
# so nothing in logic requires a specific athlete -- the items just widen your draft.
CHARACTERS: tuple[str, ...] = (
    "Jerry",    # 1  japes
    "Amy",      # 2  amy
    "Chandar",  # 3  chandar
    "Benjy",    # 4  derk
    "Rizzik",   # 5  rizzik
    "Bea",      # 6  bea
    "Yoka",     # 7  yoka
    "Suze",     # 8  suze
    "Marc",     # 9  marc
    "Edgar",    # 10 gregor
    "Mascot",   # 11 mascot
    "July",     # 12 july
)
NUM_START_CHARS = 3
# The tournament is winnable with any team, so Hot Foot contributes no real filler --
# its filler is the do-nothing Encouragement (Hot Foot is in `bad_filler_games`).
FILLER = "Encouragement"

# id offset layout inside Hot Foot's 1000-id block:
#   101..112   the 12 athletes (CHARACTERS order = roster index 1..12)
#   200        Encouragement (filler)
#   997/998/999   Gift / Gold / Cherry


item_table: dict[str, ItemInfo] = {
    **{name: ItemInfo(100 + i, IC.progression, 1) for i, name in enumerate(CHARACTERS, start=1)},
    FILLER: ItemInfo(200, IC.filler, 0),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    groups = game_item_groups(GAME_NAME, item_table)
    groups[f"{GAME_NAME} - Athletes"] = {f"{GAME_NAME} - {name}" for name in CHARACTERS}
    return groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    # You start with 3 random athletes unlocked; the other 9 are shuffled into the
    # multiworld. When Hot Foot is a goal game its Gold location holds a locked item,
    # so it has one fewer fillable slot -- start with a 4th athlete to keep the counts
    # balanced (pool 8 == 6 Games + Gift + Cherry).
    n_start = NUM_START_CHARS + (1 if GAME_NAME in world.goal_games else 0)
    starters = world.random.sample(CHARACTERS, n_start)
    for name in starters:
        world.multiworld.push_precollected(create_item(name, world))
    return _create_items(GAME_NAME, item_table, world,
                         quantity_overrides={name: 0 for name in starters})


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - {FILLER}"
