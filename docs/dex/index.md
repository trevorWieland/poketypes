# Dex Intro

## 5-Minute Summary
In the `poketypes` package, we include the module `dex`, which contains two different types of data structures, so-called DexClass Enums, which contain uniquely enumerated labels for everything from pokemon formes to items to moves and more. The other contained data structure is the PokedexClass BaseModel, which are pydantic BaseModels, meant for holding reference material about a specific corresponding DexClass label. 

For example, one specific DexClass is the `DexPokemon`, an Enum which maps every distinct pokemon forme (base, cosmetic, temporary, etc.) to a unique integer. So we have things like `DexPokemon.POKEMON_MAGIKARP`, which is mapped to the integer 129000.
Then, we have the `PokedexPokemon` BaseModel, whose purpose would be to store all useful information about each specific corresponding `DexPokemon` id, such as the types of the pokemon (each stored as a `DexType`), the learnset of the pokemon (stored as `DexMove`), etc..

This means that if you are building logic for interpretting a pokemon battle, rather than relying on string comparisons which can both be slow and inconsistent, you can instead use included functions such as `cast2dex`, which can take input strings and a relevant DexClass, and return the correct label to use.

These extra layers of labeling may seem cumbersome to work with at first, but since we provide all of the cleaning functions you could need to transform between them, the trade-off for using just a few extra lines of code is 100% guarunteed label consistency and accuracy, with minimal risk of typos.

For instance, you might care about checking if an opponent pokemon can potentially have the ability levitate. Then you could directly use `DexAbility.ABILITY_LEVITATE`, checking if this label exists in the corresponding `PokedexPokemon.abilities`. Since no string comparisons are happening, there's no risk of accidentally spelling levitate wrong since the type hinting will inform you.

Lastly, there is the actual pokedex instances, which are accessed by calling `dex.gen()`. This returns a pydantic object that has a pre-instantiated dictionary for Pokemon, Moves, and Items, which each map from their corresponding DexClass to their corresponding PokedexClass. For example, `dex.gen(5).pokemon[DexPokemon.POKEMON_MAGIKARP]` will return the `PokedexPokemon` object for Magikarp, will all the details already filled out, as it was in generation 5. If you leave out the gen number, it will automatically use the latest generation available.

## Reference Links
For details on all the different kinds of DexClasses, see the reference page [here](reference/dex-classes.md)

For details on all the different kinds of PokedexClasses, see the reference page [here](reference/pokedex-classes.md)

For details on all the different cleaning utilities, see the reference page [here](reference/utilities.md)

For details on the gen function, see the reference page [here](reference/pokedex-instance.md)