from typing import Any

from BaseClasses import Tutorial, Region, Item, ItemClassification, Location
from Options import OptionError
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import add_rule

from .constants import *
from . import options

from .general_items import cartridge_items, cartridge_item_group

from .games import (barbuta, porgy, vainger, night_manor, party_house, block_koala, rail_heist, mortol,
                    waldorf, magic_garden, mortol_ii, attactics, kick_club, velgress, campanella_2, warptank,
                    the_big_bell_race, bug_hunter, paint_chase, onion_delivery)
from .games.barbuta import items, locations, regions
from .games.porgy import items, locations, regions
from .games.vainger import items, locations, regions
from .games.night_manor import items, locations, regions
from .games.party_house import items, locations, regions
from .games.block_koala import items, locations, regions
from .games.rail_heist import items, locations, regions
from .games.mortol import items, locations, regions
from .games.waldorf import items, locations, regions
from .games.magic_garden import items, locations, regions
from .games.mortol_ii import items, locations, regions
from .games.attactics import items, locations, regions
from .games.kick_club import items, locations, regions
from .games.velgress import items, locations, regions
from .games.campanella_2 import items, locations, regions
from .games.warptank import items, locations, regions
from .games.the_big_bell_race import items, locations, regions
from .games.bug_hunter import items, locations, regions
from .games.paint_chase import items, locations, regions
from .games.onion_delivery import items, locations, regions


_ALL_GAME_NAMES = sorted(name for name in game_ids if name != "Main Menu")


class UFO50Web(WebWorld):
    theme = "partyTime"
    bug_report_page = "https://github.com/UFO-50-Archipelago/Archipelago/issues"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up UFO 50 Full for Archipelago multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["LeonarthCG"]
    )
    tutorials = [setup_en]
    option_groups = options.ufo50_option_groups
    options_presets = {
        # every game enabled (and thus a goal)
        "All Games": {"games": _ALL_GAME_NAMES},
    }


# games with an actual implementation
# add to this list as part of your PR
# try to keep them in the same order as on the main menu
ufo50_games: dict = {
    "Barbuta": barbuta,
    "Mortol II": mortol_ii,
    "Magic Garden": magic_garden,
    "Waldorf's Journey": waldorf,
    "Mortol": mortol,
    "Attactics": attactics,
    "Kick Club": kick_club,
    "Block Koala": block_koala,
    "Porgy": porgy,
    "Rail Heist": rail_heist,
    "Vainger": vainger,
    "Night Manor": night_manor,
    "Party House": party_house,
    "Velgress": velgress,
    "Campanella 2": campanella_2,
    "Warptank": warptank,
    "Bug Hunter": bug_hunter,
    "The Big Bell Race": the_big_bell_race,
    "Paint Chase": paint_chase,
    "Onion Delivery": onion_delivery,
}


# for the purpose of generically making the gift, gold, and cherry locations
unimplemented_ufo50_games: list[str] = [name for name in game_ids.keys() if name not in ufo50_games.keys()]

# doing something like this in the world class itself led to weird errors
temp_ufo50_location_name_to_id = {k: v for game in ufo50_games.values() for k, v in game.locations.get_locations().items()}
for game in unimplemented_ufo50_games:
    base_id = get_game_base_id(game)
    temp_ufo50_location_name_to_id[f"{game} - Garden"] = base_id + 997
    temp_ufo50_location_name_to_id[f"{game} - Gold"] = base_id + 998
    temp_ufo50_location_name_to_id[f"{game} - Cherry"] = base_id + 999


