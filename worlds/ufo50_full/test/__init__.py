"""Generation tests for the UFO 50 world.

There is no pytest in this tree, so these are plain ``unittest`` modules driven by
``test.general.setup_multiworld`` (the same entry point the rest of Archipelago's
test suite uses). Run them with::

    python -m unittest discover -t . -s worlds/ufo50_full/test        # all of them
    python -m unittest worlds.ufo50_full.test.test_all_games          # one module

Each test builds a multiworld by hand with :func:`generate` (varied yaml options,
often several cases per test method), then asserts on reachability, the item pool
and whether the seed fills and beats -- so they subclass :class:`UFO50GenTestBase`
rather than ``WorldTestBase`` (which auto-generates one world from a single
``options`` dict).
"""

import unittest

from BaseClasses import CollectionState, MultiWorld
from Fill import distribute_items_restrictive
from test.general import gen_steps, setup_multiworld

from .. import UFO50World, ufo50_games

# every game with a real implementation (Ninpek / Magic Garden / Velgress are not here)
ALL_GAMES = list(ufo50_games.keys())


def generate(options: dict, seed: int = 0) -> MultiWorld:
    """A generated single-player UFO 50 multiworld with the given yaml options."""
    return setup_multiworld(UFO50World, gen_steps, seed=seed, options=options)


def sphere_one(multiworld: MultiWorld, game_name: str) -> list[str]:
    """Sorted bare location names for ``game_name`` reachable with no items."""
    empty = CollectionState(multiworld)
    prefix = f"{game_name} - "
    return sorted(loc.name[len(prefix):] for loc in multiworld.get_locations(1)
                  if loc.name.startswith(prefix) and loc.can_reach(empty))


class UFO50GenTestBase(unittest.TestCase):
    """Base for tests that build multiworlds by hand with :func:`generate`."""

    def assert_all_reachable(self, multiworld: MultiWorld, game_name: str | None = None) -> None:
        """Every location (optionally only ``game_name``'s) is reachable with all items."""
        state = multiworld.get_all_state(False)
        prefix = None if game_name is None else f"{game_name} - "
        unreachable = [loc.name for loc in multiworld.get_locations(1)
                       if (prefix is None or loc.name.startswith(prefix)) and not loc.can_reach(state)]
        self.assertEqual(unreachable, [], "locations unreachable with all items collected")

    def assert_beatable_after_fill(self, multiworld: MultiWorld) -> None:
        """The seed fills without deadlock and is then winnable from an empty state."""
        distribute_items_restrictive(multiworld)
        self.assertTrue(multiworld.can_beat_game(CollectionState(multiworld)),
                        "seed not beatable after fill")
