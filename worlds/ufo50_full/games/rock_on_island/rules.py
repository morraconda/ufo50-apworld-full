from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Region

from .items import (GAME_NAME, CHICKENS, CAMPFIRES, PROG_SPEAR, PROG_FIRE, PROG_ROCK,
                    PROG_WEAPON_UP, PROG_THROW_UP)

if TYPE_CHECKING:
    from ... import UFO50World


_spear = f"{GAME_NAME} - {PROG_SPEAR}"
_fire = f"{GAME_NAME} - {PROG_FIRE}"
# every progression item, at its full required count
_all_counts = {
    f"{GAME_NAME} - {CHICKENS}": 1,
    f"{GAME_NAME} - {CAMPFIRES}": 1,
    f"{GAME_NAME} - {PROG_SPEAR}": 2,
    f"{GAME_NAME} - {PROG_FIRE}": 2,
    f"{GAME_NAME} - {PROG_ROCK}": 2,
    f"{GAME_NAME} - {PROG_WEAPON_UP}": 2,
    f"{GAME_NAME} - {PROG_THROW_UP}": 2,
}


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    def has_everything(state: CollectionState) -> bool:
        return all(state.has(name, player, n) for name, n in _all_counts.items())

    regions["Menu"].connect(regions["The Island"])
    regions["The Island"].connect(regions["Fireside"],
                                  rule=lambda state: state.has(_fire, player, 1))
    regions["Fireside"].connect(regions["Spearpoint"],
                                rule=lambda state: state.has(_spear, player, 2))
    regions["Spearpoint"].connect(regions["Mastery"], rule=has_everything)