class UFO50World(World):
    """ 
    UFO 50 is a collection of 50 single and multiplayer games from the creators of Spelunky, Downwell, Air Land & Sea,
    Skorpulac, Catacomb Kids, and Madhouse.
    Jump in and explore a variety of genres, from platformers and shoot 'em ups to puzzle games and RPGs.
    Their goal is to combine a familiar 8-bit aesthetic with new ideas and modern game design sensibilities.
    """  # Excerpt from https://50games.fun/
    game = GAME_NAME
    web = UFO50Web()
    required_client_version = (0, 5, 0)
    topology_present = False

    item_name_to_id = {k: v for game in ufo50_games.values() for k, v in game.items.get_items().items()}
    item_name_to_id.update(cartridge_items)
    item_name_to_id.update({"Intentional Nothing Filler Item": base_id - 100})
    location_name_to_id = temp_ufo50_location_name_to_id

    item_name_groups = {k: v for game in ufo50_games.values() for k, v in game.items.get_item_groups().items()}
    item_name_groups.update(cartridge_item_group)
    location_name_groups = {k: v for game in ufo50_games.values() for k, v in game.locations.get_location_groups().items()}

    options_dataclass = options.UFO50Options
    options: options.UFO50Options

    # for universal tracker support
    using_ut: bool
    ut_passthrough: dict[str, Any]
    ut_can_gen_without_yaml = True  # class var that tells it to ignore the player yaml

    included_games: list[str]  # list of games that are going to be played by this player
    included_unimplemented_games: list[str]  # list of included unimplemented games being played by this player

    starting_games: list[str]  # the games you start with unlocked
    goal_games: list[str]  # the games that are your goals

    porgy_lantern_and_radar_slots_req: dict[str, int]

    def generate_early(self) -> None:
        if not self.player_name.isascii():
            raise OptionError(f"{self.player_name}'s name must be only ASCII.")

        # every game listed in `games` is enabled AND a goal; random_choice games are
        # enabled but never goals. This is overridden below for universal tracker.
        ut_goal_game_ids: set[int] | None = None

        # for universal tracker support
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if GAME_NAME in self.multiworld.re_gen_passthrough:
                self.ut_passthrough = self.multiworld.re_gen_passthrough[GAME_NAME]
                # sets the games that ended up on as `games`, turns off random_choice_games
                id_to_game = {v: k for k, v in game_ids.items()}
                self.options.games.value = {id_to_game[game_id] for game_id in self.ut_passthrough["included_games"]}
                self.options.random_choice_games.value.clear()
                self.options.random_choice_game_count.value = 0
                ut_goal_game_ids = set(self.ut_passthrough["goal_games"])

                self.options.porgy_fuel_difficulty.value = self.ut_passthrough[options.PorgyFuelDifficulty.internal_name]
                self.options.porgy_check_on_touch.value = self.ut_passthrough[options.PorgyCheckOnTouch.internal_name]
                self.options.porgy_radar.value = self.ut_passthrough[options.PorgyRadar.internal_name]
                self.options.porgy_lanternless.value = self.ut_passthrough[options.PorgyLanternless.internal_name]

        included_game_names = sorted(self.options.games.value)
        # exclude your `games` from the random choice pool
        maybe_games = sorted(self.options.random_choice_games.value - self.options.games.value)
        # if the number of games you want is higher than the number of games you chose, enable all chosen
        if self.options.random_choice_game_count >= len(maybe_games):
            included_game_names += maybe_games
        elif self.options.random_choice_game_count and maybe_games:
            included_game_names += self.random.sample(maybe_games, self.options.random_choice_game_count.value)

        if not included_game_names:
            raise OptionError(f"{GAME_NAME}: {self.player_name} has not selected any games.")

        self.included_games = []
        self.included_unimplemented_games = []
        for game_name in included_game_names:
            if game_name in ufo50_games.keys():
                self.included_games.append(game_name)
            else:
                self.included_unimplemented_games.append(game_name)

        if ut_goal_game_ids is not None:
            self.goal_games = [name for name in included_game_names if game_ids[name] in ut_goal_game_ids]
        else:
            self.goal_games = [name for name in included_game_names if name in self.options.games.value]

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        victory_location = Location(self.player, "Completed All Games", None, menu)
        victory_location.place_locked_item(Item("Victory", ItemClassification.progression, None, self.player))
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        menu.locations.append(victory_location)

        # every goal game is beaten by reaching its Gold condition
        for game_name in self.goal_games:
            add_rule(victory_location, lambda state, loc=f"{game_name} - Gold":
                     state.can_reach_location(loc, self.player))

        for game_name in self.included_games:
            game = ufo50_games[game_name]
            game_regions = game.regions.create_regions_and_rules(self)
            for region in game_regions.values():
                self.multiworld.regions.append(region)
            game_menu = self.get_region(f"{game.game_name} - Menu")
            menu.connect(game_menu, f"Boot {game.game_name}",
                         rule=lambda state, name=game.game_name: state.has(f"{name} Cartridge", self.player))

        for game_name in self.included_unimplemented_games:
            locs = {
                f"{game_name} - Garden": self.location_name_to_id[f"{game_name} - Garden"],
                f"{game_name} - Gold": self.location_name_to_id[f"{game_name} - Gold"],
                f"{game_name} - Cherry": self.location_name_to_id[f"{game_name} - Cherry"],
            }
            region = Region(f"{game_name} Region", self.player, self.multiworld)
            region.add_locations(locs)
            menu.connect(region, f"Boot {game_name}",
                         rule=lambda state, name=game_name: state.has(f"{name} Cartridge", self.player))

    def create_item(self, name: str, item_class: ItemClassification = None) -> Item:
        # figure out which game it's from and call its create_item
        game_name = name.split(" - ", 1)[0]
        if game_name in ufo50_games:
            return ufo50_games[game_name].items.create_item(name, self, item_class)
        if name.endswith("Cartridge"):
            item_class = item_class or ItemClassification.progression
        return Item(name, item_class or ItemClassification.filler, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        created_items: list[Item] = []
        for game_name in self.included_games:
            game = ufo50_games[game_name]
            created_items += game.items.create_items(self)

        included_game_names = self.included_games + self.included_unimplemented_games
        # check precollected items for cartridges, add them to the starting games list
        precollected_cartridges = set()
        self.starting_games = []
        for item in self.multiworld.precollected_items[self.player]:
            if item.name.endswith("Cartridge"):
                game_name = item.name.split(" Cartridge")[0]
                if game_name not in self.starting_games and game_name in included_game_names:
                    self.starting_games.append(game_name)
                    precollected_cartridges.add(game_name)

        # if your starting game amount is higher than included games, then they're all starting games
        if self.options.starting_game_amount >= len(included_game_names):
            self.starting_games = included_game_names
        else:
            addtl_games_to_start_with = max(self.options.starting_game_amount.value - len(self.starting_games), 0)
            self.starting_games += self.random.choices(
                [game for game in included_game_names if game not in self.starting_games],
                k=addtl_games_to_start_with)
            for game_name in self.starting_games:
                if game_name in ufo50_games.keys():
                    break
            else:
                # remove a game, add an implemented game, unless none are implemented
                # since we're popping, we don't need to worry about removing a precollected cartridge
                if self.included_games and addtl_games_to_start_with > 0:
                    self.starting_games.pop()
                    self.starting_games.append(self.random.choice(self.included_games))

        all_games = self.included_games + self.included_unimplemented_games
        for game_name in all_games:
            cartridge = self.create_item(f"{game_name} Cartridge",
                                         ItemClassification.progression | ItemClassification.useful)
            if game_name in self.starting_games and game_name not in precollected_cartridges:
                self.multiworld.push_precollected(cartridge)
            else:
                created_items.append(cartridge)

        unfilled_locations = self.multiworld.get_unfilled_locations(self.player)
        extra_items_needed = len(unfilled_locations) - len(created_items)

        # debug, delete this later once it all works nicely
        if extra_items_needed < 0:
            raise Exception("Too many items for the number of games, need to fix this somehow.")

        for _ in range(extra_items_needed):
            created_items.append(self.create_item(self.get_filler_item_name(), ItemClassification.filler))

        self.multiworld.itempool += created_items

    # games where the filler is a nothing item, so let's just exclude these where we can
    bad_filler_games: set[str] = {"Night Manor", "Magic Garden", "Attactics", "Warptank",
                                  "Bug Hunter", "The Big Bell Race", "Paint Chase", "Onion Delivery"}

    def get_filler_item_name(self) -> str:
        if not self.included_games:
            return "Intentional Nothing Filler Item"
        good_filler_item_games = [game for game in self.included_games if game not in self.bad_filler_games]
        if not good_filler_item_games:
            good_filler_item_games = self.included_games
        return ufo50_games[self.random.choice(good_filler_item_games)].items.get_filler_item_name(self)

    def fill_slot_data(self) -> dict[str, Any]:
        included_games = [game_ids[game_name] for game_name in self.included_games]
        included_games += [game_ids[game_name] for game_name in self.included_unimplemented_games]
        goal_games = [game_ids[game_name] for game_name in self.goal_games]
        slot_data = {
            "included_games": included_games,
            # every goal game is beaten by reaching its Gold condition (there is no
            # Cherry goal); the client accepts a Cherry as satisfying it too
            "goal_games": goal_games,
            options.PorgyFuelDifficulty.internal_name: self.options.porgy_fuel_difficulty.value,
            options.PorgyCheckOnTouch.internal_name: self.options.porgy_check_on_touch.value,
            options.PorgyRadar.internal_name: self.options.porgy_radar.value,
            options.PorgyLanternless.internal_name: self.options.porgy_lanternless.value,
            options.BlockKoalaLevelRandomizer.internal_name: self.options.block_koala_level_randomizer.value,
        }
        return slot_data

    # for the universal tracker, doesn't get called in standard gen
    # docs: https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/re-gen-passthrough.md
    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
