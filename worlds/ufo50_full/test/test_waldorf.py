"""Waldorf's Journey: precollected starting kit, filler-only pool, everything sphere 1."""

from collections import Counter

from ..games.waldorf.items import STARTING_ITEMS
from . import UFO50GenTestBase, generate, sphere_one

_GAME = "Waldorf's Journey"

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


class WaldorfGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=4)

        precollected = {item.name for item in multiworld.precollected_items[1]
                        if item.name.startswith("Waldorf")}
        for name in STARTING_ITEMS:
            self.assertIn(f"{_GAME} - {name}", precollected)

        pool = Counter(item.name for item in multiworld.itempool if item.name.startswith("Waldorf"))
        self.assertEqual(set(pool), {f"{_GAME} - Shell"}, "pool should hold only Shell filler")

        locations = sorted(loc.name[len(f"{_GAME} - "):] for loc in multiworld.get_locations(1)
                           if loc.name.startswith(f"{_GAME} - "))
        self.assertEqual(sphere_one(multiworld, _GAME), locations, "every check should be sphere 1")

        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_solo_goal_cherry(self) -> None:
        self._check(_SOLO_GOAL)

    def test_solo_non_goal_no_cherry(self) -> None:
        self._check(_SOLO_NON_GOAL)

    def test_mixed_multiworld(self) -> None:
        self._check(_MIXED)
