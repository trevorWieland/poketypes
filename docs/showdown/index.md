# Showdown Intro

## 5-Minute Summary
In the `poketypes` package, we include the module `showdown`, which contains pydantic `BaseModel` subclasses for
General and Battle Message formats. This allows for a smoother communication process with Pokemon Showdown, as rather
than needing to build a message parser yourself, relying on relatively limited documentation from Showdown directly,
you can instead build logic to take as input either `Message` or `BattleMessage` objects, which will come pre-parsed,
with full type-hinting and data validation built in.

To start, you can import both from the module `showdown` like so:

    from poketypes.showdown import Message, BattleMessage

Both `Message` and `BattleMessage` are subclasses of `pydantic.BaseModel`, and both also have an additional function
called `from_message`, which takes as input a string, and returns an initialized and parsed object from the input
string message.

    message = BattleMessage.from_string("|poke|p1|Metagross, L80|item")

At this point, `message` will automatically be identified as a `poke` battle message, and will be an instance of the
class `poketypes.showdown.battlemessage.BattleMessage_poke`. Rather than checking with `isinstance`, however, we 
recommend instead checking the `message.BMTYPE` (or `message.MTYPE` for general messages), which is of the type
`poketypes.showdown.BMType`, an Enum of all the different battle message types you can receive. For type hinting
purposes, such as in the signature of a function that would process a given `BattleMessage` subclass, you would do
the following:

    def process_bm_poke(message: poketypes.showdown.battlemessage.BattleMessage_poke):

This will ensure that your IDE will have type hinting support as you process the message, and in the specific example
of `BattleMessage_poke`, will give support in directly accessing the data fields like `message.PLAYER` that are
unique to this `BattleMessage` subclass.

Check out the Guides in this section for some common use-cases of this module, eith step-by-step instructions on each
part of the process. Or if you prefer to learn by reading docs, check out the Reference links below or on the sidebar
to familiarize yourself with some of the different categories of messages.

## Reference Links
For details on all the different kinds of `Message` subclasses, see the reference page [here](reference/standard-messages.md)

For details on all the different kinds of `BattleMessage` subclasses, see the reference page [here](reference/battle-messages.md)