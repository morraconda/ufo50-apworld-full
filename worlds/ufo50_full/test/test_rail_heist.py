"""Rail Heist: the goal is reachable and the seed fills + beats."""

from . import UFO50GenTestBase, generate

_SOLO_GOAL = {
    "always_on_games": ["Rail Heist"], "starting_game_amount": 1,
    "goal_games": ["Rail Heist"], "goal_game_amount": 1,
    "cherry_allowed_games": ["Rail Heist"],
}
_SOLO_NON_GOAL = {
    "always_on_games": ["Rail Heist"], "starting_game_amount": 1,
    "goal_games": ["Barbuta"], "goal_game_amount": 1, "cherry_allowed_games": [],
}
_MIXED = {
    "always_on_games": ["Rail Heist", "Barbuta", "Porgy"], "starting_game_amount": 1,
    "goal_games": ["Rail Heist", "Barbuta"], "goal_game_amount": 2,
    "cherry_allowed_games": ["Rail Heist"],
}


class RailHeistGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=1)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_solo_goal_cherry(self) -> None:
        self._check(_SOLO_GOAL)

    def test_solo_non_goal_no_cherry(self) -> None:
        self._check(_SOLO_NON_GOAL)

    def test_mixed_multiworld(self) -> None:
        self._check(_MIXED)
