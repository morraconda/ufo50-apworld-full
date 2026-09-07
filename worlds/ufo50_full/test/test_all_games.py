"""All UFO 50 generation tests.

Every test just builds a multiworld with :func:`generate` and asserts the general
"the goal is possible" properties -- every location reachable with all items, and
the seed fills without deadlock and is beatable. Nothing here pins item counts, ids
or sphere-1 contents.

Every game listed in the ``games`` option is enabled and is a goal (you must get Gold
in all of them). ``random_choice_games`` are enabled but never goals -- the tests use
that when they want an enabled-but-not-goal game.

Three groups:
  * ``AllGamesGenerationTest`` -- every implemented game switched on at once.
  * ``PerGameGenerationTest``  -- each game on its own: solo goal, solo non-goal, and
    a small mixed multiworld. Methods are generated from ``_PER_GAME``.
  * ``OptionMatrixTest``       -- assorted yaml-option combinations that touch code
    paths the above miss (small multiworlds, per-game ``create_items`` branches).
"""

from . import ALL_GAMES, UFO50GenTestBase, generate


def _others(*keep: str) -> list[str]:
    """Every implemented game except the given ones -- handy for random_choice_games."""
    return [g for g in ALL_GAMES if g not in keep]


class AllGamesGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=7)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_all_goals(self) -> None:
        self._check({"games": ALL_GAMES, "starting_game_amount": 1})

    def test_single_goal_many_enabled(self) -> None:
        self._check({
            "games": ["Barbuta"], "starting_game_amount": 1,
            "random_choice_games": _others("Barbuta"), "random_choice_game_count": 50,
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
    ("Warptank",          ["Barbuta", "Mortol"],       8),
    ("Bug Hunter",        ["Barbuta", "Mortol"],       3),
    ("The Big Bell Race", ["Barbuta", "Mortol"],       5),
    ("Paint Chase",       ["Barbuta", "Mortol"],       9),
    ("Onion Delivery",    ["Barbuta", "Mortol"],       7),
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
            "solo_non_goal": {
                "games": ["Barbuta"], "starting_game_amount": 1,
                "random_choice_games": [game], "random_choice_game_count": 1,
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

    def test_rail_heist_enabled_not_goal(self) -> None:
        multiworld = generate({
            "games": ["Barbuta"], "starting_game_amount": 1,
            "random_choice_games": ["Rail Heist"], "random_choice_game_count": 1,
        }, seed=2)
        self.assert_beatable_after_fill(multiworld)

    def test_multi_game_multi_goal(self) -> None:
        multiworld = generate({
            "games": ["Rail Heist", "Barbuta"], "starting_game_amount": 1,
            "random_choice_games": ["Porgy"], "random_choice_game_count": 1,
        }, seed=2)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_porgy_radar_always_on_and_early_pins_off(self) -> None:
        multiworld = generate({
            "games": ["Porgy"], "starting_game_amount": 1,
            "random_choice_games": ["Night Manor", "Block Koala"], "random_choice_game_count": 2,
            "porgy_radar": 0, "nm_early_pin": 0, "block_koala_early_start_gate": 0,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_early_pins_on(self) -> None:
        multiworld = generate({
            "games": ["Night Manor"], "starting_game_amount": 1,
            "random_choice_games": ["Block Koala"], "random_choice_game_count": 1,
            "nm_early_pin": 1, "block_koala_early_start_gate": 1,
        }, seed=13)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
