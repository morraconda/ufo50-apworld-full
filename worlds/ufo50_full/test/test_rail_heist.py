"""Rail Heist: the time/bullet requirement model, sphere 1, reachability, id layout."""

from ..game_helpers import level_id
from ..games.rail_heist import items as rh_items
from ..games.rail_heist.locations import (ANGEL, CHECK_TYPE_SLOT, CLEAR, DEVIL, LEVEL_NAMES,
                                          location_table)
from ..games.rail_heist.rules import ALL_BULLET_LEVELS, get_check_req
from . import UFO50GenTestBase, generate, sphere_one

_RH_ONLY = {
    "always_on_games": ["Rail Heist"], "starting_game_amount": 1,
    "goal_games": ["Rail Heist"], "goal_game_amount": 1,
    "cherry_allowed_games": ["Rail Heist"],
}

# (time budget, bullets required) for a check with no AP items, per level and check type.
_EXPECTED_REQ = {
    1: {CLEAR: (24, False), ANGEL: (34, False), DEVIL: (54, False)},
    2: {CLEAR: (30, False), ANGEL: (40, False), DEVIL: (60, True)},
    16: {CLEAR: (76, True), ANGEL: (86, True), DEVIL: (106, True)},
    18: {CLEAR: (50, True), ANGEL: (60, True), DEVIL: (80, True)},
    20: {CLEAR: (94, True), ANGEL: (104, True), DEVIL: (124, True)},
}


class RailHeistRequirementTest(UFO50GenTestBase):
    def test_all_bullet_levels(self) -> None:
        self.assertEqual(set(ALL_BULLET_LEVELS), {16, 18, 20})
        self.assertEqual([LEVEL_NAMES[lvl] for lvl in sorted(ALL_BULLET_LEVELS)],
                         ["Armored Up", "Sitting Ducks", "The Final Score"])

    def test_check_requirements(self) -> None:
        for lvl, by_type in _EXPECTED_REQ.items():
            for check_type, (time, bullets) in by_type.items():
                req = get_check_req(lvl, check_type)
                self.assertEqual((req.time, req.bullets), (time, bullets),
                                 f"{LEVEL_NAMES[lvl]} {check_type}")


class RailHeistIdLayoutTest(UFO50GenTestBase):
    def test_location_offsets(self) -> None:
        for lvl, name in LEVEL_NAMES.items():
            for check_type in (CLEAR, ANGEL, DEVIL):
                self.assertEqual(location_table[f"{name} - {check_type}"].id_offset,
                                 level_id(lvl, CHECK_TYPE_SLOT[check_type]))

    def test_item_offsets(self) -> None:
        for lvl, name in LEVEL_NAMES.items():
            self.assertEqual(rh_items.item_table[f"{name} Time"].id_offset, level_id(lvl, 0))
            self.assertEqual(rh_items.item_table[f"{name} Bullets"].id_offset, level_id(lvl, 1))


class RailHeistGenerationTest(UFO50GenTestBase):
    def test_sphere_one_is_level_one_only(self) -> None:
        multiworld = generate(_RH_ONLY, seed=1)
        self.assertEqual(sphere_one(multiworld, "Rail Heist"),
                         sorted(f"{LEVEL_NAMES[1]} - {ct}" for ct in (CLEAR, ANGEL, DEVIL)))

    def test_reachable_and_beatable(self) -> None:
        multiworld = generate(_RH_ONLY, seed=1)
        self.assert_all_reachable(multiworld)
        self.assert_beatable_after_fill(multiworld)
