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
# Every run of a level starts with BASE_TIME seconds and no bullets (Level 1 is the
# exception, see LEVEL_1_START_TIME). Time is extended by two item types:
#   * "All Levels +2 Seconds"  - global, flat, additive            (x20 in the pool)
#   * "<level> Time"           - grants that level's full speed-star time budget,
#                               LEVEL_STAR_TIME[level]              (x1 each, per level)
#
# get_run_time() returns how many seconds are bankable on a given level.
# has_time() compares that against a per-check requirement.
# has_bullets() is the boolean "do you have this level's bullets" check.
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

# Level 1 is hardcoded to start with a bigger clock so all of its checks are in logic
# with zero items -- it is the guaranteed sphere-1 seed for the fill (Garden used to
# fill that role but is now pushed back to Level 10).
# Keep this >= LEVEL_STAR_TIME[1] + DEVIL_TIME_BONUS (Level 1's hardest check).
LEVEL_1_START_TIME: int = 54


def get_run_time(level: int, state: CollectionState, world: "UFO50World") -> int:
    player = world.player
    start = LEVEL_1_START_TIME if level == 1 else BASE_TIME
    seconds = start + PLUS_2_VALUE * state.count(plus_2_seconds, player)
    if state.has(level_time_item(level), player):
        seconds += LEVEL_STAR_TIME[level]
    return seconds


def has_time(amount: int, level: int, state: CollectionState, world: "UFO50World") -> bool:
    return get_run_time(level, state, world) >= amount


def has_bullets(level: int, state: CollectionState, world: "UFO50World") -> bool:
    return state.has(level_bullets_item(level), world.player)


# ---------------------------------------------------------------------------
# Per-check requirements
#
# Time needed, relative to the level's speed-star time:
#   Clear       = LEVEL_STAR_TIME[level]
#   Angel Star  = LEVEL_STAR_TIME[level] + ANGEL_TIME_BONUS
#   Devil Star  = LEVEL_STAR_TIME[level] + DEVIL_TIME_BONUS
#
# Bullets: only the Devil Star needs them (you have to gun down every officer) -- except
# on the levels in ALL_BULLET_LEVELS, where every check needs bullets. Level 1's Devil
# Star is exempt from the bullet requirement so all three Level 1 checks stay in logic
# with zero items.
# ---------------------------------------------------------------------------

ANGEL_TIME_BONUS: int = 10
DEVIL_TIME_BONUS: int = 30

CHECK_TIME_BONUS: dict[str, int] = {
    CLEAR: 0,
    ANGEL: ANGEL_TIME_BONUS,
    DEVIL: DEVIL_TIME_BONUS,
}

# levels where every check needs bullets, not just the Devil Star
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
    if level == 1:  # sphere-1 seed: keep every Level 1 check reachable with zero items
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

    # Garden: comes into logic once Level 10 ("Daring Duo") can be cleared
    set_rule(world.get_location(f"{GAME_NAME} - Garden"),
             make_check_rule(10, CLEAR, world))

    # Gold goal: clear every level (enough time for each level's star budget)
    set_rule(world.get_location(f"{GAME_NAME} - Gold"),
             lambda state: all(has_time(LEVEL_STAR_TIME[lvl], lvl, state, world)
                               for lvl in range(1, NUM_LEVELS + 1)))

    # Cherry goal: earn every Devil Star
    if GAME_NAME in world.options.cherry_allowed_games:
        devil_rules = [make_check_rule(lvl, DEVIL, world) for lvl in range(1, NUM_LEVELS + 1)]
        set_rule(world.get_location(f"{GAME_NAME} - Cherry"),
                 lambda state: all(r(state) for r in devil_rules))
