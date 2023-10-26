# The PokedexClass
`poketypes.dex.pokedex` OR directly import from `poketypes.dex`

## Basics
Each PokedexClass is a pydantic BaseModel, holding every possibly-useful attribute sourced directly from pokemon showdown typescript files as the ground truth.

## Reference
::: poketypes.dex.pokedex
    options:
        show_source: false
        show_bases: false
        show_symbol_type_heading: true
        docstring_section_style: spacy
        show_symbol_type_toc: true
        heading_level: 3
        annotations_path: source
        members_order: source