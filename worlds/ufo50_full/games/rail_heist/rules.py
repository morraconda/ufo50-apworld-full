from typing import TYPE_CHECKING, Callable, NamedTuple

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from .locations import location_table, LEVEL_NAMES, NUM_LEVELS, CLEAR, ANGEL, DEVIL

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Rail Heist"

plus_2_seconds = f"{GAME_NAME} - All Levels +2 Seconds"


def level_time_item(level: int) -> str:
    return f"{GAME_NAME} - {LEVEL_NAMES[level]} Time"


def level_bullets_item(level: int) -> str:
    return f"{GAME_NAME} - {LEVEL_NAMES[level]} Bullets"


# ---------------------------------------------------------------------------
# Time model
#
# Every run of a level starts with BASE_TIME seconds and no bullets. Time is extended
# by two item types:
#   * "All Levels +2 Seconds"  - global, flat, additive            (x20 in the pool)
#   * "<level> Time"           - grants that level's full speed-star time budget,
#                               LEVEL_STAR_TIME[level]              (x1 each, per level)
#
# "A Simple Heist Time" (Level 1's "<level> Time") is precollected -- see
# items.create_items -- and, for Level 1 only, also grants the Devil Star buffer, so
# all three "A Simple Heist" locations are the sphere-1 seed for the fill with no other
# items. This replaces the old hardcoded LEVEL_1_START_TIME.
#
# get_run_time() returns how many seconds are bankable on a given level.
# has_time() compares that against a per-location requirement.
# has_bullets() is the boolean "do you have this level's bullets" test.
#
# The filler item "All Levels +1 Second" also adds time in-game, but it's filler-
# classified so logic does NOT count it -- it's a pure bonus (a player who has some
# is ahead of logic, which is the safe direction).
# ---------------------------------------------------------------------------

BASE_TIME: int = 10          # seconds you start every level with (game's premise)
PLUS_2_VALUE: int = 2        # seconds per "All Levels +2 Seconds"

# Real "Star" (speed medal) target time in seconds for each level, from the game data
# in gml_Object_o13_Game_Other_21.gml (scr13_CreateLevel): a level's Star is awarded
# when finalTime <= starGoal. This is the per-level time budget the logic uses.
LEVEL_STAR_TIME: dict[int, int] = {
    1: 24,   2: 30,   3: 49,   4: 31,   5: 54,
    6: 33,   7: 36,   8: 44,   9: 36,  10: 47,
    11: 31,  12: 27,  13: 36,  14: 54,  15: 40,
    16: 76,  17: 45,  18: 50,  19: 53,  20: 94,
}

def get_run_time(level: int, state: CollectionState, world: "UFO50World") -> int:
    player = world.player
    seconds = BASE_TIME + PLUS_2_VALUE * state.count(plus_2_seconds, player)
    if state.has(level_time_item(level), player):
        seconds += LEVEL_STAR_TIME[level]
        # Level 1's "Time" item is the sphere-1 seed (it's precollected -- see
        # items.create_items). It grants the Devil Star buffer too, so all three of
        # "A Simple Heist"'s locations are reachable with no other items.
        if level == 1:
            seconds += DEVIL_TIME_BONUS
    return seconds


def has_time(amount: int, level: int, state: CollectionState, world: "UFO50World") -> bool:
    return get_run_time(level, state, world) >= amount


def has_bullets(level: int, state: CollectionState, world: "UFO50World") -> bool:
    return state.has(level_bullets_item(level), world.player)


# ---------------------------------------------------------------------------
# Per-location requirements
#
# Time needed, relative to the level's speed-star time:
#   Clear       = LEVEL_STAR_TIME[level]
#   Angel Star  = LEVEL_STAR_TIME[level] + ANGEL_TIME_BONUS
#   Devil Star  = LEVEL_STAR_TIME[level] + DEVIL_TIME_BONUS
#
# Bullets: only the Devil Star needs them (you have to gun down every officer) -- except
# on the levels in ALL_BULLET_LEVELS, where every location needs bullets. Level 1's Devil
# Star is exempt so all three "A Simple Heist" locations are reachable with only its
# (precollected) Time item.
# ---------------------------------------------------------------------------

ANGEL_TIME_BONUS: int = 10
DEVIL_TIME_BONUS: int = 30

# Vanilla Cherry: clear every level and hold at least this many of the 60 stars
# (speed Star / Angel / Devil across the 20 levels). From CHERRY_GOAL in
# gml_Object_o13_Game_Create_0.gml.
CHERRY_GOAL: int = 40

CHECK_TIME_BONUS: dict[str, int] = {
    CLEAR: 0,
    ANGEL: ANGEL_TIME_BONUS,
    DEVIL: DEVIL_TIME_BONUS,
}

# levels where every location needs bullets, not just the Devil Star
_ALL_BULLET_LEVEL_NAMES: frozenset[str] = frozenset({
    "Armored Up",
    "Sitting Ducks",
    "The Final Score",
})
ALL_BULLET_LEVELS: frozenset[int] = frozenset(
    level for level, name in LEVEL_NAMES.items() if name in _ALL_BULLET_LEVEL_NAMES
)


class CheckReq(NamedTuple):
    time: int
    bullets: bool


def get_check_req(level: int, check_type: str) -> CheckReq:
    time = LEVEL_STAR_TIME[level] + CHECK_TIME_BONUS[check_type]
    needs_bullets = check_type == DEVIL or level in ALL_BULLET_LEVELS
    if level == 1:  # sphere-1 seed -- keep every "A Simple Heist" location bullet-free
        needs_bullets = False
    return CheckReq(time=time, bullets=needs_bullets)


def make_check_rule(level: int, check_type: str, world: "UFO50World") -> Callable[[CollectionState], bool]:
    req = get_check_req(level, check_type)

    def rule(state: CollectionState) -> bool:
        if not has_time(req.time, level, state, world):
            return False
        if req.bullets and not has_bullets(level, state, world):
            return False
        return True

    return rule


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    regions["Menu"].connect(regions["Levels"])

    for loc_name, loc_data in location_table.items():
        if loc_data.check_type == "":
            continue
        set_rule(world.get_location(f"{GAME_NAME} - {loc_name}"),
                 make_check_rule(loc_data.level, loc_data.check_type, world))

    # Gift: comes into logic once Level 10 ("Daring Duo") can be cleared
    set_rule(world.get_location(f"{GAME_NAME} - Gift"),
             make_check_rule(10, CLEAR, world))

    # Gold goal: clear every level (enough time for each level's star budget)
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(has_time(LEVEL_STAR_TIME[lvl], lvl, state, world)
                               for lvl in range(1, NUM_LEVELS + 1)))

    # Cherry location: the vanilla condition -- clear every level (the Gold rule) and be
    # able to obtain at least CHERRY_GOAL of the 60 stars (Clear / Angel / Devil on
    # each of the 20 levels).
    star_rules = [make_check_rule(lvl, check_type, world)
                  for lvl in range(1, NUM_LEVELS + 1)
                  for check_type in (CLEAR, ANGEL, DEVIL)]
    set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
             lambda state: all(has_time(LEVEL_STAR_TIME[lvl], lvl, state, world)
                               for lvl in range(1, NUM_LEVELS + 1))
             and sum(1 for r in star_rules if r(state)) >= CHERRY_GOAL)
