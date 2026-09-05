"""Every implemented game switched on at once, across the goal / cherry permutations.

Exercises the goal-event path, the non-goal path and the "Gold becomes the
completion event" (no cherry) path for all games in a single multiworld.
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
