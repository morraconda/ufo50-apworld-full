from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location

from ...constants import get_game_base_id
from ...game_helpers import get_locations as _get_locations, game_location_groups
from ...goal_locations import (skip_cherry_location_if_disabled, is_completion_event_location,
                               place_completion_event)

if TYPE_CHECKING:
    from ... import UFO50World

GAME_NAME = "Night Manor"


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str


location_table: dict[str, LocationInfo] = {
    "Starting Room - Spoon": LocationInfo(0, "Starting Room"),
    "Starting Room - Bowl": LocationInfo(1, "Starting Room"),
    # in vent after you open with spoon
    "Starting Room - Yellow Note": LocationInfo(2, "Starting Room"),
    # in vent after you open with spoon
    "Starting Room - Hairpin": LocationInfo(3, "Starting Room"),  

    "First Floor Bathroom - Tweezers": LocationInfo(4, "First Floor & Exterior"),  # in medicine cabinet
    # in sink after you use drain cleaner and tweezers
    "First Floor Bathroom - Silver Key": LocationInfo(39, "First Floor & Exterior"),
    "First Floor Bathroom - Ring": LocationInfo(40, "First Floor & Exterior"),  # on corpse if you use hacksaw

    "Guest Bedroom - Journal Entry 2": LocationInfo(5, "First Floor & Exterior"),
    "Guest Bedroom - Journal Entry 5": LocationInfo(6, "First Floor & Exterior"),
    "Guest Bedroom - Hook": LocationInfo(7, "First Floor & Exterior"),  # in closet
    "Guest Bedroom - Batteries": LocationInfo(8, "First Floor & Exterior"),  # in drawer
    # in jewelery box when opened with silver key
    "Guest Bedroom - Brass Key": LocationInfo(41, "First Floor & Exterior"),

    "Living Room - Journal Entry 1": LocationInfo(9, "First Floor & Exterior"),
    "Living Room - Coins": LocationInfo(10, "First Floor & Exterior"),  # in couch
    "Living Room - Matches": LocationInfo(11, "First Floor & Exterior"),  # above fireplace
    "Living Room - Red Gemstone": LocationInfo(23, "First Floor & Exterior"),  # In fireplace after you burn

    "Dining Room - Journal Entry 4": LocationInfo(12, "First Floor & Exterior"),
    "Dining Room - Ornamental Egg": LocationInfo(22, "First Floor & Exterior"),  # In cabinet after you smash it,

    "Kitchen - Journal Entry 7": LocationInfo(13, "First Floor & Exterior"),  # on the fridge
    "Kitchen - Kitchen Knife": LocationInfo(14, "First Floor & Exterior"),  # on counter, accessible after running from killer
    "Kitchen - Drain Cleaner": LocationInfo(15, "First Floor & Exterior"),  # under sink

    "Garage - Oil Can": LocationInfo(16, "First Floor & Exterior"),  # on side shelf
    "Garage - Flashlight": LocationInfo(17, "First Floor & Exterior"),  # on side shelf
    "Garage - Duct Tape": LocationInfo(18, "First Floor & Exterior"),  # on back shelf
    "Garage - Journal Entry 8": LocationInfo(19, "First Floor & Exterior"),  # on back wall
    "Garage - Gas Can": LocationInfo(20, "First Floor & Exterior"),  # In metal box after you spray with oil can
    "Garage - Crowbar": LocationInfo(21, "First Floor & Exterior"),  # In metal box after you spray with oil can,

    "Sunroom - Journal Entry 9": LocationInfo(24, "First Floor & Exterior"),  # On table
    # in container after you cut vines with hedge shears
    "Sunroom - Hacksaw": LocationInfo(38, "First Floor & Exterior"),

    "Lounge - Pool Cue": LocationInfo(25, "Second Floor"),  # In corner
    "Lounge - Journal Entry 10": LocationInfo(26, "Second Floor"),  # On side table
    "Lounge - Sheet Music": LocationInfo(27, "Second Floor"),  # Falls from jukebox after using coins

    # accessible from floating corpse after you tape hook to pool cue
    "Pool - Copper Key": LocationInfo(28, "First Floor & Exterior"),

    "Shed - Screwdriver": LocationInfo(29, "Shed"),  # on toolbench
    "Shed - Journal Entry 11": LocationInfo(30, "Shed"),  # on toolbench
    "Shed - Wrench": LocationInfo(31, "Shed"),  # hanging on side wall
    "Shed - Hedge Shears": LocationInfo(32, "Shed"),  # hanging on back wall
    "Shed - Shovel": LocationInfo(33, "Shed"),  # in back corner
    "Shed - Bronze Key": LocationInfo(34, "Shed"),  # in sack if you cut with knife
    "Shed - Gold Key": LocationInfo(35, "Shed"),  # in ornamental egg if you crush with vice

    "Backyard - Motor": LocationInfo(36, "First Floor & Exterior"),  # in lawnmower after you use wrench

    "Garden - Steel Key": LocationInfo(37, "First Floor & Exterior"),  # in hole after you dig with shovel
    # after you cut the corpse down from the balcony, cut with knife
    "Garden - Yellow Gemstone": LocationInfo(53, "Master Bedroom"),

    "Foyer - Gear": LocationInfo(42, "First Floor & Exterior"),  # in clock after used with brass key

    # in statue if you use ring on insignia
    "Exterior Front - Green Gemstone": LocationInfo(43, "First Floor & Exterior"),

    "Master Bedroom - Journal Entry 12": LocationInfo(44, "Master Bedroom"),  # on dresser
    "Master Bedroom - Journal Entry 15": LocationInfo(45, "Master Bedroom"),  # in bedside table
    # get from safe behind painting above bed, use combination
    "Master Bedroom - White Gemstone": LocationInfo(64, "Master Bedroom"),

    "Office - Journal Entry 6": LocationInfo(46, "Master Bedroom"),  # on floor near desk
    "Office - Magnifying Glass": LocationInfo(47, "Master Bedroom"),  # on bottom of back shelf
    "Office - Tea Tree Oil": LocationInfo(48, "Master Bedroom"),  # on back shelf
    "Office - Fungicide Recipe": LocationInfo(62, "Master Bedroom"),  # in trash on computer after using password on it

    "Master Bathroom - Hydrogen Peroxide": LocationInfo(49, "Master Bedroom"),  # cabinet under sink,
    "Master Bathroom - Safe Combination": LocationInfo(50, "Master Bedroom"),  # behind mirror if you smash it

    "Balcony - Journal Entry 16": LocationInfo(51, "Master Bedroom"),  # on table
    "Balcony - Cigar Butt": LocationInfo(52, "Master Bedroom"),  # in ashtray

    "Kids Bedroom - Journal Entry 13": LocationInfo(54, "Second Floor"),  # on side desk
    "Kids Bedroom - Computer Password": LocationInfo(55, "Second Floor"),  # use magnifying glass on dollhouse
    "Kids Bedroom - Glasses": LocationInfo(65, "Second Floor"),  # get by using aluminum key on music box

    "Attic - Journal Entry 3": LocationInfo(56, "Second Floor"),  # on floor near mannequins
    "Attic - Piano Wire": LocationInfo(57, "Second Floor"),  # use sheet music on piano and play
    "Attic - Crossbow": LocationInfo(58, "Second Floor"),  # in chest to the right after unlocking with bronze key
    
    "Play Room - Doll": LocationInfo(59, "Second Floor"),  # in bottom right corner of room
    "Manor - Aluminum Key": LocationInfo(60, "First Floor & Exterior"),  # get by cutting doll with knife
    "Play Room - Journal Entry 14": LocationInfo(61, "Second Floor"),  # in bottom left corner
    "Play Room - Maze Directions": LocationInfo(66, "Second Floor"),  # use red glasses on scribbles on wall

    # open gate with gems, use directions on maze, get bolt from statue
    "Maze - Crossbow Bolt": LocationInfo(67, "Maze"),
    # combine crossbow and bolt, lure killer or wait, shoot him and get the key
    "Manor - Iron Key": LocationInfo(68, "First Floor & Exterior"),

    "Basement - Journal Entry 17": LocationInfo(69, "Basement"),  # on floor

    "Garden": LocationInfo(997, "First Floor & Exterior"),
    "Gold": LocationInfo(998, "First Floor & Exterior"),
    "Cherry": LocationInfo(999, "Basement")
}


sphere_1_locs: list[str] = ["Starting Room - Spoon", "Starting Room - Bowl"]


# this is for filling out location_name_to_id, it should be static regardless of yaml options
def get_locations() -> dict[str, int]:
    return _get_locations(GAME_NAME, location_table)


# this should return the location groups for this game, independent of yaml options
# you should include a group that contains all location for this game that is called the same thing as the game
def get_location_groups() -> dict[str, set[str]]:
    return game_location_groups(GAME_NAME, location_table)


# this is not a required function, but a recommended one -- the world class does not call this function
def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    for loc_name, loc_data in location_table.items():
        region = regions[loc_data.region_name]
        if skip_cherry_location_if_disabled(world, GAME_NAME, loc_name):
            break
        if is_completion_event_location(world, GAME_NAME, loc_name):
            place_completion_event(world, GAME_NAME, loc_name, region)
            break

        loc = Location(world.player, f"{GAME_NAME} - {loc_name}", get_game_base_id(GAME_NAME) + loc_data.id_offset,
                       region)
        region.locations.append(loc)
