"""Magic Garden: the goal is reachable and the seed fills + beats."""

from . import UFO50GenTestBase, generate

_GAME = "Magic Garden"

_SOLO_GOAL = {
    "always_on_games": [_GAME], "starting_game_amount": 1,
    "goal_games": [_GAME], "goal_game_amount": 1, "cherry_allowed_games": [_GAME],
}
_SOLO_NON_GOAL = {
    "always_on_games": [_GAME], "starting_game_amount": 1,
    "goal_games": ["Barbuta"], "goal_game_amount": 1, "cherry_allowed_games": [],
}
_MIXED = {
    "always_on_games": [_GAME, "Barbuta", "Mortol"], "starting_game_amount": 1,
    "goal_games": [_GAME], "goal_game_amount": 1, "cherry_allowed_games": [_GAME],
}


class MagicGardenGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=11)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_solo_goal_cherry(self) -> None:
        self._check(_SOLO_GOAL)

    def test_solo_non_goal_no_cherry(self) -> None:
        self._check(_SOLO_NON_GOAL)

    def test_mixed_multiworld(self) -> None:
        self._check(_MIXED)
