"""Unit tests for the shared helpers in ``game_helpers`` that carry their own logic."""

import unittest

from ..game_helpers import IDS_PER_LEVEL, MAX_LEVELS, level_id


class LevelIdTest(unittest.TestCase):
    def test_formula(self) -> None:
        self.assertEqual(level_id(1, 0), 10)
        self.assertEqual(level_id(1, 3), 13)
        self.assertEqual(level_id(2, 0), 20)
        self.assertEqual(level_id(20, 2), 202)
        self.assertEqual(level_id(MAX_LEVELS, IDS_PER_LEVEL - 1), 509)

    def test_slot_defaults_to_zero(self) -> None:
        self.assertEqual(level_id(7), 70)

    def test_level_out_of_range(self) -> None:
        for bad_level in (0, -1, MAX_LEVELS + 1):
            with self.assertRaises(ValueError):
                level_id(bad_level, 0)

    def test_slot_out_of_range(self) -> None:
        for bad_slot in (-1, IDS_PER_LEVEL, IDS_PER_LEVEL + 5):
            with self.assertRaises(ValueError):
                level_id(1, bad_slot)

    def test_never_collides_with_goal_ids(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            for slot in range(IDS_PER_LEVEL):
                self.assertLess(level_id(level, slot), 997)
