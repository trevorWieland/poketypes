"""Contains modules related to showdown message processing.

When parsing messages from showdown, it is the user's responsibility to figure out first whether the message is
related to a specific battle or is a general message. Then, you should pass each stripped, str line of the message
to either Message.from_message or BattleMessage.from_message, which will parse, validate, and return the corresponding
Message/BattleMessage object to you. The returned object will be a subclass of Message/BattleMessage, unless an error
in parsing ocurred, in which case it will be a plain Message/BattleMessage with error information.
"""

from .battlemessage import BattleMessage, BMType, PokemonIdentifier
from .showdownmessage import Message, MType
