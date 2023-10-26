# poketypes/protos/protogen.py

"""Provides tools for generating consistent protobuf Enums from pokemon data fields.

The primary goal of this module is for every Enum created to be consistent across generations from a label-number
perspective. Meaning that while future generations of pokemon will certainly have new keys assigned for new pokemon,
any pokemon introduced previously will have the same label-number in every generation then on.
"""

import json
import re
from copy import deepcopy
from typing import Dict, List, Tuple

import requests
from mergers import merge
from statics import CURRENT_GEN, DATA_TYPES
from poketypes.dex.dexdata import clean_name


def fetch_and_clean_ps_data(url: str) -> Dict[str, Dict]:
    """Fetch, clean, and parse a typescript file with pokemon info into a dictionary.

    Modified a bit to work on all relevant typescript files.
    Credit: https://github.com/hsahovic/poke-env/ for the original version.

    Args:
        url (str): The path to the typescript file to parse.

    Returns:
        Dict[str, Dict]: A mapping of keys to some arbirtrary data structure based on the typescript file.
    """
    data = requests.get(url).text

    if data == "404: Not Found":
        return {}

    # Remove extra function parts if present
    data = re.sub(r"function.*{\n(?:\t.*\n)+}", "", data)

    # Remove start and end of the file
    data = "{" + "= {".join(data.split("= {")[1:])[:-2]

    # Transform tabs into spaces
    data = data.replace("\t", " ")

    # Transform keys into correct json strings
    data = re.sub(r"([\w\d]+): ", r'"\1": ', data)

    # Transform single quoted text into double quoted text
    data = re.sub(r"'([\w\d ]+)'", r'"\1"', data)

    # Remove comments
    data = re.sub(r" +//.+", "", data)

    # Remove empty lines
    for _ in range(3):
        data = re.sub(r"\n\n", "\n", data)

    data = re.sub(r",\n( +)\]", r"\n\1]", data)

    # Correct double-quoted text inside double-quoted text
    data = re.sub(r': ""(.*)":(.*)",', r': "\1:\2",', data)

    # Correct isolated "undefined" values
    data = re.sub(r": undefined", r": null", data)

    # Callback and handlers
    for function_title_match in (r"(on\w+)", r"(\w+Callback)", r"(effec\w+)"):
        for n_space in range(10):
            spaces = " " * (n_space)
            pattern = r"^" + spaces + function_title_match + r"\((\w+, )*(\w+)?\) \{\n(.+\n)+?" + spaces + r"\},"
            sub = spaces + r'"\1": "\1",'
            data = re.sub(pattern, sub, data, flags=re.MULTILINE)
        pattern = function_title_match + r"\(\) \{\s*\}"
        sub = r'"\1": "\1"'
        data = re.sub(pattern, sub, data, flags=re.MULTILINE)

    # Remove singleline function
    data = re.sub(r"\s+on\w+\(\w*\) {},\n", "", data)

    # Remove incorrect commas
    data = re.sub(r",\n( *)\}", r"\n\1}", data)

    # Null arrow functions
    data = re.sub(r"\(\) => null", r"null", data)

    # Remove incorrect commas
    data = re.sub(r",\n( *)\}", r"\n\1}", data)
    data = re.sub(r",\n( +)\]", r"\n\1]", data)
    # Correct double-quoted text inside double-quoted text

    data = re.sub(r': "(.*)"(.*)":(.*)",', r': "\1\2:\3",', data)
    data = re.sub(r': ""(.*)":(.*)",', r': "\1:\2",', data)

    # Correct non-quoted number keys
    data = re.sub(r"(\d+):", r'"\1":', data)

    # Correct non-quoted H keys
    data = re.sub(r"H: ", r'"H": ', data)
    data = re.sub(r", moves:", r', "moves":', data)
    data = re.sub(r", nature:", r', "nature":', data)

    data = re.sub(r";", "", data)

    data_dict: Dict[str, Dict] = json.loads(data)

    return data_dict


