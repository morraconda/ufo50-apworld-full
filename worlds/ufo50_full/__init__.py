from typing import Any

from BaseClasses import Tutorial, Region, Item, ItemClassification, Location, Entrance
from Options import OptionError
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import add_rule, set_rule

from .constants import *
from . import options

from .general_items import (cartridge_items, cartridge_item_group, trap_items, trap_item_group,
                            logic_gate_items, logic_gate_item_group)

from .games import (barbuta, porgy, vainger, night_manor, party_house, block_koala, rail_heist, mortol,
                    waldorf, magic_garden, mortol_ii, attactics, kick_club, velgress, campanella_2, warptank,
                    the_big_bell_race, bug_hunter, paint_chase, onion_delivery,
                    campanella_3, star_waspir, elfazars_hat, caramel_caramel, seaside_drive,
                    devilition, fist_hell, avianos, hot_foot, bushido_ball, hyper_contender, pingolf,
                    campanella, planet_zoldath, combatants, lords_of_diskonia, cyber_owls,
                    ninpek, rakshasa, valbrace, rock_on_island, camouflage, overbold, divers,
                    grimstone, mooncat, mini_and_max, golfaria, pilot_quest, quibble_race)
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
from .games.campanella_3 import items, locations, regions
from .games.star_waspir import items, locations, regions
from .games.elfazars_hat import items, locations, regions
from .games.caramel_caramel import items, locations, regions
from .games.seaside_drive import items, locations, regions
from .games.devilition import items, locations, regions
from .games.fist_hell import items, locations, regions
from .games.avianos import items, locations, regions
from .games.hot_foot import items, locations, regions
from .games.bushido_ball import items, locations, regions
from .games.hyper_contender import items, locations, regions
from .games.pingolf import items, locations, regions
from .games.campanella import items, locations, regions
from .games.planet_zoldath import items, locations, regions
from .games.combatants import items, locations, regions
from .games.lords_of_diskonia import items, locations, regions
from .games.cyber_owls import items, locations, regions
from .games.ninpek import items, locations, regions
from .games.rakshasa import items, locations, regions
from .games.valbrace import items, locations, regions
from .games.rock_on_island import items, locations, regions
from .games.camouflage import items, locations, regions
from .games.overbold import items, locations, regions
from .games.divers import items, locations, regions
from .games.grimstone import items, locations, regions
from .games.mooncat import items, locations, regions
from .games.mini_and_max import items, locations, regions
from .games.golfaria import items, locations, regions
from .games.pilot_quest import items, locations, regions
from .games.quibble_race import items, locations, regions


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
    "Campanella 3": campanella_3,
    "Star Waspir": star_waspir,
    "Elfazar's Hat": elfazars_hat,
    "Caramel Caramel": caramel_caramel,
    "Seaside Drive": seaside_drive,
    "Devilition": devilition,
    "Fist Hell": fist_hell,
    "Avianos": avianos,
    "Hot Foot": hot_foot,
    "Bushido Ball": bushido_ball,
    "Hyper Contender": hyper_contender,
    "Pingolf": pingolf,
    "Campanella": campanella,
    "Planet Zoldath": planet_zoldath,
    "Combatants": combatants,
    "Lords of Diskonia": lords_of_diskonia,
    "Cyber Owls": cyber_owls,
    "Ninpek": ninpek,
    "Rakshasa": rakshasa,
    "Valbrace": valbrace,
    "Rock On! Island": rock_on_island,
    "Camouflage": camouflage,
    "Overbold": overbold,
    "Divers": divers,
    "Grimstone": grimstone,
    "Mooncat": mooncat,
    "Mini & Max": mini_and_max,
    "Golfaria": golfaria,
    "Pilot Quest": pilot_quest,
    "Quibble Race": quibble_race,
}


# for the purpose of generically making the gift, gold, and cherry locations
unimplemented_ufo50_games: list[str] = [name for name in game_ids.keys() if name not in ufo50_games.keys()]

# doing something like this in the world class itself led to weird errors
temp_ufo50_location_name_to_id = {k: v for game in ufo50_games.values() for k, v in game.locations.get_locations().items()}
for game in unimplemented_ufo50_games:
    base_id = get_game_base_id(game)
    temp_ufo50_location_name_to_id[f"{game} - Gift"] = base_id + 997
    temp_ufo50_location_name_to_id[f"{game} - Gold"] = base_id + 998
    temp_ufo50_location_name_to_id[f"{game} - Cherry"] = base_id + 999


