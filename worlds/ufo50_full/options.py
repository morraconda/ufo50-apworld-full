from dataclasses import dataclass

from Options import (StartInventoryPool, Range, OptionSet, PerGameCommonOptions, OptionGroup, Choice, Toggle,
                     DefaultOnToggle)

from .constants import game_ids


class Games(OptionSet):
    """
    Choose which games you want to play. Every game listed here is enabled and is a
    goal: to finish, you must get Gold in all of them.

    The following games have full implementations: Barbuta, Vainger, Night Manor, and Porgy.
    Party House has a more minor implementation, and counts as an implemented game.
    Any game may be selected. Games without a full implementation only have Gift,
    Gold, and Cherry locations.
    """
    internal_name = "games"
    display_name = "Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default is here so the unit tests don't fail
    default = ["Barbuta"]


class CherryDisabledGames(OptionSet):
    """
    Games listed here have their Cherry location removed -- it will not be a check.
    Listing a game you are not playing does nothing. The Gift and Gold locations are
    unaffected.
    """
    internal_name = "cherry_disabled_games"
    display_name = "Cherry Disabled Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}


class DeferSphere1Games(DefaultOnToggle):
    """
    If enabled, any included game whose every check is reachable the moment you boot
    it ("sphere 1 only" games) is locked until you have beaten (reached the Gold
    condition of) at least half -- rounded down -- of your included games. This keeps
    those games from being a pile of free early checks. A game you start with is
    exempt, and the lock is skipped entirely if too few other games could satisfy it.

    Disable this for the old behaviour, where those games are playable from the start.
    """
    internal_name = "defer_sphere_1_games"
    display_name = "Defer Sphere 1 Games"


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
    Determine how much fuel you need to get locations.
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
    If enabled, the Hairpin will be on the floor in the starting room on either the Bowl or Spoon locations.
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


# Warptank
class WarptankLevelRandomizer(Toggle):
    """
    Randomize which sector each capsule pad warps to, seeded by the multiworld seed.
    Clearing a pad still sends that pad's own sector check. The final sector is never
    randomized, and the Orb / Garl / Kraft arena sectors only shuffle among each other.
    Does not affect logic.
    """
    internal_name = "warptank_level_randomizer"
    display_name = "Warptank - Level Randomizer"


@dataclass
class UFO50Options(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    games: Games
    starting_game_amount: StartingGameAmount
    defer_sphere_1_games: DeferSphere1Games
    cherry_disabled_games: CherryDisabledGames

    porgy_fuel_difficulty: PorgyFuelDifficulty
    porgy_check_on_touch: PorgyCheckOnTouch
    porgy_radar: PorgyRadar
    porgy_lanternless: PorgyLanternless

    nm_early_pin: NMEarlyPin

    block_koala_level_randomizer: BlockKoalaLevelRandomizer
    block_koala_early_start_gate: BlockKoalaEarlyStartGate

    warptank_level_randomizer: WarptankLevelRandomizer


ufo50_option_groups = [
    OptionGroup("General Options", [
        Games,
        StartingGameAmount,
        DeferSphere1Games,
        CherryDisabledGames,
    ]),
    OptionGroup("Block Koala Options", [
        BlockKoalaLevelRandomizer,
        BlockKoalaEarlyStartGate,
    ]),
    OptionGroup("Warptank Options", [
        WarptankLevelRandomizer,
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
