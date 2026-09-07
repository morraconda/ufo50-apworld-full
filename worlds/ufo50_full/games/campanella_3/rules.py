from typing import TYPE_CHECKING

from BaseClasses import Region

from .items import GAME_NAME, FORWARD_SHOT, UPWARD_BEAM, RIGHT_BEAM, LEFT_BEAM, DOWN_BEAM

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player

    def item(name: str) -> str:
        return f"{GAME_NAME} - {name}"

    regions["Menu"].connect(regions["Stage A"])
    regions["Stage A"].connect(regions["Armed"],
                               rule=lambda state: state.has(item(FORWARD_SHOT), player))
    regions["Armed"].connect(regions["Up Armed"],
                             rule=lambda state: state.has(item(UPWARD_BEAM), player))
    regions["Up Armed"].connect(
        regions["Fully Armed"],
        rule=lambda state: state.has_all(
            (item(RIGHT_BEAM), item(LEFT_BEAM), item(DOWN_BEAM)), player))
