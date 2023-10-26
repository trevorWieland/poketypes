# Building a Replay Log Parser

## Introduction

This tutorial will guide usage of `poketypes.showdown` to create a simple replay log parser, which can read any
arbitrary Pokemon Showdown replay file, and turn it into a list of `BattleMessage` subclass objects, that you could
then proceed to do some sort of analysis or transformation on.

Since we'll be processing a Replay log in this example, we will only be using `poketypes.showdown.BattleMessage`, but
similar concepts can be applied for processing any message sent by showdown, so long as you make the distinction between
general messages and message chunks that target a specific battle.

## Prerequisites

Make sure that you have `poketypes` installed to your virtual environment, which you can do with:

    pip install poketypes

Additionally, go ahead and download the replay file [here](https://replay.pokemonshowdown.com/oumonotype-82345404).
If you click the Download button on this page, it should download a .html file called 'OUMonotype-2014-01-29-kdarewolf-onox.html',
which we will use as an example, but any replay file should work.

## Step 1: Extracting the Battle Log

Replay files are stored in html files, which means we need to extract the text log that we want to parse first.

To do that, since we only need very basic html extraction, we can 
