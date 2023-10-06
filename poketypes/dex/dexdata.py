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

from typing import Optional
import unicodedata


def clean_name(name: Optional[str]) -> Optional[str]:
    """
    Formats a given unclean string name as the format needed for searching the Enum
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
            .replace(".", ""),
        )
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )
    return clean_id


def cast2dex(name: str, dex_class) -> int:
    """
    Given a string name, cleans it and casts it to the corresponding entry in the given dex_class

    EX:
    Magikarp -> Cleaned to: MAGIKARP -> DexPokemon.POKEMON_MAGIKARP (Which is secretly the int 129000)

    EX:
    Scizor-Mega -> Cleaned to: SCIZORMEGA -> DexPokemon.POKEMON_SCIZORMEGA (Which is secretly the int 208001)
    """

    clean_id = clean_name(name)

    if clean_id is None:
        return clean_id

    if dex_class == DexAbility:
        return DexAbility.Value(f"ABILITY_" + clean_id)
    elif dex_class == DexCondition:
        return DexCondition.Value(f"CONDITION_" + clean_id)
    elif dex_class == DexGen:
        return DexGen.Value(f"GEN_" + clean_id)
    elif dex_class == DexItem:
        return DexItem.Value(f"ITEM_" + clean_id)
    elif dex_class == DexMove:
        return DexMove.Value(f"MOVE_" + clean_id)
    elif dex_class == DexMoveCategory:
        return DexMoveCategory.Value(f"MOVECATEGORY_" + clean_id)
    elif dex_class == DexMoveTarget:
        return DexMoveTarget.Value(f"MOVETARGET_" + clean_id)
    elif dex_class == DexNature:
        return DexNature.Value(f"NATURE_" + clean_id)
    elif dex_class == DexPokemon:
        return DexPokemon.Value(f"POKEMON_" + clean_id)
    elif dex_class == DexStat:
        return DexStat.Value(f"STAT_" + clean_id)
    elif dex_class == DexStatus:
        return DexStatus.Value(f"STATUS_" + clean_id)
    elif dex_class == DexType:
        return DexType.Value(f"TYPE_" + clean_id)
    elif dex_class == DexWeather:
        return DexWeather.Value(f"WEATHER_" + clean_id)
