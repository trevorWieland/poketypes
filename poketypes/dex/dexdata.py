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


def clean_name(name: str) -> str:
    """
    Formats a given unclean string name as the format needed for searching the Enum
    """


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
