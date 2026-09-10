"""All UFO 50 generation tests.

Every test just builds a multiworld with :func:`generate` and asserts the general
"the goal is possible" properties -- every location reachable with all items, and
the seed fills without deadlock and is beatable. Nothing here pins item counts, ids
or sphere-1 contents.

Every game listed in the ``games`` option is enabled and is a goal (you must get Gold
in all of them). That is the only way to enable a game.

Three groups:
  * ``AllGamesGenerationTest`` -- every implemented game switched on at once.
  * ``PerGameGenerationTest``  -- each game on its own, and in a small mixed
    multiworld. Methods are generated from ``_PER_GAME``.
  * ``OptionMatrixTest``       -- assorted yaml-option combinations that touch code
    paths the above miss (small multiworlds, per-game ``create_items`` branches).
"""

from . import ALL_GAMES, UFO50GenTestBase, generate


class AllGamesGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=7)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_all_goals(self) -> None:
        self._check({"games": ALL_GAMES, "starting_game_amount": 1})

    def test_all_games_all_starting(self) -> None:
        self._check({"games": ALL_GAMES, "starting_game_amount": 50})


# --- per game -----------------------------------------------------------------
# (game name, mixed-multiworld partners, seed)
_PER_GAME: list[tuple[str, list[str], int]] = [
    ("Magic Garden",      ["Barbuta", "Mortol"],     11),
    ("Mortol",            ["Barbuta", "Rail Heist"],   3),
    ("Mortol II",         ["Barbuta", "Mortol"],       1),
    ("Waldorf's Journey", ["Barbuta", "Mortol"],       4),
    ("Rail Heist",        ["Barbuta", "Porgy"],        1),
    ("Attactics",         ["Barbuta", "Mortol"],       5),
    ("Kick Club",         ["Barbuta", "Attactics"],   11),
    ("Party House",       ["Barbuta", "Mortol"],       7),
    ("Velgress",          ["Barbuta", "Mortol"],       2),
    ("Campanella 2",      ["Barbuta", "Mortol"],       6),
    ("Warptank",          ["Barbuta", "Mortol"],       8),
    ("Bug Hunter",        ["Barbuta", "Mortol"],       3),
    ("The Big Bell Race", ["Barbuta", "Mortol"],       5),
    ("Paint Chase",       ["Barbuta", "Mortol"],       9),
    ("Onion Delivery",    ["Barbuta", "Mortol"],       7),
    ("Campanella 3",      ["Barbuta", "Mortol"],       2),
    ("Star Waspir",       ["Barbuta", "Mortol"],       4),
    ("Elfazar's Hat",     ["Barbuta", "Mortol"],       6),
    ("Caramel Caramel",   ["Barbuta", "Mortol"],       1),
    ("Seaside Drive",     ["Barbuta", "Mortol"],       3),
    ("Devilition",        ["Barbuta", "Mortol"],       5),
    ("Fist Hell",         ["Barbuta", "Mortol"],       9),
    ("Avianos",           ["Barbuta", "Mortol"],       2),
    ("Hot Foot",          ["Barbuta", "Mortol"],       6),
    ("Bushido Ball",      ["Barbuta", "Mortol"],       4),
    ("Hyper Contender",   ["Barbuta", "Mortol"],       8),
    ("Pingolf",           ["Barbuta", "Mortol"],       4),
    ("Campanella",        ["Barbuta", "Mortol"],       6),
    ("Planet Zoldath",    ["Barbuta", "Mortol"],       5),
    ("Combatants",        ["Barbuta", "Mortol"],       3),
    ("Lords of Diskonia", ["Barbuta", "Mortol"],       7),
    ("Cyber Owls",        ["Barbuta", "Mortol"],       2),
    ("Ninpek",            ["Barbuta", "Mortol"],       9),
    ("Rakshasa",          ["Barbuta", "Mortol"],       1),
    ("Valbrace",          ["Barbuta", "Mortol"],       5),
    ("Rock On! Island",   ["Barbuta", "Mortol"],       6),
    ("Camouflage",        ["Barbuta", "Mortol"],       8),
    ("Overbold",          ["Barbuta", "Mortol"],       3),
    ("Divers",            ["Barbuta", "Mortol"],       4),
    ("Grimstone",         ["Barbuta", "Mortol"],       5),
    ("Mooncat",           ["Barbuta", "Mortol"],       6),
    ("Mini & Max",        ["Barbuta", "Mortol"],       4),
    ("Golfaria",          ["Barbuta", "Mortol"],       5),
    ("Pilot Quest",       ["Barbuta", "Mortol"],       6),
    ("Quibble Race",      ["Barbuta", "Mortol"],       7),
]


