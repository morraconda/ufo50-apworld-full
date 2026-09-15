from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import (GAME_NAME, CARDINALS, DIAGONALS, TICKET, SHOOT_DOWN,
                     SHOOT_LEFT, SHOOT_UP_LEFT, SHOOT_DOWN_LEFT)

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    cardinal = tuple(f"{GAME_NAME} - {n}" for n in CARDINALS)
    diagonal = tuple(f"{GAME_NAME} - {n}" for n in DIAGONALS)
    ticket = f"{GAME_NAME} - {TICKET}"
    leftward = tuple(f"{GAME_NAME} - {n}" for n in (SHOOT_LEFT, SHOOT_UP_LEFT, SHOOT_DOWN_LEFT))

    regions["Menu"].connect(regions["Stages 1-2"])
    regions["Stages 1-2"].connect(
        regions["Ticket Gate"],
        rule=lambda state: state.has(ticket, player))
    regions["Stages 1-2"].connect(
        regions["Cardinal Zone"],
        rule=lambda state: state.has_all(cardinal, player))
    regions["Cardinal Zone"].connect(
        regions["Demon Tower"],
        rule=lambda state: state.has_all(diagonal, player))

    # Stage II (the Train gauntlet) can't be cleared without shooting downward.
    set_rule(world.get_location(f"{GAME_NAME} - Train"),
             lambda state: state.has(f"{GAME_NAME} - {SHOOT_DOWN}", player))

    # Josie and the third White Pea ticket both require shooting some leftward direction.
    set_rule(world.get_location(f"{GAME_NAME} - Josie"),
             lambda state: state.has_any(leftward, player))
    set_rule(world.get_location(f"{GAME_NAME} - White Pea Ticket 3"),
             lambda state: state.has_any(leftward, player))
