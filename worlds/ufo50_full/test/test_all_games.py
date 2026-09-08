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
]


class PerGameGenerationTest(UFO50GenTestBase):
    pass


def _bind_per_game_tests() -> None:
    for game, partners, seed in _PER_GAME:
        slug = game.lower().replace(" ", "_").replace("'", "")
        cases = {
            "solo_goal": {
                "games": [game], "starting_game_amount": 1,
            },
            "mixed_multiworld": {
                "games": [game] + partners, "starting_game_amount": 1,
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
    def test_default_barbuta_only(self) -> None:
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
        self.assert_beatable_after_fill(multiworld)

    def test_cherry_disabled_games(self) -> None:
        multiworld = generate({
            "games": ["Barbuta", "Combatants", "Hot Foot", "Waldorf's Journey"],
            "starting_game_amount": 1,
            "cherry_disabled_games": ["Combatants", "Hot Foot", "Waldorf's Journey", "Pilot Quest"],
        }, seed=4)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
        loc_names = {loc.name for loc in multiworld.get_locations(1)}
        for g in ("Combatants", "Hot Foot", "Waldorf's Journey"):
            self.assertNotIn(f"{g} - Cherry", loc_names)
        self.assertIn("Barbuta - Cherry", loc_names)
