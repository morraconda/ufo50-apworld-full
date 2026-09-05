"""Mortol: item-pool shape, sphere 1, reachability, per-level id layout."""

from collections import Counter

from ..game_helpers import level_id
from ..games.mortol.locations import NUM_LEVELS, PICKUPS, level_name, location_table
from . import UFO50GenTestBase, generate, sphere_one

_MORTOL_SOLO_GOAL = {
    "always_on_games": ["Mortol"], "starting_game_amount": 1,
    "goal_games": ["Mortol"], "goal_game_amount": 1, "cherry_allowed_games": ["Mortol"],
}
_MORTOL_SOLO_NON_GOAL = {
    "always_on_games": ["Mortol"], "starting_game_amount": 1,
    "goal_games": ["Barbuta"], "goal_game_amount": 1, "cherry_allowed_games": [],
}
_MORTOL_MIXED = {
    "always_on_games": ["Mortol", "Barbuta", "Rail Heist"], "starting_game_amount": 1,
    "goal_games": ["Mortol"], "goal_game_amount": 1, "cherry_allowed_games": ["Mortol"],
}

# Stage 1-A's clear plus its six life pickups are always reachable with no items.
_EXPECTED_SPHERE_ONE = sorted(["1-A"] + [f"1-A - Life Pickup {y}" for y in range(1, 7)])


class MortolIdLayoutTest(UFO50GenTestBase):
    def test_clear_offsets(self) -> None:
        for lvl in range(1, NUM_LEVELS + 1):
            self.assertEqual(location_table[level_name(lvl)].id_offset, level_id(lvl, 0))

    def test_pickup_offsets(self) -> None:
        per_level: Counter[int] = Counter()
        for _x, _y, _n, lvl in PICKUPS:
            per_level[lvl] += 1
            name = f"{level_name(lvl)} - Life Pickup {per_level[lvl]}"
            self.assertEqual(location_table[name].id_offset, level_id(lvl, per_level[lvl]))

    def test_offsets_distinct_and_below_goal_ids(self) -> None:
        offsets = [data.id_offset for name, data in location_table.items()
                   if name not in ("Garden", "Gold", "Cherry")]
        self.assertEqual(len(offsets), len(set(offsets)), "duplicate id offset")
        self.assertTrue(all(off < 997 for off in offsets))


class MortolGenerationTest(UFO50GenTestBase):
    def _check(self, options: dict) -> None:
        multiworld = generate(options, seed=3)
        pool = Counter(item.name for item in multiworld.itempool if item.name.startswith("Mortol"))
        self.assertEqual(pool["Mortol - +3 Lives"], 31)
        self.assertEqual(pool["Mortol - +5 Lives"], 20)
        self.assertEqual(pool["Mortol - +10 Lives"], 9)
        self.assertEqual(sphere_one(multiworld, "Mortol"), _EXPECTED_SPHERE_ONE)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)

    def test_solo_goal_cherry(self) -> None:
        self._check(_MORTOL_SOLO_GOAL)

    def test_solo_non_goal_no_cherry(self) -> None:
        self._check(_MORTOL_SOLO_NON_GOAL)

    def test_mixed_multiworld(self) -> None:
        self._check(_MORTOL_MIXED)
