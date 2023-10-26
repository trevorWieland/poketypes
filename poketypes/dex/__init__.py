"""Contains Enums and BaseModels for all things pokemon data related.

Enums follow the naming scheme of Dex{NAME}, while the data-rich BaseModels follow the format Pokedex{NAME}.
For example, DexPokemon is an Enum listing all pokemon species and their unique ID, while PokedexPokemon will contain
helpful information about some given pokemon.

Additionally, there is the pre-initialized POKEDEX object, which contain filled real data for all known pokemon fields.
For example, POKEDEX.Gen(5).Pokemon(DexPokemon.POKEMON_MAGIKARP) will return a PokedexPokemon object with gen-5 relevant
information for the pokemon Magikarp. POKEDEX.Gen(6).Item(DexItem.ITEM_ABSOLITE) will return information about the
item Absolite as it is in gen6, etc..
"""


from .dexdata import AnyDex, cast2dex, clean_forme, clean_name
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
from .pokedex import PokedexItem, PokedexMove, PokedexPokemon
