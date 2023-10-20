# poketypes/protos/protogen.py

"""Provides tools for generating consistent protobuf Enums from pokemon data fields.

The primary goal of this module is for every Enum created to be consistent across generations from a label-number
perspective. Meaning that while future generations of pokemon will certainly have new keys assigned for new pokemon,
any pokemon introduced previously will have the same label-number in every generation then on.
"""

import json
import re
import unicodedata
from copy import deepcopy
from typing import Dict

import requests
from mergers import merge
from statics import CURRENT_GEN, DATA_TYPES


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


def protogen_natures(nature_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for natures.

    Built expecting parsed data from natures.ts showdown information.
    Does not use any value information, only the keys from the dictionary.

    Args:
        nature_data (Dict[str, Dict]): A dict mapping nature keys to some arbitrary unused data structure.

    Returns:
        str: A multi-line string containing a properly formatted Enum.
    """
    # Section comments
    proto_str = "//Contains data for Pokemon Natures\n"

    # Start Enum Construction
    proto_str += "enum DexNature {\n"
    proto_str += "\tNATURE_UNASSIGNED = 0;\n"

    # Add each nature to the enum
    for e, key in enumerate(nature_data.keys()):
        proto_str += f"\tNATURE_{key.upper()} = {e+1};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    # Section comments
    proto_str = "//Contains data for Pokemon\n"

    # Sort and identify unique numbers for each pokemon
    # Number definition: {DEX_NUM}{FORM_NUM zfilled to 3 places}
    # Current definitions supports up to 999 versions of charizard before it breaks :]

    pokemon = []
    last_poke_num = None
    c = 0
    for key, value in pokedex_data.items():
        if value["num"] < 1:
            # We skip fakemon
            continue

        if last_poke_num is None:
            num = int(str(value["num"]) + "".zfill(3))
        elif last_poke_num == value["num"]:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(3))
        else:
            c = 0
            num = int(str(value["num"]) + str(c).zfill(3))

        pokemon.append((key.upper(), num))
        last_poke_num = value["num"]

        for cosmetic in value.get("cosmeticFormes", []):
            clean_name = (
                unicodedata.normalize(
                    "NFKD",
                    cosmetic.upper()
                    .replace("-", "")
                    .replace("’", "")
                    .replace("'", "")
                    .replace(" ", "")
                    .replace("*", "")
                    .replace(":", "")
                    .replace(".", ""),
                )
                .encode("ASCII", "ignore")
                .decode("ASCII"),
            )[0]

            c += 1
            pokemon.append((clean_name, int(str(value["num"]) + str(c).zfill(3))))

    pokemon = sorted(pokemon, key=lambda x: x[1])

    # Start Enum Construction
    proto_str += "enum DexPokemon {\n"
    proto_str += "\tPOKEMON_UNASSIGNED = 0;\n"

    # Add each nature to the enum
    for key, num in pokemon:
        proto_str += f"\tPOKEMON_{key} = {num};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

    return proto_str


def protogen_moves(move_data: Dict[str, Dict]) -> str:
    """Generate a protobuf formatted string with Enum info for moves.

    Built expecting parsed data from moves.ts showdown information.
    Fields used in the arbirtrary structure:
        - `num`: The id number of the pokemon. Different formes of the same move share this. Required.
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
    moves = []
    last_move_num = None
    c = 0
    for key, value in move_data.items():
        if value["num"] < 1:
            # We skip fake moves
            continue

        if last_move_num is None:
            num = int(str(value["num"]) + "".zfill(2))
        elif last_move_num == value["num"]:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(2))
        else:
            c = 0
            num = int(str(value["num"]) + str(c).zfill(2))

        moves.append((key.upper(), num))
        last_move_num = value["num"]

        if "hiddenpower" in key:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(2))
            moves.append((key.upper() + "60", num))
        elif "return" in key:
            c += 1
            num = int(str(value["num"]) + str(c).zfill(2))
            moves.append((key.upper() + "102", num))

    moves.append(("RECHARGE", 1))

    moves = sorted(moves, key=lambda x: x[1])

    # Start Enum Construction
    proto_str += "enum DexMove {\n"
    proto_str += "\tMOVE_UNASSIGNED = 0;\n"

    # Add each nature to the enum
    for key, num in moves:
        proto_str += f"\tMOVE_{key} = {num};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    # Section comments
    proto_str = "//Contains data for Pokemon Types\n"

    # Start Enum Construction
    proto_str += "enum DexType {\n"
    proto_str += "\tTYPE_UNASSIGNED = 0;\n"

    # Add each type to the enum
    for e, key in enumerate(typechart_data.keys()):
        proto_str += f"\tTYPE_{key.upper()} = {e+1};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    # Section comments
    proto_str = ""

    # Start Enum Construction for Statuses
    proto_str += "//Contains data for Pokemon Statuses\n"

    proto_str += "enum DexStatus {\n"
    proto_str += "\tSTATUS_UNASSIGNED = 0;\n"

    proto_str += "\tSTATUS_FNT = 1;\n"

    filtered_data = {k: v for k, v in condition_data.items() if v.get("effectType") == "Status"}

    # Add each type to the enum
    for e, key in enumerate(filtered_data.keys()):
        proto_str += f"\tSTATUS_{key.upper()} = {e+2};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

    # Start Enum Construction for Weathers
    proto_str += "//Contains data for Pokemon Weathers\n"

    proto_str += "enum DexWeather {\n"
    proto_str += "\tWEATHER_UNASSIGNED = 0;\n"
    proto_str += "\tWEATHER_NONE = 1;\n"

    filtered_data = {k: v for k, v in condition_data.items() if v.get("effectType") == "Weather"}

    # Add each type to the enum
    for e, key in enumerate(filtered_data.keys()):
        proto_str += f"\tWEATHER_{key.upper()} = {e+2};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

    # Start Enum Construction for Weathers
    proto_str += "//Contains data for Pokemon Conditions\n"

    proto_str += "enum DexCondition {\n"
    proto_str += "\tCONDITION_UNASSIGNED = 0;\n"

    filtered_data = {k: v for k, v in condition_data.items() if v.get("effectType") is None}

    # Add each type to the enum
    for e, key in enumerate(filtered_data.keys()):
        proto_str += f"\tCONDITION_{key.upper()} = {e+1};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    # Section comments
    proto_str = "//Contains data for Pokemon Items\n"

    # Start Enum Construction
    proto_str += "enum DexItem {\n"
    proto_str += "\toption allow_alias = true;\n"
    proto_str += "\tITEM_UNASSIGNED = 0;\n"

    # Add each item to the enum
    for key, value in item_data.items():
        if value["num"] < 1:
            continue
        proto_str += f"\tITEM_{key.upper()} = {value['num'] + 1};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    # Section comments
    proto_str = "//Contains data for Pokemon Abilities\n"

    # Start Enum Construction
    proto_str += "enum DexAbility {\n"
    proto_str += "\tABILITY_UNASSIGNED = 0;\n"

    # Add each item to the enum
    for key, value in ability_data.items():
        if value["num"] < 0:
            continue
        if key.upper() == "VESSELOFRUIN":
            proto_str += f"\tABILITY_{key.upper()} = {str(value['num'] + 1) + '00'};\n"
        elif key.upper() == "TABLETSOFRUIN":
            proto_str += f"\tABILITY_{key.upper()} = {str(value['num'] + 1) + '01'};\n"
        elif key.upper() == "BEADSOFRUIN":
            proto_str += f"\tABILITY_{key.upper()} = {str(value['num'] + 1) + '02'};\n"
        elif key.upper() == "ASONEGLASTRIER":
            proto_str += f"\tABILITY_ASONE = {str(value['num'] + 1)};\n"
            proto_str += f"\tABILITY_ASONEGLASTRIER = {str(value['num'] + 1) + '01'};\n"
            proto_str += f"\tABILITY_ASONESPECTRIER = {str(value['num'] + 1) + '02'};\n"
        elif key.upper() == "ASONESPECTRIER":
            continue
        else:
            proto_str += f"\tABILITY_{key.upper()} = {value['num'] + 1};\n"

    # Finalize the enum with a closing bracket
    proto_str += "}\n\n"

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
    fetch_latest()

    protogen()
