"""All UFO 50 generation tests.

Every test just builds a multiworld with :func:`generate` and asserts the general
"the goal is possible" properties -- every location reachable with all items, and
the seed fills without deadlock and is beatable. Nothing here pins item counts, ids
or sphere-1 contents.

Three groups:
  * ``AllGamesGenerationTest`` -- every implemented game switched on at once, across
    the goal / cherry permutations.
  * ``PerGameGenerationTest``  -- each game on its own: solo goal+cherry, solo
    non-goal (no cherry), and a small mixed multiworld. Methods are generated from
    ``_PER_GAME`` (one per ``test_<game>_<case>``).
  * ``OptionMatrixTest``       -- assorted yaml-option combinations that touch code
    paths the above miss (small multiworlds, per-game ``create_items`` branches).
"""

from . import ALL_GAMES, UFO50GenTestBase, generate


class AllGamesGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=7)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_all_goals_all_cherry(self) -> None:
        self._check({
            "always_on_games": ALL_GAMES, "starting_game_amount": 1,
            "goal_games": ALL_GAMES, "goal_game_amount": 50,
            "cherry_allowed_games": ALL_GAMES,
        })

    def test_single_goal_no_cherry(self) -> None:
        self._check({
            "always_on_games": ALL_GAMES, "starting_game_amount": 1,
            "goal_games": ["Barbuta"], "goal_game_amount": 1,
            "cherry_allowed_games": [],
        })

    def test_all_goals_no_cherry(self) -> None:
        self._check({
            "always_on_games": ALL_GAMES, "starting_game_amount": 1,
            "goal_games": ALL_GAMES, "goal_game_amount": 50,
            "cherry_allowed_games": [],
        })


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
]


class PerGameGenerationTest(UFO50GenTestBase):
    pass


def _bind_per_game_tests() -> None:
    for game, partners, seed in _PER_GAME:
        slug = game.lower().replace(" ", "_").replace("'", "")
        cases = {
            "solo_goal_cherry": {
                "always_on_games": [game], "starting_game_amount": 1,
                "goal_games": [game], "goal_game_amount": 1, "cherry_allowed_games": [game],
            },
            "solo_non_goal_no_cherry": {
                "always_on_games": [game], "starting_game_amount": 1,
                "goal_games": ["Barbuta"], "goal_game_amount": 1, "cherry_allowed_games": [],
            },
            "mixed_multiworld": {
                "always_on_games": [game] + partners, "starting_game_amount": 1,
                "goal_games": [game], "goal_game_amount": 1, "cherry_allowed_games": [game],
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
            "always_on_games": ["Rail Heist"], "starting_game_amount": 1,
            "goal_games": ["Rail Heist"], "goal_game_amount": 1,
            "cherry_allowed_games": ["Rail Heist"],
        }, seed=2)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_rail_heist_only_non_goal_no_cherry(self) -> None:
        multiworld = generate({
            "always_on_games": ["Rail Heist"], "starting_game_amount": 1,
            "goal_games": ["Barbuta"], "goal_game_amount": 1,
            "cherry_allowed_games": [],
        }, seed=2)
        self.assert_beatable_after_fill(multiworld)

    def test_multi_game_multi_goal(self) -> None:
        multiworld = generate({
            "always_on_games": ["Rail Heist", "Barbuta", "Porgy"], "starting_game_amount": 1,
            "goal_games": ["Rail Heist", "Barbuta"], "goal_game_amount": 2,
            "cherry_allowed_games": ["Rail Heist"],
        }, seed=2)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_porgy_radar_always_on_and_early_pins_off(self) -> None:
        multiworld = generate({
            "always_on_games": ["Porgy", "Night Manor", "Block Koala"], "starting_game_amount": 1,
            "goal_games": ["Porgy"], "goal_game_amount": 1, "cherry_allowed_games": [],
            "porgy_radar": 0, "nm_early_pin": 0, "block_koala_early_start_gate": 0,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_early_pins_on(self) -> None:
        multiworld = generate({
            "always_on_games": ["Night Manor", "Block Koala"], "starting_game_amount": 1,
            "goal_games": ["Night Manor"], "goal_game_amount": 1,
            "cherry_allowed_games": ["Night Manor"],
            "nm_early_pin": 1, "block_koala_early_start_gate": 1,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
