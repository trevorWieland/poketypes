# poketypes
 Automated classes with full typehinting support for pokemon, abilities, items, and so much more

I'm currently migrating code from a mess of a folder on my local machine to this properly formatted repo.
Once everything is moved over, packaged, and properly tested, an official release will be made.

## Version Details

While the version is below 1.0.0, please note that breaking changes to message/pokedex classes may be made at any time. Additionally, changes may be made without bumping version number, especially while classes/features are being built out. 

Once the version is 1.0.0, we will follow semantic versioning to the letter, though we will additionally make the following
design guarantees where possible:

- Full compatibility with pokemon showdown data (This is our ground-truth)
- Future updated label classes (e.g. DexPokemon) will only *add* labels, and will not change any pre-existing ones
    - This means that the key DexPokemon.POKEMON_MAGIKARP will always have the value 129000, for example
- Outside game knowledge will only be used where absolutely needed, everything else is auto-built from showdown data

We will also follow the following main guidelines for versioning (based on semantic versioning):

    MAJOR.MINOR.PATCH

We consider the following to be MAJOR changes:
- New Generation releases
- Breaking changes

We consider the following to be MINOR changes:
- New fields to messages
- Extra functions to add capability
- New classes
- Major bug fixes (e.g. fixing battle message accuracy)

We consider the following to be PATCH changes:
- Rephrasing field descriptions
- Adding extra type hinting
- Documentation improvements
- Niche bug fixes (e.g. animation detail accuracy)

Thus, we recommend if you are building on top of poketypes to fix to a given MAJOR version, and verify that nothing breaks for your project before upgrading from one MAJOR version to the next. Our top priority is label-consistancy between versions, so that models expecting the same labels will work on all MAJOR versions. If this priority clashes in some way with any other feature, preserving label integrity will come first.