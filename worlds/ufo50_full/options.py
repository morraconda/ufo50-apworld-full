from dataclasses import dataclass

from Options import (StartInventoryPool, Range, OptionSet, PerGameCommonOptions, OptionGroup, Choice, Toggle,
                     DefaultOnToggle)

from .constants import game_ids
from .death_link import DEATH_LINK_RULES


class Games(OptionSet):
    """
    Choose which games you want to play. To goal, you must Gold Disk all of them.

    Fully Implemented: (and imo really cool implementations)
        Barbuta, Magic Garden, Velgress, Campanella, Porgy, Party House, Vainger, Campanella 2, Night Manor, Combatants

    Fully Implemented:
        Mortol, Planet Zoldath, Attactics, Devilition, Kick Club, Block Koala, Warptank, Waldorf's Journey,
        Rail Heist, Rock On! Island, Mortol II, Quibble Race

    Somewhat Implemented: (there exists logic, but not much)
        Ninpek, Bushido Ball, Caramel Caramel, Hot Foot, Pingolf, Fist Hell, Overbold, Hyper Contender,
        Rakshasa, Star Waspir, Elfazar's Hat, Seaside Drive, Campanella 3,

    Placeholder Implemented: (All checks are sphere 1, game is not randomised)
        Bug Hunter, Paint Chase, Avianos, Mooncat, Camouflage, Golfaria, The Big Bell Race, Onion Delivery,
        Divers, Valbrace, Grimstone, Lords of Diskonia, Pilot Quest, Mini & Max, Cyber Owls
    """
    internal_name = "games"
    display_name = "Games"
    valid_keys = {game_name for game_name in game_ids.keys() if game_name != "Main Menu"}
    # default: every game, in death_link.py (DEATH_LINK_RULES) order
    default = list(DEATH_LINK_RULES.keys())

_CHERRY_OFF_BY_DEFAULT: set[str] = {
    "Barbuta", "Campanella", "Golfaria", "Block Koala", "Camouflage", "Porgy", "Vainger",
    "Rock On! Island", "Fist Hell", "Valbrace", "Pilot Quest", "Combatants", "Cyber Owls",
}

class StartingGameAmount(Range):
    """
    Choose how many games to have unlocked at the start.
    """
    internal_name = "starting_game_amount"
    display_name = "Starting Game Amount"
    range_start = 1
    range_end = 50
    default = 50

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

class PilotQuestStart(Toggle):
    """
    If enabled, Pilot Quest is guaranteed to be one of your starting cartridges.
    Has no effect if Pilot Quest is not in "Games".
    """
    internal_name = "pilot_quest_start"
    display_name = "Pilot Quest Start"


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


@dataclass
class UFO50Options(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    games: Games
    starting_game_amount: StartingGameAmount
    pilot_quest_start: PilotQuestStart
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


ufo50_option_groups = [
    OptionGroup("General Options", [
        Games,
        StartingGameAmount,
        PilotQuestStart,
        DeferSphere1Games,
        CherryEnabledGames,
        TrapPercentage,
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
