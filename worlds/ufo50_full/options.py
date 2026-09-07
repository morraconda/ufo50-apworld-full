from dataclasses import dataclass

from Options import (StartInventoryPool, Range, OptionSet, PerGameCommonOptions, OptionGroup, Choice, Toggle,
                     DefaultOnToggle, Visibility)

from .constants import game_ids


class Games(OptionSet):
    """
    Choose which games you want to play. Every game listed here is enabled and is a
    goal: to finish, you must get Gold in all of them.

    The following games have full implementations: Barbuta, Vainger, Night Manor, and Porgy.
    Party House has a more minor implementation, and counts as an implemented game.
    Any game may be selected. Games without a full implementation only have Garden,
    Gold, and Cherry checks.
    """
    internal_name = "games"
    display_name = "Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default is here so the unit tests don't fail
    default = ["Barbuta"]


class RandomChoiceGames(OptionSet):
    """
    Choose which games have a chance of being enabled alongside your Games.
    The number that will be enabled is based on the Random Choice Game Count option.
    Random Choice Games are enabled but are never goals.
    """
    internal_name = "random_choice_games"
    display_name = "Random Choice Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}


class RandomChoiceGameCount(Range):
    """
    Choose how many Random Choice Games will be enabled alongside your Games.
    If your Random Choice Game Count is larger than the number of games in your Random Choice Games list, all of them will be enabled.
    """
    internal_name = "random_choice_game_count"
    display_name = "Random Choice Game Count"
    range_start = 0
    range_end = 50
    default = 0
    # this is super unnecessary to show in the spoiler, so just hide it
    visibility = Visibility.template | Visibility.simple_ui | Visibility.complex_ui


class StartingGameAmount(Range):
    """
    Choose how many games to have unlocked at the start.
    At least one of the starting games will always be one of the implemented games, to avoid issues with generation and very early BK.
    If this value is higher than the number of games you selected, you will start with all of them unlocked.
    If you put a game in your start inventory from pool, it will count towards the amount from this option.
    """
    internal_name = "starting_game_amount"
    display_name = "Starting Game Amount"
    range_start = 1
    range_end = 50
    default = 1


class PorgyFuelDifficulty(Choice):
    """
    Determine how much fuel you need to get checks.
    Hard means an efficient route with minimal damage.
    Medium means 25% more fuel than Hard.
    Easy means 50% more fuel than Hard.
    """
    internal_name = "porgy_fuel_difficulty"
    display_name = "Porgy - Fuel Difficulty"
    option_easy = 0
    option_medium = 1
    option_hard = 2
    default = 1


class PorgyCheckOnTouch(Toggle):
    """
    If enabled, you will check a location as soon as you touch it, rather than having to bring it back.
    For a shorter, quicker experience.
    """
    internal_name = "porgy_check_on_touch"
    display_name = "Porgy - Check on Touch"


class PorgyRadar(Choice):
    """
    Choose how the Radar System and its logic behave.
    Always On: The Radar System is always on without needing to equip it or receive it.
    Not Required: The Radar System is not logically required for concealed locations.
    Required: The Radar System is logically required for all concealed locations.
    Required No Tell: The Radar System is logically required for concealed locations without a visual cue.
    """
    internal_name = "porgy_radar"
    display_name = "Porgy - Radar Logic"
    option_always_on = 0
    option_not_required = 1
    option_required = 2
    option_required_no_tell = 3
    default = 2


class PorgyLanternless(Toggle):
    """
    If enabled, you will not logically require the Spotlight in the Abyss area.
    """
    internal_name = "porgy_lanternless"
    display_name = "Porgy - Lanternless"


# Night Manor
class NMEarlyPin(DefaultOnToggle):
    """
    If enabled, the Hairpin will be on the floor in the starting room on either the Bowl or Spoon checks.
    """
    internal_name = "nm_early_pin"
    display_name = "Night Manor - Early Hairpin"


# Block Koala
class BlockKoalaLevelRandomizer(Toggle):
    """
    Randomize the layout/order of levels in Block Koala. Does not affect logic.
    """
    internal_name = "block_koala_level_randomizer"
    display_name = "Block Koala - Level Randomizer"


class BlockKoalaEarlyStartGate(DefaultOnToggle):
    """
    If enabled, the Start Gate will be placed on Level 01.
    """
    internal_name = "block_koala_early_start_gate"
    display_name = "Block Koala - Early Start Gate"


@dataclass
class UFO50Options(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    games: Games
    random_choice_games: RandomChoiceGames
    random_choice_game_count: RandomChoiceGameCount
    starting_game_amount: StartingGameAmount

    porgy_fuel_difficulty: PorgyFuelDifficulty
    porgy_check_on_touch: PorgyCheckOnTouch
    porgy_radar: PorgyRadar
    porgy_lanternless: PorgyLanternless

    nm_early_pin: NMEarlyPin

    block_koala_level_randomizer: BlockKoalaLevelRandomizer
    block_koala_early_start_gate: BlockKoalaEarlyStartGate


ufo50_option_groups = [
    OptionGroup("General Options", [
        Games,
        RandomChoiceGames,
        RandomChoiceGameCount,
        StartingGameAmount,
    ]),
    OptionGroup("Block Koala Options", [
        BlockKoalaLevelRandomizer,
        BlockKoalaEarlyStartGate,
    ]),
    OptionGroup("Porgy Options", [
        PorgyFuelDifficulty,
        PorgyCheckOnTouch,
        PorgyRadar,
        PorgyLanternless,
    ]),
    OptionGroup("Night Manor Options", [
        NMEarlyPin,
    ])
]