def create_proto_str(field_name: str, id_names: List[Tuple[str, int]], allow_alias: bool = False) -> str:
    """Create a protobuf formatted string with Enum info.

    Uses the provided enum name and id_names to create a properly formatted Enum. If allow_alias is True, then the
    ids in id_names should all be unique, otherwise an error will be raised.

    Args:
        field_name (str): The name of the field for creating an Enum. For example, field_name="Nature" will create an
            Enum named "DexNature".
        id_names (List[Tuple[str, int]]): A list of name, id pairs to be added to the enum.
        allow_alias (bool, optional): Whether the Enum should allow multiple names to share ids. Defaults to False.

    Returns:
        str: The properly formatted protobuf string.
    """
    # Section comments
    proto_str = f"/* Represents possible {field_name}s\n\nOptions:<br/>\n"

    for name, id in id_names:
        proto_str += f"\t>- {id}: {name}\n"

    proto_str += "*/\n"

    # Start Enum Construction
    proto_str += f"enum Dex{field_name} {{\n"
    if allow_alias:
        proto_str += "\toption allow_alias = true;\n"
    proto_str += f"\t{field_name.upper()}_UNASSIGNED = 0;\n"

    # Add each item to the enum
    for name, id in id_names:
        proto_str += f"\t{field_name.upper()}_{name.upper()} = {id};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

    return proto_str


