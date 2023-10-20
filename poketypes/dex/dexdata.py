# poketypes/dex/dexdata.py

"""Provides tools for cleaning Dex IDs back and forth from strings, as well as other utility functions."""

import unicodedata
from typing import Optional, Union

from .dexdata_pb2 import (
    DexAbility,
    DexCondition,
    DexGen,
    DexItem,
    DexMove,
    DexMoveCategory,
    DexMoveTarget,
    DexNature,
    DexPokemon,
    DexStat,
    DexStatus,
    DexType,
    DexWeather,
)

AnyDex = Union[
    type[DexAbility],
    type[DexCondition],
    type[DexGen],
    type[DexItem],
    type[DexMove],
    type[DexMoveCategory],
    type[DexMoveTarget],
    type[DexNature],
    type[DexPokemon],
    type[DexStat],
    type[DexStatus],
    type[DexType],
    type[DexWeather],
]


def clean_name(name: Optional[str]) -> Optional[str]:
    """Format a given uncleaned string name as the format needed for searching the corresponding Enum.

    Args:
        name (Optional[str]): An optional name to clean. If None is given, we immediately return None.

    Returns:
        Optional[str]: The clean-form of the input name, if it wasn't None or blank.
    """
    if name is None or name == "":
        return None

    clean_id = (
        unicodedata.normalize(
            "NFKD",
            name.upper()
            .replace("-", "")
            .replace("’", "")
            .replace("'", "")
            .replace(" ", "")
            .replace("*", "")
            .replace(":", "")
            .replace("%", "")
            .replace(".", "")
            .replace(")", "")
            .replace("(", ""),
        )
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )
    return clean_id


def clean_forme(species: DexPokemon.ValueType) -> DexPokemon.ValueType:
    """Transform a pokemon species (DexPokemon) into the string name of it's base forme.

    Makes use of the fact that DexPokemon are of the form {dex_number}{3-digit forme number},
    and that the base forme is always forme-number `000`.
    If this changes, this function will no longer work.

    Args:
        species (DexPokemon.ValueType): The input species to clean to base forme.

    Returns:
        DexPokemon.ValueType: The corresponding ID of the base forme species.
    """
    clean_species = (species // 1000) * 1000
    return clean_species


def cast2dex(name: str, dex_class: AnyDex) -> int:
    """Clean and cast name to the corresponding entry in the given dex_class.

    EX:
    Magikarp -> Cleaned to: MAGIKARP -> DexPokemon.POKEMON_MAGIKARP (Which is secretly the int 129000)

    EX:
    Scizor-Mega -> Cleaned to: SCIZORMEGA -> DexPokemon.POKEMON_SCIZORMEGA (Which is secretly the int 208001)

    Args:
        name (str): The name of the entry.
        dex_class (AnyDex): Which Dex Enum to use in labeling. Must be a valid Dex{NAME} class.

    Returns:
        int: The corresponding value for this cleaned entry.
    """
    clean_id = clean_name(name)

    if clean_id is None:
        return clean_id

    if dex_class == DexAbility:
        return DexAbility.Value(f"ABILITY_{clean_id}")
    elif dex_class == DexCondition:
        return DexCondition.Value(f"CONDITION_{clean_id}")
    elif dex_class == DexGen:
        return DexGen.Value(f"GEN_{clean_id}")
    elif dex_class == DexItem:
        return DexItem.Value(f"ITEM_{clean_id}")
    elif dex_class == DexMove:
        return DexMove.Value(f"MOVE_{clean_id}")
    elif dex_class == DexMoveCategory:
        return DexMoveCategory.Value(f"MOVECATEGORY_{clean_id}")
    elif dex_class == DexMoveTarget:
        return DexMoveTarget.Value(f"MOVETARGET_{clean_id}")
    elif dex_class == DexNature:
        return DexNature.Value(f"NATURE_{clean_id}")
    elif dex_class == DexPokemon:
        return DexPokemon.Value(f"POKEMON_{clean_id}")
    elif dex_class == DexStat:
        return DexStat.Value(f"STAT_{clean_id}")
    elif dex_class == DexStatus:
        return DexStatus.Value(f"STATUS_{clean_id}")
    elif dex_class == DexType:
        return DexType.Value(f"TYPE_{clean_id}")
    elif dex_class == DexWeather:
        return DexWeather.Value(f"WEATHER_{clean_id}")
