# Why Two Classes?

Once you've started using the showdown message classes, you might start wondering why there is even a split between
`Message` and `BattleMessage` classes at all, why not just have one class called `Message` which works for both?

The answer is really from a convenience standpoint, rather than any technical limitation.

In theory, we could absolutely just have one larger `Message` class that encompasses both of our current message classes,
however in practice we don't use the two that we have today in the same way at all. With Pokemon Showdown's webclient,
battle messages are actually a special type of room-message, sent with a chunk formatting that looks something like:

    """>battle-BATTLEID
    |init|battle
    |title|colress-gpt-test1 vs. colress-gpt-test2
    |j|☆colress-gpt-test1
    """

Already, in order to process this in a parser, we will need special handling to identify that a certain message chunk
is related to some specific room/battle, and then process each remaining line in the chunk as a message pertaining
to that room. Since we're already checking for room information with the ">" at the start, we may as well just check
for ">battle" instead, and parse everything that follows as though it is specific to a battle.

It is theoretically possible that in the future we may decide that simplifying our two class structure into just a single
`Message` class may make sense, but considering that other than some benefits in terms of code organization, there
really isn't much reason to do so either. The `Message` and `BattleMessage` classes are complex enough as they are now,
so if we tried to merge them into one we would really need to consider a different file formatting structure for writing
subclasses, compared to our current solution of one file for `Message` and one file for `BattleMessage`.