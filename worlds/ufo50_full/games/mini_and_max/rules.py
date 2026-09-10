from typing import TYPE_CHECKING

from BaseClasses import Region
from worlds.generic.Rules import set_rule

from .items import (GAME_NAME, PROGRESSIVE_SHRINK, PROGRESSIVE_HIGHER_JUMP,
                    PROGRESSIVE_GLOVE, ARMOR, MITTENS_GATE, LAUNCH_CODES,
                    SHRINK_REGION_NAMES, TOTAL_UPGRADE_COPIES)
from .locations import SHINY_THRESHOLDS, shiny_loc_name, shiny_upgrades_needed

if TYPE_CHECKING:
    from ... import UFO50World


UPGRADES_GROUP = f"{GAME_NAME} - Upgrades"


def _g(name: str) -> str:
    return f"{GAME_NAME} - {name}"


def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    player = world.player
    shrink = _g(PROGRESSIVE_SHRINK)      # "Mini & Max - Progressive Magic Potion"
    hjump = _g(PROGRESSIVE_HIGHER_JUMP)  # "Mini & Max - Progressive Protein"
    glove = _g(PROGRESSIVE_GLOVE)        # "Mini & Max - Progressive Glove"
    armor = _g(ARMOR)                    # "Mini & Max - Dog Armor"
    mittens = _g(MITTENS_GATE)
    codes = _g(LAUNCH_CODES)

    regions["Menu"].connect(regions["Hub"])

    # --- <parent> -> each shrink region -----------------------------------------
    # The 23 shrink regions have no locations right now (quest checks are disabled), but
    # they are still built and wired so the precollected gate items + the mod's
    # ap41_micro_access line up and quests can be re-attached later. Each edge needs one
    # Progressive Magic Potion AND that region's gate item, with two special cases:
    #   Top Right  <- reached from "Top Shelf Right" (not the Hub)
    #   Doorknob   <- also needs the Glove (Progressive Glove >= 1)
    SHRINK_REGION_PARENT: dict[str, str] = {"Top Right": "Top Shelf Right"}
    SHRINK_REGION_EXTRA: dict[str, list[tuple[str, int]]] = {"Doorknob": [(glove, 1)]}

    for _region in SHRINK_REGION_NAMES:
        parent = SHRINK_REGION_PARENT.get(_region, "Hub")
        extra = tuple(SHRINK_REGION_EXTRA.get(_region, ()))
        regions[parent].connect(
            regions[_region],
            rule=lambda state, name=_region, ex=extra: (
                state.has(shrink, player, 1)
                and state.has(_g(name), player)
                and all(state.has(it, player, cnt) for it, cnt in ex)))

    # --- shiny thresholds ------------------------------------------------------
    # Gated on the upgrade count: 2 upgrades per full 100 shinies (20/40/60/80 free,
    # 100 -> 2, 200 -> 4, ... 1000 -> 20), capped at the pool total so the top ones
    # stay reachable. "Mini & Max - Upgrades" holds all 16 upgrade item names and every
    # upgrade is an advancement item, so has_group counts them.
    for n in SHINY_THRESHOLDS:
        need = min(shiny_upgrades_needed(n), TOTAL_UPGRADE_COPIES)
        if need <= 0:
            continue
        set_rule(world.get_location(_g(shiny_loc_name(n))),
                 lambda state, k=need: state.has_group(UPGRADES_GROUP, player, k))

    # Gift lives in the Hub with no rule -- sphere 1.

    # Gold (in "Ending") needs the full escape kit: both Progressive Magic Potion, both
    # Progressive Protein, Dog Armor, Mittens' Gate and Launch Codes.
    regions["Hub"].connect(
        regions["Ending"],
        rule=lambda state: (state.has(shrink, player, 2)
                            and state.has(hjump, player, 2)
                            and state.has(armor, player)
                            and state.has(mittens, player)
                            and state.has(codes, player)))

    # Cherry (the time-reversal ending) = the full kit AND the Clock reachable.
    regions["Ending"].connect(
        regions["Cherry Ending"],
        rule=lambda state: state.can_reach(_g("Clock"), "Region", player))
