from .dexdata_pb2 import (
    DexAbility,
    DexCondition,
    DexGen,
    DexItem,
    DexMove,
    DexMoveCategory,
    DexMoveTag,
    DexNature,
    DexPokemon,
    DexStat,
    DexStatus,
    DexType,
    DexWeather,
)
from pydantic import BaseModel, Field
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


def cast2dex(name: str, dex_class):
    """ """

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
    elif dex_class == DexMoveTag:
        return DexMoveTag.Value(f"MOVETAG_" + clean_id)
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


class PokedexAbility(BaseModel):
    """
    Pokedex class for Abilities.

    Currently doesn't contain any information other than the id/name. Created for API consistency.
    """

    name: str = Field(..., description="Friendly string name of this ability")
    id: DexAbility.ValueType = Field(..., description="The DexAbility ID of this ability")


class PokedexMove(BaseModel):
    """
    Pokedex class for Moves.

    Contains information about move type, accuracy, base power, etc.
    """

    name: str = Field(..., description="Friendly string name of this move")
    id: DexMove.ValueType = Field(..., description="The DexMove ID of this move")

    accuracy: Optional[int] = Field(..., description="The accuracy of this move. None if the move bypasses accuracy")
    base_power: int = Field(..., description="The base power of the move")
    pp: int = Field(..., description="The pp of this move")
    priority: int = Field(..., description="The priority of the move")

    category: DexMoveCategory.ValueType = Field(..., description="The move category as a DexMoveCategory")
