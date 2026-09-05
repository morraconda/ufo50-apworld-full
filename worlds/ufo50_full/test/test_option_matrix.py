"""Assorted yaml-option combinations that touch code paths the all-games test misses.

Includes the small-multiworld matrix (default Barbuta-only, Rail Heist solo and
mixed) plus the per-game ``create_items`` option branches: Porgy's always-on radar
and the Night Manor / Block Koala early-item pins toggled both ways.
"""

from . import UFO50GenTestBase, generate


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
