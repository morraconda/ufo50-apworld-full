from dataclasses import dataclass

from Options import (StartInventoryPool, Range, OptionSet, PerGameCommonOptions, OptionGroup, Choice, Toggle,
                     DeathLink as DeathLinkOption, DefaultOnToggle)

from .constants import game_ids
from .death_link import DEATH_LINK_RULES


class Games(OptionSet):
    """
    Choose which games you want to play. To goal, you must Gold Disk all of them.
    """
    internal_name = "games"
    display_name = "Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default: every game, in death_link.py (DEATH_LINK_RULES) order
    default = list(DEATH_LINK_RULES.keys())


# Games whose Cherry is a genuine "beat basically the whole game" requirement -- kept
# OFF by default so it can't sit deep on the critical path. Everything else gets its
# Cherry by default (mostly no-logic games where it is just another sphere-1 check).
_CHERRY_OFF_BY_DEFAULT: set[str] = {
    "Barbuta", "Campanella", "Golfaria", "Block Koala", "Camouflage", "Porgy",
    "Vainger", "Rock On! Island", "Fist Hell", "Campanella 2", "Valbrace",
    "Elfazar's Hat", "Pilot Quest", "Combatants", "Cyber Owls",
}


class CherryEnabledGames(OptionSet):
    """
    Games listed here will have their "Cherry" location added to the pool. This does not change the Goal condition.
    Games not listed here may still have Cherry-related checks. (eg Night Manor - Fungicide Recipe)
    """
    internal_name = "cherry_enabled_games"
    display_name = "Cherry Enabled Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default: every game except the ones whose Cherry is a deep late-game gate,
    # in death_link.py (DEATH_LINK_RULES) order
    default = [game for game in DEATH_LINK_RULES if game not in _CHERRY_OFF_BY_DEFAULT]


class DeferSphere1Games(DefaultOnToggle):
    """
    If enabled, all games with no logic will have their checks be artificially out of logic behind 3 checks.
    You can still get all checks as soon as you receive the cartridge, they'll just be out of logic.
    This protects against having important early items being locked behind eg. Pilot Quest Cherry.
    If disabled, these games are fully in-logic as soon as you receive the cartridge.
    """
    internal_name = "defer_sphere_1_games"
    display_name = "Defer No Logic Games"


class StartingGameAmount(Range):
    """
    Choose how many games to have unlocked at the start.
    """
    internal_name = "starting_game_amount"
    display_name = "Starting Game Amount"
    range_start = 1
    range_end = 50
    default = 5


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
    Randomize the levels in Block Koala. Does not affect logic.
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
    Randomize which sector each capsule pad warps to. Does not affect logic.
    """
    internal_name = "warptank_level_randomizer"
    display_name = "Warptank - Level Randomizer"


# Traps
class TrapPercentage(Range):
    """
    Replaces this percentage of the filler items in your pool with traps.
    The only trap right now is Controls Swap, which swaps the A and B buttons for 30 seconds.
    """
    internal_name = "trap_percentage"
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 20


class DeathLink(DeathLinkOption):
    """
    When you die, everyone else with DeathLink dies too, and their deaths kill you.
    Each UFO 50 game has its own send / receive condition, which may be asymmetrical.
    Use "Deathlink Games" to restrict DeathLink to a subset of your games.
    """
    internal_name = "death_link"
    display_name = "Death Link"


class DeathLinkGames(OptionSet):
    """
    Which of your games have DeathLink active. Only matters when Death Link is on.
    An explicit empty list means no game has DeathLink; the default is every game.
    """
    internal_name = "deathlink_games"
    display_name = "Deathlink Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default: every game, in death_link.py (DEATH_LINK_RULES) order
    default = list(DEATH_LINK_RULES.keys())


@dataclass
class UFO50Options(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    games: Games
    starting_game_amount: StartingGameAmount
    defer_sphere_1_games: DeferSphere1Games
    cherry_enabled_games: CherryEnabledGames

    porgy_fuel_difficulty: PorgyFuelDifficulty
    porgy_check_on_touch: PorgyCheckOnTouch
    porgy_radar: PorgyRadar
    porgy_lanternless: PorgyLanternless

    nm_early_pin: NMEarlyPin

    block_koala_level_randomizer: BlockKoalaLevelRandomizer
    block_koala_early_start_gate: BlockKoalaEarlyStartGate

    warptank_level_randomizer: WarptankLevelRandomizer

    trap_percentage: TrapPercentage
    death_link: DeathLink
    deathlink_games: DeathLinkGames


ufo50_option_groups = [
    OptionGroup("General Options", [
        Games,
        StartingGameAmount,
        DeferSphere1Games,
        CherryEnabledGames,
        TrapPercentage,
        DeathLink,
        DeathLinkGames,
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
