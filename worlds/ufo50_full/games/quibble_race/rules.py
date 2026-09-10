from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import GAME_NAME, BREEDER, UPGRADES_GROUP, TOTAL_ITEMS
from .locations import NUM_RACES, races_items_needed

if TYPE_CHECKING:
    from ... import UFO50World


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    breeder = f"{GAME_NAME} - {BREEDER}"

    regions["Menu"].connect(regions["Racing"])

    # Gift = your bred (sponsored) quibble wins a race -> needs the Breeder shop.
    regions["Racing"].connect(regions["Bred Champion"],
                              rule=lambda state: state.has(breeder, player))
    # Cherry = build the whole operation -> every shop + thug item.
    regions["Racing"].connect(regions["Cash Empire"],
                              rule=lambda state: state.has_group(UPGRADES_GROUP, player, TOTAL_ITEMS))

    # "Won N Bets" wants floor(X / 3) of the ten shop / thug items in logic (all are
    # advancement, so has_group counts them). Gold (also in Racing) stays free.
    for n in range(1, NUM_RACES + 1):
        need = races_items_needed(n)
        if need <= 0:
            continue
        set_rule(world.get_location(f"{GAME_NAME} - Won {n} Bets"),
                 lambda state, k=need: state.has_group(UPGRADES_GROUP, player, k))
