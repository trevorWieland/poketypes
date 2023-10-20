# poketypes/protos/statics.py

"""Provides constant values for use in identifying which data_types are supported, and various gen-specific details.

Contains the following constants:
    - DATA_TYPES: A list of string typechart file names that are supported by the parsing tool in protogen.
    - CURRENT_GEN: The integer latest generation of pokemon.
    - MAX_MON_IDX_PER_GEN: A mapping of gen -> idx for each gen, detailing which pokedex number to cutoff at.
    - MAX_MOVE_IDX_PER_GEN: A mapping of gen -> idx for each gen, detailing which move number to cutoff at.
    - MAX_ABILITY_IDX_PER_GEN: A mapping of gen -> idx for each gen, detailing which ability number to cutoff at.
"""


DATA_TYPES = [
    "typechart",
    "natures",
    "pokedex",
    "learnsets",
    "moves",
    "items",
    "conditions",
    "abilities",
    "formats-data",
]

CURRENT_GEN = 9
MAX_MON_IDX_PER_GEN = {1: 151, 2: 251, 3: 386, 4: 493, 5: 649, 6: 721, 7: 809, 8: 898}
MAX_MOVE_IDX_PER_GEN = {1: 165, 2: 251, 3: 354, 4: 467, 5: 559, 6: 621, 7: 742, 8: 850}
MAX_ABILITY_IDX_PER_GEN = {1: 0, 2: 0, 3: 76, 4: 123, 5: 164, 6: 191, 7: 233, 8: 267}