def protogen_natures(nature_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for natures.

    Built expecting parsed data from natures.ts showdown information.
    Does not use any value information, only the keys from the dictionary.

    Args:
        nature_data (Dict[str, Dict]): A dict mapping nature keys to some arbitrary unused data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    id_names: List[Tuple[str, int]] = []
    for e, key in enumerate(nature_data.keys()):
        id_names.append((key.upper(), e + 1))

    proto_str = create_proto_str("Nature", id_names)

    return proto_str


def protogen_pokedex(pokedex_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for pokemon species / formes.

    Built expecting parsed data from pokedex.ts showdown information.
    Fields used in the arbirtrary structure:
        - `num`: The pokedex number of the pokemon. Different formes share this. Required.
        - `cosmeticFormes`: A list of other species that are purely-cosmetic versions of this. Optional.
    The Enum value uses the format {POKEDEX_NUM}{3-DIGIT FORME NUMBER}, where both cosmetic and true formes get their
    own unique incremental forme number. This supports up to 1000 versions of Charizard, so we should be fine :').

    Args:
        pokedex_data (Dict[str, Dict]): A dict mapping pokemon species keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # Sort and identify unique numbers for each pokemon
    # Number definition: {DEX_NUM}{FORM_NUM zfilled to 3 places}
    # Current definitions supports up to 999 versions of charizard before it breaks :]

    id_names: List[Tuple[str, int]] = []
    last_poke_num = None
    c = 0
    for key, value in pokedex_data.items():
        if value["num"] < 1:
            # We skip fakemon
            continue

        if last_poke_num == value["num"]:
            c += 1
        else:
            c = 0

        num = int(str(value["num"]) + str(c).zfill(3))

        id_names.append((key.upper(), num))
        last_poke_num = value["num"]

        for cosmetic in value.get("cosmeticFormes", []):
            # We first have to clean the string because cosmeticFormes contains uncleaned names, unlike the keys
            name = clean_name(cosmetic)

            c += 1
            num = int(str(value["num"]) + str(c).zfill(3))
            id_names.append((name, num))

    id_names = sorted(id_names, key=lambda x: x[1])

    proto_str = create_proto_str("Pokemon", id_names)

    return proto_str


def protogen_moves(move_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for moves.

    Built expecting parsed data from moves.ts showdown information.
    Fields used in the arbirtrary structure:
        - `num`: The id number of the move. Different formes of the same move share this. Required.
    The Enum value uses the format {MOVE_NUM}{2-DIGIT FORME NUMBER}, with any moves that share the same id number
    getting assigned their own unique forme number.

    Args:
        move_data (Dict[str, Dict]): A dict mapping pokemon move keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # Section comments
    proto_str = "//Contains data for Pokemon Moves\n"

    # Start Enum Construction
    id_names: List[Tuple[str, int]] = []
    last_move_num = None
    c = 0
    for key, value in move_data.items():
        if value["num"] < 1:
            # We skip fake moves
            continue

        if last_move_num == value["num"]:
            c += 1
        else:
            c = 0

        num = int(str(value["num"]) + str(c).zfill(2))

        id_names.append((key.upper(), num))
        last_move_num = value["num"]

        if "hiddenpower" in key:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(2))
            id_names.append((key.upper() + "60", num))
        elif "return" in key:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(2))
            id_names.append((key.upper() + "102", num))

    id_names.append(("RECHARGE", 1))

    id_names = sorted(id_names, key=lambda x: x[1])

    proto_str = create_proto_str("Move", id_names)

    return proto_str


def protogen_typechart(typechart_data: (Dict[str, Dict])) -> str:
    """Generate a protobuf formatted string with Enum info for typechart information.

    Built expecting parsed data from typechart.ts showdown information.
    The data structure passed in can be arbitrary, as for this step we only care about the keys.

    Args:
        typechart_data (Dict[str, Dict]): A dict mapping pokemon type keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    id_names: List[Tuple[str, int]] = []

    for e, key in enumerate(typechart_data.keys()):
        id_names.append((key.upper(), e + 1))

    id_names = sorted(id_names, key=lambda x: x[1])

    proto_str = create_proto_str("Type", id_names)

    return proto_str


def protogen_conditions(condition_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for conditions information.

    Built expecting parsed data from conditions.ts showdown information.
    This function is highly likely to need to be changed, as better definitions of volatile keys are worked on.
    Weather, Status, and Conditions can be pulled from here, though it might not contain all volatile statuses :/

    Args:
        condition_data (Dict[str, Dict]): A dict mapping condition keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # Construct Status Enum
    status_data = {k: v for k, v in condition_data.items() if v.get("effectType") == "Status"}

    status_names: List[Tuple[str, int]] = []
    status_names.append(("FNT", 1))

    for e, key in enumerate(status_data.keys()):
        status_names.append((key.upper(), e + 2))

    status_names = sorted(status_names, key=lambda x: x[1])

    proto_str = create_proto_str("Status", status_names)

    # Constuct Weather Enum
    weather_data = {k: v for k, v in condition_data.items() if v.get("effectType") == "Weather"}

    weather_names: List[Tuple[str, int]] = []
    weather_names.append(("NONE", 1))

    for e, key in enumerate(weather_data.keys()):
        weather_names.append((key.upper(), e + 2))

    weather_names = sorted(weather_names, key=lambda x: x[1])

    proto_str += create_proto_str("Weather", weather_names)

    # Constuct Condition Enum
    condition_data = {k: v for k, v in condition_data.items() if v.get("effectType") is None}

    condition_names: List[Tuple[str, int]] = []

    for e, key in enumerate(condition_data.keys()):
        condition_names.append((key.upper(), e + 1))

    condition_names = sorted(condition_names, key=lambda x: x[1])

    proto_str += create_proto_str("Condition", condition_names)

    return proto_str


def protogen_items(item_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for item information.

    Built expecting parsed data from items.ts showdown information.
    Fields used in the arbirtrary structure:
        - `num`: The id number of the item. This should already be unique. Required.

    Args:
        item_data (Dict[str, Dict]): A dict mapping item name keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # Construct Item Enum
    id_names: List[Tuple[str, int]] = []

    for key, value in item_data.items():
        if value["num"] < 1:
            continue
        id_names.append((key.upper(), value["num"] + 1))

    id_names = sorted(id_names, key=lambda x: x[1])

    proto_str = create_proto_str("Item", id_names, allow_alias=True)

    return proto_str


def protogen_abilities(ability_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for ability information.

    Built expecting parsed data from abilities.ts showdown information.
    Fields used in the arbirtrary structure:
        - `num`: The id number of the ability. This sometimes will not be unique! Required.
    The Enum value uses the format {ABILITY_NUM}{2-DIGIT FORME NUMBER}, with any abilities that share the same id number
    getting assigned their own unique forme number.

    Args:
        ability_data (Dict[str, Dict]): A dict mapping ability name keys to some (mostly) arbitrary data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # construct Ability Enum
    id_names: List[Tuple[str, int]] = []

    # Add each item to the list
    for key, value in ability_data.items():
        if value["num"] < 0:
            continue

        num = str(value["num"] + 1)

        if key.upper() == "VESSELOFRUIN":
            id_names.append((key.upper(), int(num + "00")))
        elif key.upper() == "TABLETSOFRUIN":
            id_names.append((key.upper(), int(num + "01")))
        elif key.upper() == "BEADSOFRUIN":
            id_names.append((key.upper(), int(num + "02")))
        elif key.upper() == "ASONEGLASTRIER":
            id_names.append(("ASONE", int(num + "00")))
            id_names.append(("ASONEGLASTRIER", int(num + "01")))
            id_names.append(("ASONESPECTRIER", int(num + "02")))
        elif key.upper() == "ASONESPECTRIER":
            continue
        else:
            id_names.append((key.upper(), int(num + "00")))

    id_names = sorted(id_names, key=lambda x: x[1])

    proto_str = create_proto_str("Ability", id_names)

    return proto_str


PROTOGEN_DICT = {
    "natures": protogen_natures,
    "pokedex": protogen_pokedex,
    "moves": protogen_moves,
    "typechart": protogen_typechart,
    "items": protogen_items,
    "conditions": protogen_conditions,
    "abilities": protogen_abilities,
}


def protogen():
    """Generate a protobuf file 'dexdata' ready for protoc creation, using each relevant protogen builder.

    This function will create the file "poketypes/protos/dexdata.proto", containing all the Enums that are required
    to add fully automated type-hinting support.
    We rely on `DATA_TYPES` from statics to tell us which json files to read, then `PROTOGEN_DICT` to point to the
    relevant function that can handle Enum Generation from that file.
    Once each component string is created, we will then save the completed string to the file, though the user will
    then still need to create the python Enums using `protoc` and this new file.
    """
    # Import basics (Stat names, any other easy hard-code things)
    with open("poketypes/protos/basics.proto", "r", encoding="utf8") as f:
        proto_str = f.read()

    proto_str += "\n\n"

    # File comments
    proto_str += "//Auto-Generated by protogen.py\n"
    proto_str += f"//Contains data for Gen {CURRENT_GEN}\n\n"

    for dt in DATA_TYPES:
        if dt in PROTOGEN_DICT.keys():
            with open(f"poketypes/protos/json/gen{CURRENT_GEN}_{dt}.json", "r", encoding="utf8") as f:
                data = json.load(f)

            proto_str += PROTOGEN_DICT[dt](data)

    with open("poketypes/protos/dexdata.proto", "w", encoding="utf8") as f:
        f.write(proto_str)


def fetch_latest(verbose: bool = True):
    """Fetch and process the latest Pokemon Showdown typescript data files into more usable json files.

    This will also merge the files to previous generations, since these will be used for generating the PokedexClass
    dictionaries for corresponding previous generations.
    In short, we have two different goals:
        - Type hinting through auto-generating enums
        - Detailed instantiated dataclasses for each pokemon/move/item/etc that can be read at runtime
    The data in these json files will serve as both the ground-truth for our enum labels (DexClass),
    then later the details themselves (PokedexClass)

    Args:
        verbose (bool, optional): Whether to run this function with print statements or not. Defaults to True.
    """
    base_url = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data"

    if verbose:
        print("Starting Showdown JSON Update...")

    for dt in DATA_TYPES:
        if verbose:
            print(f"Starting latest-gen fetch for {dt} data")

        data = fetch_and_clean_ps_data(f"{base_url}/{dt}.ts")
        if verbose:
            print(f"Successfully loaded latest {dt} from pokemon showdown!")

        data_by_gen = {CURRENT_GEN: data}

        for gen in range(CURRENT_GEN - 1, 0, -1):
            next_gen_data = deepcopy(data_by_gen[gen + 1])

            if verbose:
                print(f"Fetching gen {gen} data...")

            this_gen_data = fetch_and_clean_ps_data(f"{base_url}/mods/gen{gen}/{dt}.ts")

            if verbose:
                print(f"Gen {gen} data successfully downloaded!")
                print(f"Backmerging with later data to create gen {gen} file...")

            data_by_gen[gen] = merge(dt, gen, this_gen_data, next_gen_data)

            if verbose:
                print(f"Successfully back-merged gen {gen} {dt}!")

        print(f"Completed all {dt} generation parses!")
        print()

        for gen, data in data_by_gen.items():
            if data is None:
                continue
            with open(f"poketypes/protos/json/gen{gen}_{dt.replace('-', '')}.json", "w", encoding="utf8") as f:
                json.dump(data, f)


if __name__ == "__main__":
    # fetch_latest()

    protogen()
