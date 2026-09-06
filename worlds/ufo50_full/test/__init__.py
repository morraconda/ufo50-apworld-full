"""Generation tests for the UFO 50 world.

There is no pytest in this tree, so these are plain ``unittest`` modules driven by
``test.general.setup_multiworld`` (the same entry point the rest of Archipelago's
test suite uses). Run them with::

    python -m unittest discover -t . -s worlds/ufo50_full/test        # all of them
    python -m unittest worlds.ufo50_full.test.test_all_games          # one module

Every test just builds a multiworld with :func:`generate` for some yaml options and
asserts the general "the goal is possible" properties: every location is reachable
with all items, and the seed fills without deadlock and is beatable. Nothing here
pins exact item counts, ids, or sphere-1 contents -- those change with tuning and
would only produce brittle failures.
"""

import unittest

from BaseClasses import CollectionState, MultiWorld
from Fill import distribute_items_restrictive
from test.general import gen_steps, setup_multiworld

from .. import UFO50World, ufo50_games

# every game with a real implementation
ALL_GAMES = list(ufo50_games.keys())


def generate(options: dict, seed: int = 0) -> MultiWorld:
    """A generated single-player UFO 50 multiworld with the given yaml options."""
    return setup_multiworld(UFO50World, gen_steps, seed=seed, options=options)


class UFO50GenTestBase(unittest.TestCase):
    """Base for tests that build multiworlds by hand with :func:`generate`."""

    def assert_all_reachable(self, multiworld: MultiWorld) -> None:
        """Every location is reachable with all items collected."""
        state = multiworld.get_all_state(False)
        unreachable = [loc.name for loc in multiworld.get_locations(1) if not loc.can_reach(state)]
        self.assertEqual(unreachable, [], "locations unreachable with all items collected")

    def assert_beatable_after_fill(self, multiworld: MultiWorld) -> None:
        """The seed fills without deadlock and is then winnable from an empty state."""
        distribute_items_restrictive(multiworld)
        self.assertTrue(multiworld.can_beat_game(CollectionState(multiworld)),
                        "seed not beatable after fill")
