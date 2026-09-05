from typing import TYPE_CHECKING

from BaseClasses import ItemClassification as IC, Item

from ...game_helpers import (ItemInfo, get_items as _get_items, game_item_groups,
                             create_item as _create_item, create_items as _create_items)
from .locations import sphere_1_locs

if TYPE_CHECKING:
    from ... import UFO50World


GAME_NAME = "Night Manor"


# TODO: Add conditional item classification based on if victory type needed is gift, gold, cherry.
item_table: dict[str, ItemInfo] = {
    "Spoon": ItemInfo(0, IC.progression),
    "Bowl": ItemInfo(1, IC.progression),
    "Yellow Note": ItemInfo(2, IC.filler),
    "Hairpin": ItemInfo(3, IC.progression),
    "Tweezers": ItemInfo(4, IC.progression),
    "Hook": ItemInfo(7, IC.progression),
    "Batteries": ItemInfo(8, IC.progression),
    "Coins": ItemInfo(10, IC.progression),
    "Matches": ItemInfo(11, IC.progression),
    "Kitchen Knife": ItemInfo(14, IC.progression),
    "Drain Cleaner": ItemInfo(15, IC.progression),
    "Oil Can": ItemInfo(16, IC.progression),
    "Flashlight": ItemInfo(17, IC.progression),
    "Duct Tape": ItemInfo(18, IC.progression),
    "Gas Can": ItemInfo(20, IC.progression),
    "Crowbar": ItemInfo(21, IC.progression),
    "Ornamental Egg": ItemInfo(22, IC.progression),
    "Pool Cue": ItemInfo(25, IC.progression),
    "Sheet Music": ItemInfo(27, IC.progression),
    "Screwdriver": ItemInfo(29, IC.progression),
    "Wrench": ItemInfo(31, IC.progression),
    "Hedge Shears": ItemInfo(32, IC.progression),
    "Shovel": ItemInfo(33, IC.progression),
    "Motor": ItemInfo(36, IC.progression),
    "Hacksaw": ItemInfo(38, IC.progression),
    "Ring": ItemInfo(40, IC.progression),
    "Gear": ItemInfo(42, IC.progression),
    "Magnifying Glass": ItemInfo(47, IC.progression),
    "Tea Tree Oil": ItemInfo(48, IC.progression),
    "Hydrogen Peroxide": ItemInfo(49, IC.progression),
    "Safe Combination": ItemInfo(50, IC.progression),
    "Cigar Butt": ItemInfo(52, IC.progression),
    "Computer Password": ItemInfo(55, IC.progression),
    "Piano Wire": ItemInfo(57, IC.progression),
    "Crossbow": ItemInfo(58, IC.progression),
    "Doll": ItemInfo(59, IC.progression),
    "Fungicide Recipe": ItemInfo(62, IC.progression),
    "Glasses": ItemInfo(65, IC.progression),
    "Maze Directions": ItemInfo(66, IC.progression),
    "Crossbow Bolt": ItemInfo(67, IC.progression),

    "Ruby": ItemInfo(23, IC.progression),
    "Emerald": ItemInfo(43, IC.progression),
    "Topaz": ItemInfo(53, IC.progression),
    "Diamond": ItemInfo(64, IC.progression),

    "Copper Key": ItemInfo(28, IC.progression),
    "Bronze Key": ItemInfo(34, IC.progression),
    "Gold Key": ItemInfo(35, IC.progression),
    "Steel Key": ItemInfo(37, IC.progression),
    "Silver Key": ItemInfo(39, IC.progression),
    "Brass Key": ItemInfo(41, IC.progression),
    "Aluminum Key": ItemInfo(60, IC.progression),
    "Iron Key": ItemInfo(68, IC.progression),

    "Journal Entry 1": ItemInfo(9, IC.filler),
    "Journal Entry 2": ItemInfo(5, IC.filler),
    "Journal Entry 3": ItemInfo(56, IC.filler),
    "Journal Entry 4": ItemInfo(12, IC.filler),
    "Journal Entry 5": ItemInfo(6, IC.filler),
    "Journal Entry 6": ItemInfo(46, IC.filler),
    "Journal Entry 7": ItemInfo(13, IC.filler),
    "Journal Entry 8": ItemInfo(19, IC.filler),
    "Journal Entry 9": ItemInfo(24, IC.filler),
    "Journal Entry 10": ItemInfo(26, IC.filler),
    "Journal Entry 11": ItemInfo(30, IC.filler),
    "Journal Entry 12": ItemInfo(44, IC.filler),
    "Journal Entry 13": ItemInfo(54, IC.filler),
    "Journal Entry 14": ItemInfo(61, IC.filler),
    "Journal Entry 15": ItemInfo(45, IC.filler),
    "Journal Entry 16": ItemInfo(51, IC.filler),
    "Journal Entry 17": ItemInfo(69, IC.filler),
}


def get_items() -> dict[str, int]:
    return _get_items(GAME_NAME, item_table)


def get_item_groups() -> dict[str, set[str]]:
    item_groups = game_item_groups(GAME_NAME, item_table)
    item_groups.update({
        "Night Manor - Journal Entries": {
            "Night Manor - Journal Entry 1",
            "Night Manor - Journal Entry 2",
            "Night Manor - Journal Entry 3",
            "Night Manor - Journal Entry 4",
            "Night Manor - Journal Entry 5",
            "Night Manor - Journal Entry 6",
            "Night Manor - Journal Entry 7",
            "Night Manor - Journal Entry 8",
            "Night Manor - Journal Entry 9",
            "Night Manor - Journal Entry 10",
            "Night Manor - Journal Entry 11",
            "Night Manor - Journal Entry 12",
            "Night Manor - Journal Entry 13",
            "Night Manor - Journal Entry 14",
            "Night Manor - Journal Entry 15",
            "Night Manor - Journal Entry 16",
            "Night Manor - Journal Entry 17"},
        "Night Manor - Gems": {
            "Night Manor - Ruby",
            "Night Manor - Emerald",
            "Night Manor - Topaz",
            "Night Manor - Diamond"},
        "Night Manor - Red Gemstone": {
            "Night Manor - Ruby"},
        "Night Manor - Green Gemstone": {
            "Night Manor - Emerald"},
        "Night Manor - Yellow Gemstone": {
            "Night Manor - Topaz"},
        "Night Manor - White Gemstone": {
            "Night Manor - Diamond"},
        "Night Manor - Keys": {
            "Night Manor - Copper Key",
            "Night Manor - Bronze Key",
            "Night Manor - Gold Key",
            "Night Manor - Steel Key",
            "Night Manor - Silver Key",
            "Night Manor - Brass Key",
            "Night Manor - Aluminum Key",
            "Night Manor - Iron Key"},
    })
    return item_groups


def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    return _create_item(GAME_NAME, item_table, item_name, world, item_class)


def create_items(world: "UFO50World") -> list[Item]:
    overrides = None
    if world.options.nm_early_pin:
        hairpin = create_item("Hairpin", world)
        loc = world.get_location(f"{GAME_NAME} - " + world.random.choice(sphere_1_locs))
        loc.place_locked_item(hairpin)
        overrides = {"Hairpin": 0}
    return _create_items(GAME_NAME, item_table, world, overrides)


def get_filler_item_name(world: "UFO50World") -> str:
    return f"{GAME_NAME} - Yellow Note"