class PerGameGenerationTest(UFO50GenTestBase):
    pass


def _bind_per_game_tests() -> None:
    for game, partners, seed in _PER_GAME:
        slug = game.lower().replace(" ", "_").replace("'", "")
        cases = {
            # a lone game has nowhere to host the Logic Gates, so deferral must be
            # off for a solo no-logic game to generate (defer path: OptionMatrixTest)
            "solo_goal": {
                "games": [game], "starting_game_amount": 1,
                "defer_sphere_1_games": False,
            },
            # start every game so the logic-bearing partners can always host the
            # gates, even when `game` itself is deferred
            "mixed_multiworld": {
                "games": [game] + partners,
                "starting_game_amount": len(partners) + 1,
            },
        }
        for case_name, options in cases.items():
            def test(self, _options=options, _seed=seed) -> None:
                multiworld = generate(_options, seed=_seed)
                self.assert_all_reachable(multiworld)
                self.assert_beatable_after_fill(multiworld)

            test.__name__ = f"test_{slug}_{case_name}"
            setattr(PerGameGenerationTest, test.__name__, test)


_bind_per_game_tests()


# --- assorted yaml-option combinations ---------------------------------------
class OptionMatrixTest(UFO50GenTestBase):
    def test_default_options(self) -> None:
        # no options at all -> the Games default (every game) generates and is beatable
        multiworld = generate({}, seed=2)
        self.assert_beatable_after_fill(multiworld)

    def test_rail_heist_only_goal(self) -> None:
        multiworld = generate({
            "games": ["Rail Heist"], "starting_game_amount": 1,
        }, seed=2)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_multi_game_multi_goal(self) -> None:
        multiworld = generate({
            "games": ["Rail Heist", "Barbuta", "Porgy"], "starting_game_amount": 1,
        }, seed=2)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_porgy_radar_always_on_and_early_pins_off(self) -> None:
        multiworld = generate({
            "games": ["Porgy", "Night Manor", "Block Koala"], "starting_game_amount": 1,
            "porgy_radar": 0, "nm_early_pin": 0, "block_koala_early_start_gate": 0,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_early_pins_on(self) -> None:
        multiworld = generate({
            "games": ["Night Manor", "Block Koala"], "starting_game_amount": 1,
            "nm_early_pin": 1, "block_koala_early_start_gate": 1,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_defer_sphere_1_games_off(self) -> None:
        multiworld = generate({
            "games": ["Barbuta", "Combatants", "Valbrace", "Waldorf's Journey"],
            "starting_game_amount": 1, "defer_sphere_1_games": False,
        }, seed=4)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_defer_sphere_1_games_on_mixed(self) -> None:
        multiworld = generate({
            "games": ["Barbuta", "Porgy", "Combatants", "Valbrace", "Ninpek", "Divers"],
            "starting_game_amount": 1, "defer_sphere_1_games": True,
        }, seed=4)
        self.assert_all_reachable(multiworld)
        world = multiworld.worlds[1]
        # the sphere-1-only games in the seed are deferred
        self.assertTrue(world.deferred_sphere1_games)
        gate_names = {f"Artificial Logic Gate {n}" for n in (1, 2, 3)}
        pool_names = {item.name for item in multiworld.itempool}
        self.assertTrue(gate_names <= pool_names, "Artificial Logic Gate items missing from the pool")
        # a deferred game's boot entrance needs every gate (fill-time rule)
        deferred = world.deferred_sphere1_games[0]
        state = multiworld.get_all_state(False)
        entrance = multiworld.get_entrance(f"Boot {deferred}", 1)
        self.assertTrue(entrance.can_reach(state))
        for gate in gate_names:
            reduced = multiworld.get_all_state(False)
            reduced.remove(world.create_item(gate))
            self.assertFalse(entrance.can_reach(reduced),
                             f"Boot {deferred} should be blocked without {gate}")
        self.assert_beatable_after_fill(multiworld)

    def test_defer_sphere_1_games_mostly_no_logic(self) -> None:
        # Divers/Avianos/Mooncat are deferred; the logic games (Barbuta, Ninpek,
        # Bushido Ball) host the gates. All games start so a host is guaranteed.
        multiworld = generate({
            "games": ["Barbuta", "Ninpek", "Divers", "Avianos", "Mooncat", "Bushido Ball"],
            "starting_game_amount": 6, "defer_sphere_1_games": True,
        }, seed=7)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_defer_sphere_1_games_no_logic_host_fails(self) -> None:
        # every game is a no-logic game, so there is nowhere to place the gates
        # -> generation fails
        from Options import OptionError
        with self.assertRaises(OptionError):
            generate({
                "games": ["Valbrace", "Divers", "Mooncat"],
                "starting_game_amount": 1, "defer_sphere_1_games": True,
            }, seed=4)

    def test_cherry_enabled_games(self) -> None:
        # only Barbuta keeps its Cherry; the other played games lose theirs. Pilot
        # Quest is listed but not played, so it just has no effect.
        multiworld = generate({
            "games": ["Barbuta", "Combatants", "Hot Foot", "Waldorf's Journey"],
            "starting_game_amount": 1,
            "cherry_enabled_games": ["Barbuta", "Pilot Quest"],
        }, seed=4)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
        loc_names = {loc.name for loc in multiworld.get_locations(1)}
        for g in ("Combatants", "Hot Foot", "Waldorf's Journey"):
            self.assertNotIn(f"{g} - Cherry", loc_names)
        self.assertIn("Barbuta - Cherry", loc_names)

    def test_cherry_enabled_games_explicit_empty(self) -> None:
        # an explicit empty list overrides the default -> no game has a Cherry location
        multiworld = generate({
            "games": ["Barbuta", "Combatants", "Hot Foot", "Waldorf's Journey", "Night Manor"],
            "starting_game_amount": 1, "cherry_enabled_games": [],
        }, seed=4)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
        loc_names = {loc.name for loc in multiworld.get_locations(1)}
        self.assertEqual([n for n in loc_names if n.endswith(" - Cherry")], [])

    def test_cherry_enabled_games_default(self) -> None:
        # the default set gives most games a Cherry but leaves the deep-gate ones out
        multiworld = generate({
            "games": ["Barbuta", "Porgy", "Hot Foot", "Waldorf's Journey", "Night Manor"],
            "starting_game_amount": 2,
        }, seed=4)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
        loc_names = {loc.name for loc in multiworld.get_locations(1)}
        for g in ("Hot Foot", "Waldorf's Journey", "Night Manor"):
            self.assertIn(f"{g} - Cherry", loc_names)
        for g in ("Barbuta", "Porgy"):
            self.assertNotIn(f"{g} - Cherry", loc_names)

    def test_deathlink_games_slot_data(self) -> None:
        from .. import game_ids
        from ..death_link import DEATH_LINK_RULES
        games = ["Barbuta", "Ninpek", "Combatants"]
        # default -> every game's number (the mod only acts on the ones actually played)
        mw = generate({"games": games, "starting_game_amount": 1}, seed=1)
        self.assertEqual(mw.worlds[1].fill_slot_data()["deathlink_games"],
                         sorted(game_ids[g] for g in DEATH_LINK_RULES))
        # explicit empty -> empty (no game has DeathLink)
        mw = generate({"games": games, "starting_game_amount": 1, "deathlink_games": []}, seed=1)
        self.assertEqual(mw.worlds[1].fill_slot_data()["deathlink_games"], [])
        # explicit subset -> just those
        mw = generate({"games": games, "starting_game_amount": 1,
                       "deathlink_games": ["Barbuta", "Combatants"]}, seed=1)
        self.assertEqual(mw.worlds[1].fill_slot_data()["deathlink_games"],
                         sorted(game_ids[g] for g in ("Barbuta", "Combatants")))

    def test_velgress_mortol_ii_pool_shrinks_without_cherry(self) -> None:
        # Velgress / Mortol II drop one item (Progressive Gun x3->x2, +10 Lives x7->x6)
        # when they have no Cherry, so the tight pool still fits the location count.
        for name, dup_item, full, cut in (("Velgress", "Progressive Gun", 3, 2),
                                          ("Mortol II", "+10 Lives", 7, 6)):
            with_cherry = generate({"games": ["Barbuta", name], "starting_game_amount": 2,
                                    "cherry_enabled_games": [name]}, seed=3)
            without = generate({"games": ["Barbuta", name], "starting_game_amount": 2,
                                "cherry_enabled_games": []}, seed=3)
            n_with = sum(i.name == f"{name} - {dup_item}" for i in with_cherry.itempool)
            n_without = sum(i.name == f"{name} - {dup_item}" for i in without.itempool)
            self.assertEqual(n_with, full, name)
            self.assertEqual(n_without, cut, name)