def _game_is_sphere1_only(game_regions: dict[str, Region]) -> bool:
    """True if none of the game's own entrances or locations carry an access rule,
    i.e. every check is reachable the moment you boot the game. An ungated spot
    still holds the shared default rule object, exactly the sentinel ``add_rule``
    itself tests against. Any rule anywhere -- goal locations included -- means the
    game has its own logic and is left out of the blanket sphere-1 lock."""
    for region in game_regions.values():
        for exit_ in region.exits:
            if exit_.access_rule is not Entrance.access_rule:
                return False
        for loc in region.locations:
            if loc.access_rule is not Location.access_rule:
                return False
    return True


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
    item_name_to_id.update(trap_items)
    item_name_to_id.update(logic_gate_items)
    item_name_to_id.update({"Intentional Nothing Filler Item": base_id - 100})
    location_name_to_id = temp_ufo50_location_name_to_id

    item_name_groups = {k: v for game in ufo50_games.values() for k, v in game.items.get_item_groups().items()}
    item_name_groups.update(cartridge_item_group)
    item_name_groups.update(trap_item_group)
    item_name_groups.update(logic_gate_item_group)
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
    sphere1_only_games: list[str]  # included games with no internal logic (all checks reachable at boot)
    deferred_sphere1_games: list[str]  # sphere-1-only games; fill gates their Boot entrance behind the Artificial Logic Gates (generator-only)

    porgy_lantern_and_radar_slots_req: dict[str, int]

    def generate_early(self) -> None:
        if not self.player_name.isascii():
            raise OptionError(f"{self.player_name}'s name must be only ASCII.")

        # every game listed in `games` is enabled AND a goal. This is overridden below
        # for universal tracker.
        ut_goal_game_ids: set[int] | None = None

        # for universal tracker support
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if GAME_NAME in self.multiworld.re_gen_passthrough:
                self.ut_passthrough = self.multiworld.re_gen_passthrough[GAME_NAME]
                # sets the games that ended up on as `games`
                id_to_game = {v: k for k, v in game_ids.items()}
                self.options.games.value = {id_to_game[game_id] for game_id in self.ut_passthrough["included_games"]}
                ut_goal_game_ids = set(self.ut_passthrough["goal_games"])

                self.options.porgy_fuel_difficulty.value = self.ut_passthrough[options.PorgyFuelDifficulty.internal_name]
                self.options.porgy_check_on_touch.value = self.ut_passthrough[options.PorgyCheckOnTouch.internal_name]
                self.options.porgy_radar.value = self.ut_passthrough[options.PorgyRadar.internal_name]
                self.options.porgy_lanternless.value = self.ut_passthrough[options.PorgyLanternless.internal_name]
                self.options.defer_sphere_1_games.value = \
                    self.ut_passthrough[options.DeferSphere1Games.internal_name]
                self.options.cherry_enabled_games.value = \
                    set(self.ut_passthrough[options.CherryEnabledGames.internal_name])

        included_game_names = sorted(self.options.games.value)

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
            # every included game is a goal
            self.goal_games = list(included_game_names)

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

        self.sphere1_only_games = []
        self.deferred_sphere1_games = []

        # strict allowlist: a game keeps its Cherry location only if it is listed here.
        # An empty list means NO game has a Cherry.
        cherry_enabled = self.options.cherry_enabled_games.value

        for game_name in self.included_games:
            game = ufo50_games[game_name]
            game_regions = game.regions.create_regions_and_rules(self)
            if game_name not in cherry_enabled:
                self._remove_location(game_regions, f"{game_name} - Cherry")
            for region in game_regions.values():
                self.multiworld.regions.append(region)
            game_menu = self.get_region(f"{game.game_name} - Menu")
            menu.connect(game_menu, f"Boot {game.game_name}",
                         rule=lambda state, name=game.game_name: state.has(f"{name} Cartridge", self.player))
            if _game_is_sphere1_only(game_regions):
                self.sphere1_only_games.append(game_name)

        for game_name in self.included_unimplemented_games:
            locs = {
                f"{game_name} - Gift": self.location_name_to_id[f"{game_name} - Gift"],
                f"{game_name} - Gold": self.location_name_to_id[f"{game_name} - Gold"],
            }
            if game_name in cherry_enabled:
                locs[f"{game_name} - Cherry"] = self.location_name_to_id[f"{game_name} - Cherry"]
            region = Region(f"{game_name} Region", self.player, self.multiworld)
            region.add_locations(locs)
            menu.connect(region, f"Boot {game_name}",
                         rule=lambda state, name=game_name: state.has(f"{name} Cartridge", self.player))

    def _remove_location(self, game_regions: dict[str, Region], loc_name: str) -> None:
        """Drop a just-built location (and its region-cache entry) so it isn't a check."""
        for region in game_regions.values():
            for loc in list(region.locations):
                if loc.name == loc_name:
                    region.locations.remove(loc)
                    return

    def set_rules(self) -> None:
        # run after create_items so self.starting_games is known
        self._lock_sphere1_only_games()

    def _lock_sphere1_only_games(self) -> None:
        """Make fill treat each sphere-1-only game's ``Boot <Game>`` entrance as
        gated behind holding all three Artificial Logic Gate items, so critical-path
        items can't be placed on a game whose every check is open the moment you
        boot it. Generator-only: the gates are never sent to the mod and lock
        nothing in-game. The gate items are added to the pool in ``create_items``,
        which raises ``OptionError`` if there is nowhere reachable to place them."""
        for game_name in self.deferred_sphere1_games:
            add_rule(self.get_entrance(f"Boot {game_name}"),
                     lambda state: all(state.has(gate, self.player) for gate in logic_gate_items))

    def create_item(self, name: str, item_class: ItemClassification = None) -> Item:
        # figure out which game it's from and call its create_item
        game_name = name.split(" - ", 1)[0]
        if game_name in ufo50_games:
            return ufo50_games[game_name].items.create_item(name, self, item_class)
        if name.endswith("Cartridge"):
            item_class = item_class or ItemClassification.progression
        if name in trap_items:
            item_class = item_class or ItemClassification.trap
        if name in logic_gate_items:
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
            candidates = [game for game in included_game_names if game not in self.starting_games]
            self.starting_games += self.random.choices(candidates, k=addtl_games_to_start_with)
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

        # "Defer No Logic Games": fill gates every sphere-1-only game's Boot
        # entrance behind all the Artificial Logic Gate items (rule in
        # _lock_sphere1_only_games) so critical-path items can't land on a game
        # that's fully open at boot. Generator-only, not sent to the mod. The gate
        # items go into the pool here so fill can place them anywhere reachable.
        self.deferred_sphere1_games = []
        if self.options.defer_sphere_1_games:
            self.deferred_sphere1_games = list(self.sphere1_only_games)
            if self.deferred_sphere1_games:
                home_games = {g for g in self.starting_games if g not in self.deferred_sphere1_games}
                open_home_locs = sum(
                    1 for loc in self.multiworld.get_locations(self.player)
                    if loc.item is None and loc.name.split(" - ", 1)[0] in home_games
                )
                if open_home_locs < len(logic_gate_items):
                    raise OptionError(
                        f"{GAME_NAME}: {self.player_name} has 'Defer No Logic Games' on but there is "
                        f"nowhere reachable at the start to place the {len(logic_gate_items)} Artificial "
                        f"Logic Gate items -- every starting game is itself a no-logic game that would be "
                        f"deferred. Raise 'Starting Game Amount', include a game with internal progression, "
                        f"or turn 'Defer No Logic Games' off."
                    )
                created_items += [self.create_item(name) for name in logic_gate_items]

        unfilled_locations = self.multiworld.get_unfilled_locations(self.player)
        extra_items_needed = len(unfilled_locations) - len(created_items)

        if extra_items_needed < 0:
            # A game brings more items than it has open locations -- typically a tight
            # pool that lost its Cherry check (see cherry_enabled_games). Fail rather
            # than silently dropping items.
            raise OptionError(
                f"{GAME_NAME}: {self.player_name} has {-extra_items_needed} more item(s) than open "
                f"locations. Shorten the game list, or add the offending game(s) to "
                f"'Cherry Enabled Games' so their Cherry location is available."
            )

        trap_chance = self.options.trap_percentage.value / 100
        for _ in range(extra_items_needed):
            if trap_chance and self.random.random() < trap_chance:
                created_items.append(self.create_item("Controls Swap Trap"))
            else:
                created_items.append(self.create_item(self.get_filler_item_name(), ItemClassification.filler))

        self.multiworld.itempool += created_items

    # games where the filler is a nothing item, so let's just exclude these where we can
    bad_filler_games: set[str] = {"Night Manor", "Magic Garden", "Attactics", "Warptank",
                                  "Bug Hunter", "The Big Bell Race", "Paint Chase", "Onion Delivery",
                                  "Campanella 3", "Star Waspir", "Elfazar's Hat", "Caramel Caramel",
                                  "Seaside Drive", "Fist Hell", "Avianos", "Hot Foot",
                                  "Bushido Ball", "Hyper Contender", "Pingolf",
                                  "Lords of Diskonia", "Cyber Owls", "Ninpek",
                                  "Rakshasa", "Valbrace", "Rock On! Island", "Camouflage",
                                  "Overbold", "Mooncat", "Golfaria"}

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
            options.WarptankLevelRandomizer.internal_name: self.options.warptank_level_randomizer.value,
            options.DeferSphere1Games.internal_name: self.options.defer_sphere_1_games.value,
            options.CherryEnabledGames.internal_name: sorted(self.options.cherry_enabled_games.value),
            options.DeathLink.internal_name: self.options.death_link.value,
            # game numbers DeathLink applies to; empty list == every game (the mod
            # still gates on `included_games`). Only meaningful when death_link is on.
            options.DeathLinkGames.internal_name: sorted(
                game_ids[name] for name in self.options.deathlink_games.value
            ),
        }
        return slot_data

    # for the universal tracker, doesn't get called in standard gen
    # docs: https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/re-gen-passthrough.md
    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
