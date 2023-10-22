# Welcome to the Poketypes Docs!

This site contains the project documentation for the `poketypes` project, whose goal is to provide *clear*, *consistent*, *correct* data about Pokemon, using the same base data as Pokemon Showdown.


## Table Of Contents

This package provides two very useful modules for handling Pokemon data:

- [`dex`](dex/index.md): contains Pokemon Enums, Data Classes, and an instantiated information center `Gen`
- [`showdown`](showdown/index.md): provides two main classes `Message` and `BattleMessage`, for processing showdown communications

Based on the needs of your project, you may need one or both of these.

There is also the module [`protos`](protos/index.md), which contains the logic for generating the `DexClass` core Enums used in `dex`.
As an end-user of the typing and data structures in ths package, you don't need to access anything in `protos`, however,
if you want to have data-structure / enum support for more niche showdown mods, contributions to the `protos` class 
would be greatly appreciated.

## Project Overview

::: poketypes





