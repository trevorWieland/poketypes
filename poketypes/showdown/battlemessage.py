# poketypes/showdown/battlemessage.py

"""Contains BaseModels for BattleMessage parsing and processing.

Remember to use BattleMessage.from_message directly, unless you are building test cases where you want to assert that
a given message leads to a certain subclass of BattleMessage. `from_message` will auto-detect which BMType the given
message corresponds to, and return the associated subclass (or an error detailing what went wrong) for you.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum, unique
from typing import Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel, Field

from ..dex import DexAbility, DexGen, DexItem, DexMove, DexPokemon, DexStatus, DexType, DexWeather, cast2dex


@unique
class BMType(str, Enum):
    """String-Enum for holding all unique categories of Showdown Battle Messages.

    See https://github.com/smogon/pokemon-showdown/blob/master/sim/SIM-PROTOCOL.md for the full list of battle messages
    """

    # Initialization message types
    player = "player"
    teamsize = "teamsize"
    gametype = "gametype"
    gen = "gen"
    tier = "tier"
    rated = "rated"
    rule = "rule"
    clearpoke = "clearpoke"
    poke = "poke"
    start = "start"
    teampreview = "teampreview"

    # Progress message types
    empty = ""
    request = "request"
    inactive = "inactive"
    inactiveoff = "inactiveoff"
    upkeep = "upkeep"
    turn = "turn"
    win = "win"
    tie = "tie"
    expire = "expire"
    t = "t:"

    # Major actions
    move = "move"
    switch = "switch"
    drag = "drag"
    detailschange = "detailschange"
    replace = "replace"
    swap = "swap"
    cant = "cant"
    faint = "faint"

    # Minor actions
    fail = "-fail"
    block = "-block"
    notarget = "-notarget"
    miss = "-miss"
    damage = "-damage"
    heal = "-heal"
    sethp = "-sethp"
    status = "-status"
    curestatus = "-curestatus"
    cureteam = "-cureteam"
    boost = "-boost"
    unboost = "-unboost"
    setboost = "-setboost"
    swapboost = "-swapboost"
    invertboost = "-invertboost"
    clearboost = "-clearboost"
    clearallboost = "-clearallboost"
    clearpositiveboost = "-clearpositiveboost"
    clearnegativeboost = "-clearnegativeboost"
    copyboost = "-copyboost"
    weather = "-weather"
    fieldstart = "-fieldstart"
    fieldend = "-fieldend"
    sidestart = "-sidestart"
    sideend = "-sideend"
    swapsideconditions = "-swapsideconditions"
    volstart = "-start"
    volend = "-end"
    crit = "-crit"
    supereffective = "-supereffective"
    resisted = "-resisted"
    immune = "-immune"
    item = "-item"
    enditem = "-enditem"
    ability = "-ability"
    endability = "-endability"
    transform = "-transform"
    mega = "-mega"
    primal = "-primal"
    burst = "-burst"
    zpower = "-zpower"
    zbroken = "-zbroken"
    activate = "-activate"
    hint = "-hint"
    center = "-center"
    message = "-message"
    mess = "message"
    combine = "-combine"
    waiting = "-waiting"
    prepare = "-prepare"
    mustrecharge = "-mustrecharge"
    nothing = "-nothing"
    hitcount = "-hitcount"
    singlemove = "-singlemove"
    singleturn = "-singleturn"
    formechange = "-formechange"
    terastallize = "-terastallize"
    fieldactivate = "-fieldactivate"

    # Misc battle messages
    error = "error"
    bigerror = "bigerror"
    init = "init"
    deinit = "deinit"
    title = "title"
    j = "j"
    J = "J"
    join = "join"
    l = "l"  # noqa: E741
    L = "L"
    leave = "leave"
    raw = "raw"
    anim = "-anim"

    # Internal error case
    unknown = "unknown"


class PokeStat(str, Enum):
    """Helper enum for identifying valid stats."""

    attack = "atk"
    defence = "def"
    special_attack = "spa"
    special_defence = "spd"
    speed = "spe"

    hp = "hp"

    evasion = "evasion"
    accuracy = "accuracy"


class PokemonIdentifier(BaseModel):
    """A BaseModel giving details about which Pokemon is being talked about."""

    IDENTITY: str = Field(
        ...,
        description="The unique identifier for a pokemon. Looks like `ARCANINE` if the input is `p1: Arcanine`",
    )
    PLAYER: str = Field(..., description="The player this pokemon belongs to", pattern=r"p[1-4]")

    SLOT: Optional[str] = Field(
        None,
        description="Optionally, the slot this pokemon is in. Will be None if slot info isn't given in the message",
    )

    @staticmethod
    def from_ident_string(ident: str) -> "PokemonIdentifier":
        """Create a new PokemonIdentifier from an identifier string *without* slot information.

        Args:
            ident (str): An input string to extract field information from. Looks like "p1: Arcanine"

        Returns:
            PokemonIdentifier: A newly created PokemonIdentifier object from this string
        """
        return PokemonIdentifier(IDENTITY=ident.split(":")[1].strip().upper(), PLAYER=ident.split(":")[0], SLOT=None)

    @staticmethod
    def from_slot_string(slot: str) -> "PokemonIdentifier":
        """Create a new PokemonIdentifier from an identifier string *with* slot information.

        Args:
            slot (str): An input string to extract field information from. Looks like "p1a: Arcanine"

        Returns:
            PokemonIdentifier: A newly created PokemonIdentifier object from this string
        """
        return PokemonIdentifier(
            IDENTITY=slot.split(":")[1].strip().upper(), PLAYER=slot[:2].split(":")[0], SLOT=slot[2]
        )

    @staticmethod
    def from_string(string: str) -> "PokemonIdentifier":
        """Auto-Create a new PokemonIdentifier based on which type of identity string is given.

        Args:
            string (str): An input string to extract field information from. Looks like "p1a: Arcanine"

        Returns:
            PokemonIdentifier: A newly created PokemonIdentifier object from this string
        """
        if len(string.split(":")[0]) == 3:
            return PokemonIdentifier.from_slot_string(string)
        else:
            return PokemonIdentifier.from_ident_string(string)


class EffectType(str, Enum):
    """Helper class to identify which category of effect is being activated."""

    ability = "ability"
    item = "item"
    move = "move"
    status = "status"
    weather = "weather"
    condition = "condition"
    volatile = "volatile"
    pokemon = "pokemon"


class Effect(BaseModel):
    """A helper class for many Battle Message types that rely on *something* happening to cause the message effect."""

    EFFECT_TYPE: Optional[EffectType] = Field(None, description="The category of effect causing this.")

    # TODO: Add a validator for EFFECT_NAME
    EFFECT_NAME: str = Field(..., description="The name of the effect")

    # TODO: Add a validator for secondary effect name
    SEC_EFFECT_NAME: Optional[str] = Field(
        None,
        description="Secondary effect that is being impacted by this primary effect.",
    )

    EFFECT_SOURCE: Optional[PokemonIdentifier] = Field(
        None, description="If the effect is being caused by another different pokemon, then this will be that pokemon"
    )


class BattleMessage(BaseModel):
    """The base class for all specific BattleMessage subclasses to be built from.

    When parsing a string battle message, you should directly use this class's `from_message` function, which will
    auto-identify which subclass (if any) the given string belongs to.

    Across all BattleMessages, you will be able to access both BMTYPE and BATTLE_MESSAGE, though you shouldn't need
    to access BATTLE_MESSAGE directly. (If you do, then we must be missing some data that exists in the raw string)

    Attributes:
        BMTYPE: The message type of this battle message. Must be a vaild showdown battle message.
        BATTLE_MESSAGE: The raw message line as sent from showdown. Shouldn't need to be used but worth keeping.
        ERR_STATE: The error type of this battle message if it failed to parse
    """

    BMTYPE: BMType = Field(
        ...,
        description="The message type of this battle message. Must be a vaild showdown battle message.",
    )
    BATTLE_MESSAGE: str = Field(
        ...,
        description="The raw message line as sent from showdown. Shouldn't need to be used but worth keeping.",
    )

    ERR_STATE: Optional[
        Literal["UNKNOWN_BMTYPE", "MISSING_DICT_CLASS", "IMPLEMENTATION_NOT_READY", "PARSE_ERROR"]
    ] = Field(None, description="The error type of this battle message if it failed to parse")

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage":
        """Create a specific BattleMessage object from a raw message.

        For example, given a message '|faint|p2a: Umbreon', this will create a new BattleMessage_faint with fields
        extracted from the text properly.
        """
        if battle_message.strip() == "" or (
            battle_message.split("|")[1] == "request" and battle_message.split("|")[2] == ""
        ):
            return BattleMessage(BMTYPE=BMType.empty, BATTLE_MESSAGE="")

        try:
            bmtype = BMType(battle_message.split("|")[1])
            bm_class = bmtype_to_bmclass[bmtype]
        except ValueError:
            print(
                f"Failed to identify which BMType we should use for battle message key {battle_message.split('|')[1]}."
            )
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="UNKNOWN_BMTYPE")

            return bm
        except KeyError:
            print(f"BMType {bmtype} does not have a class in the dictionary! This is probably an error!")
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="MISSING_DICT_CLASS")

            return bm

        try:
            bm = bm_class.from_message(battle_message)
        except NotImplementedError:
            print(f"BMType {bmtype}'s extraction implementation isn't ready yet!")
            print(battle_message)
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="IMPLEMENTATION_NOT_READY")
        except Exception as ex:
            print(f"BMType {bmtype} failed to build from message {battle_message} due to a(n) {type(ex)}: {ex}")
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="PARSE_ERROR")

        return bm


class BattleMessage_player(BattleMessage):
    """Message containing player information.

    Attributes:
        PLAYER: The player id of this player
        USERNAME: The username of the player
        AVATAR: Either a number id of the user's avatar or a custom value
        RATING: The elo of the player in the current format, if applicable

    Note: Use Case(s)
        - To communicate player username/avatar/rating information.

    Info: Message Format(s)
        - |player|PLAYER|USERNAME|AVATAR|RATING

    Example: Input Example(s)
        - |player|p1|colress-gpt-test1|colress|1520
        - |player|p2|colress-gpt-test2|265|1229
    """

    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")
    USERNAME: str = Field(..., description="The username of the player")
    AVATAR: Union[int, str] = Field(..., description="Either a number id of the user's avatar or a custom value")
    RATING: Optional[int] = Field(None, description="The elo of the player in the current format, if applicable")

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_player":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_player(
            BMTYPE=BMType.player,
            BATTLE_MESSAGE=battle_message,
            PLAYER=bm_split[2],
            USERNAME=bm_split[3],
            AVATAR=bm_split[4] if not bm_split[4].isnumeric() else int(bm_split[4]),
            RATING=None if bm_split[5] == "" else bm_split[5],
        )


class BattleMessage_teamsize(BattleMessage):
    """Message containing teamsize information.

    Attributes:
        PLAYER: The player id of this player
        NUMBER: The number of pokemon your opponent has.

    Note: Use Case(s)
        - To communicate player team size.

    Info: Message Format(s)
        - |teamsize|PLAYER|NUMBER

    Example: Input Example(s)
        - |teamsize|p1|6
    """

    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")
    NUMBER: int = Field(..., description="The number of pokemon your opponent has.")

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_teamsize":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_teamsize(
            BMTYPE=BMType.teamsize,
            BATTLE_MESSAGE=battle_message,
            PLAYER=bm_split[2],
            NUMBER=bm_split[3],
        )


class BattleMessage_gametype(BattleMessage):
    """Message containing gametype information.

    Attributes:
        GAMETYPE: The gametype of this format

    Note: Use Case(s)
        - To communicate the game type (singles, doubles, triples, etc.)

    Info: Message Format(s)
        - |gametype|GAMETYPE

    Example: Input Example(s)
        - |gametype|singles
    """

    GAMETYPE: Literal["singles", "doubles", "triples", "multi", "freeforall"] = Field(
        ..., description="The gametype of this format"
    )

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_gametype":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_gametype(
            BMTYPE=BMType.gametype,
            BATTLE_MESSAGE=battle_message,
            GAMETYPE=bm_split[2],
        )


class BattleMessage_gen(BattleMessage):
    """Message containing gen information.

    Attributes:
        GENNUM: The integer generation number of this format

    Note: Use Case(s)
        - To communicate the generation number.

    Info: Message Format(s)
        - |gen|GENNUM

    Example: Input Example(s)
        - |gen|5
    """

    GENNUM: DexGen.ValueType = Field(..., description="The integer generation number of this format")

    def from_message(battle_message: str) -> "BattleMessage_gen":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_gen(
            BMTYPE=BMType.gen,
            BATTLE_MESSAGE=battle_message,
            GENNUM=bm_split[2],
        )


class BattleMessage_tier(BattleMessage):
    """Message containing format information.

    Attributes:
        FORMATNAME: The game format of this match

    Note: Use Case(s)
        - To communicate the format of this battle.

    Info: Message Format(s)
        - |tier|FORMATNAME

    Example: Input Example(s)
        - |tier|[Gen 5] Random Battle
    """

    FORMATNAME: str = Field(..., description="The game format of this match")

    def from_message(battle_message: str) -> "BattleMessage_tier":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_tier(
            BMTYPE=BMType.tier,
            BATTLE_MESSAGE=battle_message,
            FORMATNAME=bm_split[2],
        )


class BattleMessage_rated(BattleMessage):
    """Message containing rating information.

    Attributes:
        MESSAGE: An optional message used in tournaments

    Note: Use Case(s)
        - To communicate any extra rules/clauses for this format.

    Info: Message Format(s)
        - |rated|MESSAGE

    Example: Input Example(s)
        - |rated|
    """

    MESSAGE: Optional[str] = Field(None, description="An optional message used in tournaments")

    def from_message(battle_message: str) -> "BattleMessage_rated":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_rated(
            BMTYPE=BMType.rated,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_rule(BattleMessage):
    """Message containing extra rule information.

    Attributes:
        RULE: The name of the rule
        DESCRIPTION: A description of this rule

    Note: Use Case(s)
        - To communicate any extra rules/clauses for this format.

    Info: Message Format(s)
        - |rule|RULE: DESCRIPTION

    Example: Input Example(s)
        - |rule|HP Percentage Mod: HP is shown in percentages
    """

    RULE: str = Field(..., description="The name of the rule")
    DESCRIPTION: str = Field(..., description="A description of this rule")

    def from_message(battle_message: str) -> "BattleMessage_rule":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_rule(
            BMTYPE=BMType.rule,
            BATTLE_MESSAGE=battle_message,
            RULE=bm_split[2].split(":")[0],
            DESCRIPTION=":".join(bm_split[2].split(":")[1:]).strip(),
        )


class BattleMessage_clearpoke(BattleMessage):
    """Message containing a clearpoke notification.

    Note: Use Case(s)
        - To signal that teampreview is starting.

    Info: Message Format(s)
        - |clearpoke

    Example: Input Example(s)
        - |clearpoke
    """

    def from_message(battle_message: str) -> "BattleMessage_clearpoke":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_clearpoke(
            BMTYPE=BMType.clearpoke,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_poke(BattleMessage):
    """Message containing base-forme-only information about a pokemon, presented in teampreview.

    Attributes:
        PLAYER: The player id of this player
        SPECIES: The forme-less species for this pokemon
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the string type of the new type. Else None.
        HAS_ITEM: Whether or not the pokemon is holding an item

    Note: Use Case(s)
        - To communicate base-forme, simple pokemon information for teampreview

    Info: Message Format(s)
        - |poke|PLAYER|DETAILS|ITEM

    Example: Input Example(s)
        - |poke|p1|Metagross, L80|item
    """

    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")

    SPECIES: DexPokemon.ValueType = Field(..., description="The forme-less species for this pokemon")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[DexType.ValueType] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
    )

    HAS_ITEM: bool = Field(False, description="Whether or not the pokemon is holding an item")

    def from_message(battle_message: str) -> "BattleMessage_poke":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        details = bm_split[3].split(",")

        species = details[0].strip()
        level = 100
        gender = None
        shiny = False
        tera = None

        item = details[-1] == "item"

        if len(details) > 1:
            for detail in details[1:]:
                detail = detail.strip()
                if "tera" in detail:
                    tera = detail.split(":")[1].strip()
                elif "shiny" in detail:
                    shiny = True
                elif "L" in detail:
                    level = int(detail[1:])
                elif "M" in detail:
                    gender = "M"
                elif "F" in detail:
                    gender = "F"

        return BattleMessage_poke(
            BMTYPE=BMType.poke,
            BATTLE_MESSAGE=battle_message,
            PLAYER=bm_split[2],
            SPECIES=cast2dex(species, DexPokemon),
            LEVEL=level,
            GENDER=gender,
            SHINY=shiny,
            TERA=cast2dex(tera, DexType),
            HAS_ITEM=item,
        )


class BattleMessage_start(BattleMessage):
    """Message signaling the start of a battle.

    Note: Use Case(s)
        - To communicate that the battle has started (teampreview is over)

    Info: Message Format(s)
        - |start

    Example: Input Example(s)
        - |start
    """

    def from_message(battle_message: str) -> "BattleMessage_start":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_start(
            BMTYPE=BMType.start,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_teampreview(BattleMessage):
    """Message signaling to make a teampreview team-order decision.

    Note: Use Case(s)
        - To communicate that the user needs to select a team-order.

    Info: Message Format(s)
        - |teampreview

    Example: Input Example(s)
        - |teampreview
    """

    def from_message(battle_message: str) -> "BattleMessage_teampreview":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_teampreview(
            BMTYPE=BMType.teampreview,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_empty(BattleMessage):
    """Completely blank message.

    Note: Use Case(s)
        - To separate sections in a battle log

    Info: Message Format(s)
        - |

    Example: Input Example(s)
        - |
    """

    def from_message(battle_message: str) -> "BattleMessage_empty":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_empty(
            BMTYPE=BMType.empty,
            BATTLE_MESSAGE=battle_message,
        )


class RequestPoke(BaseModel):
    """A helper class to contain details about a pokemon held in the `side` data of a request.

    Attributes:
        IDENT: The string pokemon identifier (without slot information)
        SPECIES: The species for this pokemon, including forme
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the DexType of the new type. Else None.
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon, None if the pokemon is fainted
        STATUS: The status of the pokemon. Can be None if there is no status
        ACTIVE: Whether the pokemon is active or not
        STATS: A dictionary of stat->values for each stat of this pokemon (before modifiers)
        MOVES: The list of moves this pokemon knows, without pp information
        BASE_ABILITY: The base ability of this pokemon, ignoring any ability switching shenanigans
        ABILITY: The current ability of this pokemon. Only used in certain gens, can be None
        ITEM: The held item of this pokemon. None if no item is held
        POKEBALL: Which pokeball this pokemon is contained in
        COMMANDING: Tatsugiri commander mechanic. True if active, false if not, None if older gen
        REVIVING: Revival Blessing flag (I think?)
        TERATYPE: The type that this pokemon can teratype into
        TERASTALLIZED: The type that this pokemon is teratyped into. None if not applicable
    """

    IDENT: PokemonIdentifier = Field(..., description="The string pokemon identifier (without slot information)")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[DexType.ValueType] = Field(
        None,
        description="If this pokemon is teratyped, the DexType of the new type. Else None.",
    )

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: Optional[int] = Field(
        None,
        description="The maximum HP of the pokemon, None if the pokemon is fainted",
    )
    STATUS: Optional[DexStatus.ValueType] = Field(
        None, description="The status of the pokemon. Can be None if there is no status"
    )

    ACTIVE: bool = Field(..., description="Whether the pokemon is active or not")
    STATS: Dict[PokeStat, int] = Field(
        ...,
        description="A dictionary of stat->values for each stat of this pokemon (before modifiers)",
    )
    MOVES: List[DexMove.ValueType] = Field(
        ..., description="The list of moves this pokemon knows, without pp information"
    )
    BASE_ABILITY: DexAbility.ValueType = Field(
        ...,
        description="The base ability of this pokemon, ignoring any ability switching shenanigans",
    )
    ABILITY: Optional[DexAbility.ValueType] = Field(
        ...,
        description="The current ability of this pokemon. Only used in certain gens, can be None",
    )
    ITEM: Optional[DexItem.ValueType] = Field(
        None, description="The held item of this pokemon. None if no item is held"
    )
    POKEBALL: str = Field(..., description="Which pokeball this pokemon is contained in")

    COMMANDING: Optional[bool] = Field(
        None, description="Tatsugiri commander mechanic. True if active, false if not, None if older gen"
    )
    # TODO: Verify the REVIVING field mechanic
    REVIVING: Optional[bool] = Field(None, description="Revival Blessing flag (I think?)")

    TERATYPE: Optional[DexType.ValueType] = Field(None, description="The type that this pokemon can teratype into")

    TERASTALLIZED: Optional[DexType.ValueType] = Field(
        None, description="The type that this pokemon is teratyped into. None if not applicable"
    )


class MoveData(BaseModel):
    """A helper class to contain details about a move held in the active data for a request.

    Attributes:
        NAME: The friendly name of the move
        ID: The id of the move
        CUR_PP: The integer amount of times this move can still be used. None if Trapped
        MAX_PP: The integer amount of times this move can ever be used. None if Trapped
        TARGET: The targetting type of this move. None if Trapped
        DISABLED: Whether this move is disabled or not. None if Trapped
    """

    NAME: str = Field(..., description="The friendly name of the move")
    ID: DexMove.ValueType = Field(..., description="The id of the move")

    CUR_PP: Optional[int] = Field(
        None, description="The integer amount of times this move can still be used. None if Trapped"
    )
    MAX_PP: Optional[int] = Field(
        None, description="The integer amount of times this move can ever be used. None if Trapped"
    )

    TARGET: Optional[str] = Field(None, description="The targetting type of this move. None if Trapped")
    DISABLED: Optional[bool] = Field(None, description="Whether this move is disabled or not. None if Trapped")


class ActiveOption(BaseModel):
    """A helper class to contain details about all moves available for an active pokemon in a request.

    Attributes:
        MOVES: A list of available moves for this slot
        CAN_MEGA: Whether the pokemon can mega evolve
        CAN_ZMOVE: Whether the pokemon can zmove
        CAN_DYNA: Whether the pokemon can dynamax
        CAN_TERA: Whether the pokemon can teratype
        TRAPPED: Whether the user is trapped
    """

    MOVES: List[MoveData] = Field(..., description="A list of available moves for this slot")

    CAN_MEGA: bool = Field(False, description="Whether the pokemon can mega evolve")
    CAN_ZMOVE: bool = Field(False, description="Whether the pokemon can zmove")
    CAN_DYNA: bool = Field(False, description="Whether the pokemon can dynamax")
    CAN_TERA: bool = Field(None, description="Whether the pokemon can teratype")

    TRAPPED: bool = Field(False, description="Whether the user is trapped")


class BattleMessage_request(BattleMessage):
    """Message communicating options the user has in an upcoming choice.

    Attributes:
        REQUEST_TYPE: Which type of request this request is between TEAMPREVIEW, ACTIVE, and FORCESWITCH
        USERNAME: The player's username
        PLAYER: The player id of this player
        RQID: The id number of this request, for the purpose of an undo function
        POKEMON: The pokemon details for each pokemon in this player's side
        ACTIVE_OPTIONS: A list of actions available for each active pokemon. Will be None if switch/teampreview
        FORCESWITCH_SLOTS: A list of bool for each slot whether they are being forced to switch

    Note: Use Case(s)
        - To inform the user about their team so that a team-order decision can be made.
        - To inform the user about their available moves/switches so that a standard decision can be made.
        - To request the user to switch out a Pokemon due to a forced operation (fainted/forced out).
        - To inform the user that their opponent is making a decision and that the user has to wait for them.

    Info: Message Format(s)
        - |request|REQUEST_JSON

    Example: Input Example(s)
        - See logs for examples, there are a lot of variations.

    Tips:
        This does not necessarily mean it is time for the user to *respond* to a choice, as teampreview and move
        requests are sent *before* the details of the previous turn are sent, and thus you should wait until it is the
        correct time to send your decision.

        For FORCESWITCH requests, however, a decision should be sent once you receive this message.
    """

    REQUEST_TYPE: Literal["TEAMPREVIEW", "ACTIVE", "FORCESWITCH", "WAIT"] = Field(
        ...,
        description="Which type of request this request is between TEAMPREVIEW, ACTIVE, and FORCESWITCH",
    )

    USERNAME: str = Field(..., description="The player's username")
    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")
    RQID: Optional[int] = Field(
        None,
        description="The id number of this request, for the purpose of an undo function",
    )
    POKEMON: List[RequestPoke] = Field(..., description="The pokemon details for each pokemon in this player's side")

    ACTIVE_OPTIONS: Optional[List[ActiveOption]] = Field(
        ...,
        description="A list of actions available for each active pokemon. Will be None if switch/teampreview",
    )

    FORCESWITCH_SLOTS: Optional[List[bool]] = Field(
        None, description="A list of bool for each slot whether they are being forced to switch"
    )

    def from_message(battle_message: str) -> "BattleMessage_request":
        """Create a specific BattleMessage object from a raw message."""
        request = json.loads(battle_message.split("|")[2])

        if request.get("teamPreview", False):
            request_type = "TEAMPREVIEW"
        elif request.get("forceSwitch") is not None:
            request_type = "FORCESWITCH"
        elif len(request.get("active", [])) > 0:
            request_type = "ACTIVE"
        else:
            request_type = "WAIT"

        if request_type == "ACTIVE":
            # Process the active options
            active_options = []

            for ao_data in request.get("active", []):
                moves = []
                for m_data in ao_data.get("moves", []):
                    m = MoveData(
                        NAME=m_data["move"],
                        ID=cast2dex(m_data["id"], DexMove),
                        CUR_PP=m_data.get("pp"),
                        MAX_PP=m_data.get("maxpp"),
                        TARGET=m_data.get("target"),
                        DISABLED=isinstance(m_data.get("disabled"), str) or m_data.get("disabled"),
                    )
                    moves.append(m)

                ao = ActiveOption(
                    MOVES=moves,
                    CAN_MEGA=ao_data.get("canMegaEvo", False),
                    CAN_ZMOVE=len(ao_data.get("canZMove", [])) > 0,
                    CAN_DYNA=ao_data.get("canDynamax", False),
                    CAN_TERA=ao_data.get("canTerastallize", "") != "",
                    TRAPPED=ao_data.get("trapped", False),
                )
                active_options.append(ao)
        else:
            active_options = None

        pokemon = []

        for p_data in request["side"]["pokemon"]:
            details = p_data["details"].split(",")

            species = details[0].strip()
            species = cast2dex(species, DexPokemon)

            level = 100
            gender = None
            shiny = False
            tera = None

            if len(details) > 1:
                for detail in details[1:]:
                    detail = detail.strip()
                    if "tera" in detail:
                        tera = detail.split(":")[1].strip()
                    elif "shiny" in detail:
                        shiny = True
                    elif "L" in detail:
                        level = int(detail[1:])
                    elif "M" in detail:
                        gender = "M"
                    elif "F" in detail:
                        gender = "F"

            condition = p_data["condition"]

            hp_part = condition.split(" ")[0]

            if "/" in hp_part:
                cur_hp = int(hp_part.split("/")[0])
                max_hp = int(hp_part.split("/")[1])
            else:
                cur_hp = int(hp_part)
                max_hp = None

            if len(condition.split(" ")) > 1:
                status = condition.split(" ")[1]
            else:
                status = None

            p = RequestPoke(
                IDENT=PokemonIdentifier.from_string(p_data["ident"]),
                SPECIES=species,
                LEVEL=level,
                GENDER=gender,
                SHINY=shiny,
                TERA=cast2dex(tera, DexType),
                CUR_HP=cur_hp,
                MAX_HP=max_hp,
                STATUS=cast2dex(status, DexStatus),
                ACTIVE=p_data.get("active"),
                STATS=p_data.get("stats"),
                MOVES=[cast2dex(m, DexMove) for m in p_data.get("moves")],
                BASE_ABILITY=cast2dex(p_data.get("baseAbility"), DexAbility),
                ABILITY=cast2dex(p_data.get("ability"), DexAbility),
                ITEM=cast2dex(p_data.get("item"), DexItem),
                POKEBALL=p_data.get("pokeball"),
                COMMANDING=p_data.get("commanding"),
                REVIVING=p_data.get("reviving"),
                TERATYPE=cast2dex(p_data.get("teraType"), DexType),
                TERASTALLIZED=cast2dex(p_data.get("terastallized"), DexType),
            )

            pokemon.append(p)

        return BattleMessage_request(
            BMTYPE=BMType.request,
            BATTLE_MESSAGE=battle_message,
            USERNAME=request["side"]["name"],
            PLAYER=request["side"]["id"],
            RQID=request.get("rqig", None),
            ACTIVE_OPTIONS=active_options,
            POKEMON=pokemon,
            REQUEST_TYPE=request_type,
            FORCESWITCH_SLOTS=request.get("forceSwitch"),
        )


class BattleMessage_inactive(BattleMessage):
    """Message communicating that the inactivity timer has been set.

    Attributes:
        MESSAGE: A message related to the battle timer notification

    Note: Use Case(s)
        - To signal that there is a time-limit for descisions to be made.

    Info: Message Format(s)
        - |inactive|MESSAGE

    Example: Input Example(s)
        - TODO
    """

    MESSAGE: str = Field(..., description="A message related to the battle timer notification")

    def from_message(battle_message: str) -> "BattleMessage_inactive":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_inactive(
            BMTYPE=BMType.inactive,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_inactiveoff(BattleMessage):
    """Message communicating that the inactivity timer has been turned off.

    Attributes:
        MESSAGE: A message related to the battle timer notification

    Note: Use Case(s)
        - To signal that there is no longer a time-limit for descisions to be made.

    Info: Message Format(s)
        - |inactiveoff|MESSAGE

    Example: Input Example(s)
        - TODO
    """

    MESSAGE: str = Field(..., description="A message related to the battle timer notification")

    def from_message(battle_message: str) -> "BattleMessage_inactiveoff":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_inactiveoff(
            BMTYPE=BMType.inactiveoff,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_upkeep(BattleMessage):
    """Message communicating upkeep notice.

    Note: Use Case(s)
        - To signal that the upkeep stage has happened

    Info: Message Format(s)
        - |upkeep

    Example: Input Example(s)
        - |upkeep
    """

    def from_message(battle_message: str) -> "BattleMessage_upkeep":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_upkeep(
            BMTYPE=BMType.upkeep,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_turn(BattleMessage):
    """Message communicating that a turn has begun, and that move choices should be made.

    Attributes:
        NUMBER: The current turn number

    Note: Use Case(s)
        - To signal to the players to make a move.

    Info: Message Format(s)
        - |turn|NUMBER

    Example: Input Example(s)
        - |turn|2
    """

    NUMBER: int = Field(..., description="The current turn number")

    def from_message(battle_message: str) -> "BattleMessage_turn":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_turn(
            BMTYPE=BMType.turn,
            BATTLE_MESSAGE=battle_message,
            NUMBER=bm_split[2],
        )


class BattleMessage_win(BattleMessage):
    """Message communicating that a player has won the battle.

    Attributes:
        USERNAME: The username of the winning player

    Note: Use Case(s)
        - To signal which player has won.

    Info: Message Format(s)
        - |win|USER

    Example: Input Example(s)
        - |win|colress-gpt-test2
    """

    USERNAME: str = Field(..., description="The username of the winning player")

    def from_message(battle_message: str) -> "BattleMessage_win":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_win(
            BMTYPE=BMType.win,
            BATTLE_MESSAGE=battle_message,
            USERNAME=bm_split[2],
        )


class BattleMessage_tie(BattleMessage):
    """Message communicating that *neither* player has won the battle.

    Note: Use Case(s)
        - To signal the battle has ended in a tie

    Info: Message Format(s)
        - |tie

    Example: Input Example(s)
        - |tie
    """

    def from_message(battle_message: str) -> "BattleMessage_tie":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_tie(
            BMTYPE=BMType.tie,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_expire(BattleMessage):
    """Message communicating that the battle has ended due to mutual inactivity.

    Note: Use Case(s)
        - To signal the battle has ended due to mutual inactivity

    Info: Message Format(s)
        - |expire|

    Example: Input Example(s)
        - |expire|
    """

    def from_message(battle_message: str) -> "BattleMessage_expire":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_expire(
            BMTYPE=BMType.expire,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_t(BattleMessage):
    """Message communicating the current timestamp.

    Attributes:
        TIMESTAMP: The time of this turn as a datetime (conv from unix seconds)

    Note: Use Case(s)
        - Gives current timestamp of this set of messages

    Info: Message Format(s)
        - |t:|TIMESTAMP

    Example: Input Example(s)
        - |t:|1696832299
    """

    TIMESTAMP: datetime = Field(..., description="The time of this turn as a datetime (conv from unix seconds)")

    def from_message(battle_message: str) -> "BattleMessage_t":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_t(BMTYPE=BMType.t, BATTLE_MESSAGE=battle_message, TIMESTAMP=int(bm_split[2]))


class BattleMessage_move(BattleMessage):
    """Message communicating that a pokemon successfully used a move.

    Attributes:
        POKEMON: The pokemon using the move
        MOVE: The name of the move used
        TARGET: The primary target of this move. This can be None when applicable
        EFFECT: An optional effect that the move is taken from (Magic bounce, Sleep Talk, etc)

    Note: Use Case(s)
        - Communicating which move was used, including source/target information.

    Info: Message Format(s)
        - |move|POKEMON|MOVE|TARGET
        - |move|POKEMON|MOVE|TARGET|[from]
        - TODO: Add more

    Example: Input Example(s)
        - |move|p1a: Sceptile|Acrobatics|p2a: Espeon
        - |move|p1a: Kangaskhan|Fake Out||[still]
        - TODO: Add more
    """

    # TODO: Add an animation target field based on the [still]/[spread] information.

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon using the move")
    MOVE: str = Field(..., description="The name of the move used")

    TARGET: Optional[PokemonIdentifier] = Field(
        ...,
        description="The primary target of this move. This can be None when applicable",
    )

    EFFECT: Optional[Effect] = Field(
        None, description="An optional effect that the move is taken from (Magic bounce, Sleep Talk, etc)"
    )

    def from_message(battle_message: str) -> "BattleMessage_move":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        user = PokemonIdentifier.from_string(bm_split[2])
        move = bm_split[3]

        target = bm_split[4]

        if target == "null" or "[still]" in target or target == "":
            target = None
        else:
            target = PokemonIdentifier.from_string(target)

        if "[from]" in battle_message:
            for bm_part in bm_split:
                if "[from]" in bm_part:
                    break

            if ":" in bm_part:
                # For whatever reason there is no space between [from] and ability/item/move in this message :<
                eff_type = bm_part.split(":")[0].split("]")[1]
                eff_name = " ".join(bm_part.split(" ")[1:])
            else:
                eff_type = "move"
                eff_name = bm_part.split("]")[1]

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type)
        else:
            eff = None

        return BattleMessage_move(
            BMTYPE=BMType.move, BATTLE_MESSAGE=battle_message, POKEMON=user, MOVE=move, TARGET=target, EFFECT=eff
        )


class BattleMessage_switch(BattleMessage):
    """Message communicating that a pokemon has switched in.

    Attributes:
        POKEMON: The pokemon swapping in, potentially replacing the slot
        SPECIES: The species for this pokemon, including forme
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the string type of the new type. Else None.
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status

    Note: Use Case(s)
        - Communicating which pokemon switched in, as well as info about the pokemon.

    Info: Message Format(s)
        - |switch|POKEMON|DETAILS|HP STATUS

    Example: Input Example(s)
        - |switch|p2a: Toxicroak|Toxicroak, L81, F|100/100
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon swapping in, potentially replacing the slot")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[str] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
    )

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: int = Field(None, description="The maximum HP of the pokemon")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    def from_message(battle_message: str) -> "BattleMessage_switch":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        details = bm_split[3].split(",")

        species = details[0].strip()
        level = 100
        gender = None
        shiny = False
        tera = None

        if len(details) > 1:
            for detail in details[1:]:
                detail = detail.strip()
                if "tera" in detail:
                    tera = detail.split(":")[1].strip()
                elif "shiny" in detail:
                    shiny = True
                elif "L" in detail:
                    level = int(detail[1:])
                elif "M" in detail:
                    gender = "M"
                elif "F" in detail:
                    gender = "F"

        condition = bm_split[4]

        hp_part = condition.split(" ")[0]

        if "/" in hp_part:
            cur_hp = int(hp_part.split("/")[0])
            max_hp = int(hp_part.split("/")[1])
        else:
            cur_hp = int(hp_part)
            max_hp = None

        if len(condition.split(" ")) > 1:
            status = condition.split(" ")[1]
        else:
            status = None

        return BattleMessage_switch(
            BMTYPE=BMType.switch,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            SPECIES=cast2dex(species, DexPokemon),
            LEVEL=level,
            GENDER=gender,
            SHINY=shiny,
            TERA=tera,
            CUR_HP=cur_hp,
            MAX_HP=max_hp,
            STATUS=status,
        )


class BattleMessage_drag(BattleMessage):
    """Message communicating that a pokemon has switched in.

    Attributes:
        POKEMON: The pokemon being dragged in
        SPECIES: The species for this pokemon, including forme
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the string type of the new type. Else None.
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status

    Note: Use Case(s)
        - Communicating which pokemon was dragged in, as well as info about the pokemon.

    Info: Message Format(s)
        - |drag|POKEMON|DETAILS|HP STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon being dragged in")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[str] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
    )

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: int = Field(None, description="The maximum HP of the pokemon")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    def from_message(battle_message: str) -> "BattleMessage_drag":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        details = bm_split[3].split(",")

        species = details[0].strip()
        level = 100
        gender = None
        shiny = False
        tera = None

        if len(details) > 1:
            for detail in details[1:]:
                detail = detail.strip()
                if "tera" in detail:
                    tera = detail.split(":")[1].strip()
                elif "shiny" in detail:
                    shiny = True
                elif "L" in detail:
                    level = int(detail[1:])
                elif "M" in detail:
                    gender = "M"
                elif "F" in detail:
                    gender = "F"

        condition = bm_split[4]

        hp_part = condition.split(" ")[0]

        if "/" in hp_part:
            cur_hp = int(hp_part.split("/")[0])
            max_hp = int(hp_part.split("/")[1])
        else:
            cur_hp = int(hp_part)
            max_hp = None

        if len(condition.split(" ")) > 1:
            status = condition.split(" ")[1]
        else:
            status = None

        return BattleMessage_drag(
            BMTYPE=BMType.drag,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            SPECIES=cast2dex(species, DexPokemon),
            LEVEL=level,
            GENDER=gender,
            SHINY=shiny,
            TERA=tera,
            CUR_HP=cur_hp,
            MAX_HP=max_hp,
            STATUS=status,
        )


class BattleMessage_detailschange(BattleMessage):
    """Message communicating that a pokemon has changed formes in a permanent way.

    Attributes:
        POKEMON: The pokemon changing formes
        SPECIES: The species for this pokemon, including forme
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the string type of the new type. Else None.
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status

    Note: Use Case(s)
        - Communicating that a certain pokemon changed forme.

    Info: Message Format(s)
        - |detailschange|POKEMON|DETAILS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon changing formes")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[str] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
    )

    def from_message(battle_message: str) -> "BattleMessage_detailschange":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        details = bm_split[3].split(",")

        species = details[0].strip()
        level = 100
        gender = None
        shiny = False
        tera = None

        if len(details) > 1:
            for detail in details[1:]:
                detail = detail.strip()
                if "tera" in detail:
                    tera = detail.split(":")[1].strip()
                elif "shiny" in detail:
                    shiny = True
                elif "L" in detail:
                    level = int(detail[1:])
                elif "M" in detail:
                    gender = "M"
                elif "F" in detail:
                    gender = "F"

        return BattleMessage_detailschange(
            BMTYPE=BMType.detailschange,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            SPECIES=cast2dex(species, DexPokemon),
            LEVEL=level,
            GENDER=gender,
            SHINY=shiny,
            TERA=tera,
        )


class BattleMessage_replace(BattleMessage):
    """Message communicating that a pokemon has been replaced (Zoroark illusion ability).

    Attributes:
        POKEMON: The pokemon being revealed (Zoroark)
        SPECIES: The species for this pokemon, including forme
        LEVEL: The level of this pokemon
        GENDER: The gender of this pokemon
        SHINY: Whether the pokemon is shiny or not
        TERA: If this pokemon is teratyped, the string type of the new type. Else None.
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status

    Note: Use Case(s)
        - Communicating that a certain pokemon has been replaced.

    Info: Message Format(s)
        - |replace|POKEMON|DETAILS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon being revealed (Zoroark)")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[str] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
    )

    def from_message(battle_message: str) -> "BattleMessage_replace":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        details = bm_split[3].split(",")

        species = details[0].strip()
        level = 100
        gender = None
        shiny = False
        tera = None

        if len(details) > 1:
            for detail in details[1:]:
                detail = detail.strip()
                if "tera" in detail:
                    tera = detail.split(":")[1].strip()
                elif "shiny" in detail:
                    shiny = True
                elif "L" in detail:
                    level = int(detail[1:])
                elif "M" in detail:
                    gender = "M"
                elif "F" in detail:
                    gender = "F"

        return BattleMessage_replace(
            BMTYPE=BMType.replace,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            SPECIES=cast2dex(species, DexPokemon),
            LEVEL=level,
            GENDER=gender,
            SHINY=shiny,
            TERA=tera,
        )


class BattleMessage_swap(BattleMessage):
    """Message communicating that a certain active slot has had its pokemon swapped with another.

    Attributes:
        POKEMON: The pokemon being swapped `before` swapping
        POSITION: The slot that this Pokemon is being swapped to, as an integer
        EFFECT: An optional effect explaining what caused the swapping

    Note: Use Case(s)
        - Communicating that two pokemon have swapped active slots.

    Info: Message Format(s)
        - |swap|POKEMON|POSITION
        - |swap|POKEMON|POSITION|[from]

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon being swapped `before` swapping")
    POSITION: int = Field(
        ...,
        description="The slot that this Pokemon is being swapped to, as an integer",
        ge=0,
        le=2,
    )

    EFFECT: Optional[Effect] = Field(None, description="An optional effect explaining what caused the swapping")

    def from_message(battle_message: str) -> "BattleMessage_swap":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        pos = int(bm_split[3].strip())

        if "[from]" in battle_message:
            from_str = bm_split[4].strip()

            eff_type = from_str.split(" ")[1][:-1]
            eff_name = " ".join(from_str.split(" ")[2:])

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[5].split(" ")[1:]))
            else:
                eff_source = None

            eff = Effect(EFFECT_TYPE=eff_type, EFFECT_NAME=eff_name, EFFECT_SOURCE=eff_source)
        else:
            eff = None

        return BattleMessage_swap(
            BMTYPE=BMType.swap, BATTLE_MESSAGE=battle_message, POKEMON=poke, POSITION=pos, EFFECT=eff
        )


class BattleMessage_cant(BattleMessage):
    """Message communicating that a pokemon was unable to do something.

    Attributes:
        POKEMON: The pokemon that was unable to act
        REASON: The reason that the pokemon was unable to do what it was trying to do
        MOVE: The move being used that was unable to be used. None if not applicable

    Note: Use Case(s)
        - Communicating that a pokemon failed to do something, with the reason it failed.

    Info: Message Format(s)
        - |cant|POKEMON|REASON|MOVE

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon that was unable to act")
    # TODO: Validate possible reasons replacing with Literal/Enum
    REASON: str = Field(
        ...,
        description="The reason that the pokemon was unable to do what it was trying to do",
    )
    MOVE: Optional[str] = Field(
        ...,
        description="The move being used that was unable to be used. None if not applicable",
    )

    def from_message(battle_message: str) -> "BattleMessage_cant":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        reason = bm_split[3].strip()
        move = None if len(bm_split) <= 4 else bm_split[4].strip()

        return BattleMessage_cant(
            BMTYPE=BMType.cant,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            REASON=reason,
            MOVE=move,
        )


class BattleMessage_faint(BattleMessage):
    """Message communicating that a pokemon has fainted.

    Attributes:
        POKEMON: The pokemon that fainted

    Note: Use Case(s)
        - Communicating that a pokemon fainted.

    Info: Message Format(s)
        - |faint|POKEMON

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon fainting")

    def from_message(battle_message: str) -> "BattleMessage_faint":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_faint(BMTYPE=BMType.faint, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_fail(BattleMessage):
    """Message communicating that a pokemon has failed to do something.

    Attributes:
        POKEMON: The pokemon that failed to do something
        EFFECT: The effect causing/explaining the fail. Is Optional since sometimes it fails with no explanation

    Note: Use Case(s)
        - Communicating that a pokemon failed to do something
        - Communicate what effect caused the failure
        - Communicate if a status caused the failure.

    Info: Message Format(s)
        - |-fail|POKEMON
        - |-fail|POKEMON|EFFECT
        - |-fail|POKEMON|STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    EFFECT: Optional[Effect] = Field(
        ...,
        description="The effect causing/explaining the fail. Is Optional since sometimes it fails with no explanation",
    )

    def from_message(battle_message: str) -> "BattleMessage_fail":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        if len(bm_split) > 3:
            # In this case there is more details than just a Pokemon, so we can build and return an Effect
            if "[from]" in battle_message:
                # In this case, our main effect is whatever is detailed in the [from] string,
                # while anything in bm_split[3] is a secondary effect
                sec_effect = bm_split[3]

                for from_str in bm_split:
                    if "[from]" in from_str:
                        break

                # It seems things can fail due to weather that doesn't get a `weather:`` for some reason
                if ":" not in from_str:
                    eff_type = "weather"
                    eff_name = " ".join(from_str.split(" ")[1:])
                else:
                    eff_type = from_str.split(" ")[1][:-1]
                    eff_name = " ".join(from_str.split(" ")[2:])

                if "[of]" in battle_message:
                    for of_str in bm_split:
                        if "[of]" in of_str:
                            break

                    eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                else:
                    eff_source = None

            elif bm_split[3] == bm_split[3].lower():
                # In this case we either have a status or a volatile condition as the reason

                if len(bm_split[3]) == 3:
                    eff_type = "status"
                else:
                    eff_type = "volatile"

                eff_name = bm_split[3]
                eff_source = None
                sec_effect = None

            else:
                # In this case, our primary effect is bm_split[3] with potentially any details that come later
                # (like [weak] for substitute) added as secondary
                eff_type = "move"
                eff_source = None

                if "move:" in bm_split[3]:
                    eff_name = " ".join(bm_split[3].split(" ")[1:])
                else:
                    eff_name = bm_split[3]

                if len(bm_split) > 4:
                    sec_effect = bm_split[4]
                else:
                    sec_effect = None

            eff = Effect(
                EFFECT_NAME=eff_name, EFFECT_SOURCE=eff_source, EFFECT_TYPE=eff_type, SEC_EFFECT_NAME=sec_effect
            )

        else:
            eff = None

        return BattleMessage_fail(BMTYPE=BMType.fail, BATTLE_MESSAGE=battle_message, POKEMON=poke, EFFECT=eff)


class BattleMessage_block(BattleMessage):
    """Message communicating that a pokemon has blocked an opposing action.

    Attributes:
        POKEMON: The pokemon that was targeted but blocked something
        EFFECT: The reason this was able to be blocked

    Note: Use Case(s)
        - Communicating that a pokemon was able to block some other action.

    Info: Message Format(s)
        - |-block|POKEMON|EFFECT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(
        ...,
        description="The pokemon that was targeted but blocked something",
    )

    EFFECT: Effect = Field(..., description="The reason this was able to be blocked")

    def from_message(battle_message: str) -> "BattleMessage_block":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        eff_type = bm_split[3].split(" ")[0][:-1]
        eff_name = " ".join(bm_split[3].split(" ")[1:])

        if "[of]" in battle_message:
            eff_source = PokemonIdentifier.from_string(" ".join(bm_split[4].split(" ")[1:]))
        else:
            eff_source = None

        eff = Effect(EFFECT_TYPE=eff_type, EFFECT_NAME=eff_name, EFFECT_SOURCE=eff_source)

        return BattleMessage_block(BMTYPE=BMType.block, BATTLE_MESSAGE=battle_message, POKEMON=poke, EFFECT=eff)


class BattleMessage_notarget(BattleMessage):
    """Message communicating that no target was available at move-use time.

    Attributes:
        POKEMON: The pokemon that had no target available

    Note: Use Case(s)
        - Communicating that a pokemon had no target available.

    Info: Message Format(s)
        - |-notarget|POKEMON

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon that has no target")

    def from_message(battle_message: str) -> "BattleMessage_notarget":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_notarget(
            BMTYPE=BMType.notarget,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_miss(BattleMessage):
    """Message communicating that a given source pokemon missed its action.

    Attributes:
        SOURCE: The pokemon missing the attack
        TARGET: The pokemon evading (If applicable, can be None)

    Note: Use Case(s)
        - Communicating that a pokemon missed.
        - Communicating which pokemon was targeted but avoided the action.

    Info: Message Format(s)
        - |-miss|SOURCE
        - |-miss|SOURCE|TARGET

    Example: Input Example(s)
        - TODO
    """

    SOURCE: PokemonIdentifier = Field(..., description="The pokemon missing the attack")

    TARGET: Optional[PokemonIdentifier] = Field(None, description="The pokemon evading (If applicable, can be None)")

    def from_message(battle_message: str) -> "BattleMessage_miss":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        source = PokemonIdentifier.from_string(bm_split[2])

        if len(bm_split) > 3:
            target = PokemonIdentifier.from_string(bm_split[3])
        else:
            target = None

        return BattleMessage_miss(BMTYPE=BMType.miss, BATTLE_MESSAGE=battle_message, SOURCE=source, TARGET=target)


class BattleMessage_damage(BattleMessage):
    """Message communicating that a pokemon has taken damage.

    Attributes:
        POKEMON: The pokemon being hurt
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon. None if the pokemon is fainted
        STATUS: The status of the pokemon. Can be None if there is no status
        EFFECT: The reason this damage was dealt, if not from a move

    Note: Use Case(s)
        - Communicating that a pokemon took damage in some way.

    Info: Message Format(s)
        - |-damage|POKEMON|HP STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon being hurt")

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: Optional[int] = Field(None, description="The maximum HP of the pokemon. None if the pokemon is fainted")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    EFFECT: Optional[Effect] = Field(None, description="The reason this damage was dealt, if not from a move")

    def from_message(battle_message: str) -> "BattleMessage_damage":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        condition = bm_split[3]

        hp_part = condition.split(" ")[0]

        if "/" in hp_part:
            cur_hp = int(hp_part.split("/")[0])
            max_hp = int(hp_part.split("/")[1])
        else:
            cur_hp = int(hp_part)
            max_hp = None

        if len(condition.split(" ")) > 1:
            status = condition.split(" ")[1]
        else:
            status = None

        if len(bm_split) >= 5 and "[from]" in bm_split[4]:
            # Parse this message assuming the form |-damage|p2a: Leavanny|180/281 tox|[from] psn
            from_split = bm_split[4].split(" ")

            if ":" not in bm_split[4]:
                effect_type = None
                effect_name = " ".join(from_split[1:]).strip()
            else:
                effect_type = from_split[1].strip()[:-1]
                effect_name = " ".join(from_split[2:]).strip()

            if len(bm_split) >= 6 and "[of]" in bm_split[5]:
                source = PokemonIdentifier.from_string(bm_split[5][5:])
            else:
                source = None

            effect = Effect(EFFECT_TYPE=effect_type, EFFECT_NAME=effect_name, EFFECT_SOURCE=source)
        else:
            effect = None

        return BattleMessage_damage(
            BMTYPE=BMType.damage,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            CUR_HP=cur_hp,
            MAX_HP=max_hp,
            STATUS=status,
            EFFECT=effect,
        )


class BattleMessage_heal(BattleMessage):
    """Message communicating that a pokemon has healed some health.

    Attributes:
        POKEMON: The pokemon being healed
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status
        EFFECT: The reason this health was healed, if not from a move

    Note: Use Case(s)
        - Communicating that a pokemon healed in some way.

    Info: Message Format(s)
        - |-heal|POKEMON|HP STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(
        ..., description="The pokemon being healed. Can be slotless, so be sure to check type!"
    )

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: int = Field(None, description="The maximum HP of the pokemon")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    EFFECT: Optional[Effect] = Field(None, description="The reason this health was healed, if not from a move")

    def from_message(battle_message: str) -> "BattleMessage_heal":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        condition = bm_split[3]

        hp_part = condition.split(" ")[0]

        if "/" in hp_part:
            cur_hp = int(hp_part.split("/")[0])
            max_hp = int(hp_part.split("/")[1])
        else:
            cur_hp = int(hp_part)
            max_hp = None

        if len(condition.split(" ")) > 1:
            status = condition.split(" ")[1]
        else:
            status = None

        if len(bm_split) >= 5 and "[from]" in bm_split[4]:
            # Parse this message assuming the form |-heal|p2a: Leavanny|197/281 tox|[from] item: Leftovers
            from_split = bm_split[4].split(" ")

            if ":" not in bm_split[4]:
                effect_type = None
                effect_name = " ".join(from_split[1:]).strip()
            else:
                effect_type = from_split[1].strip()[:-1]
                effect_name = " ".join(from_split[2:]).strip()

            if len(bm_split) >= 6 and "[of]" in bm_split[5]:
                source = PokemonIdentifier.from_string(bm_split[5][5:])
            else:
                source = None

            effect = Effect(EFFECT_TYPE=effect_type, EFFECT_NAME=effect_name, EFFECT_SOURCE=source)
        else:
            effect = None

        return BattleMessage_heal(
            BMTYPE=BMType.heal,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            CUR_HP=cur_hp,
            MAX_HP=max_hp,
            STATUS=status,
            EFFECT=effect,
        )


class BattleMessage_sethp(BattleMessage):
    """Message communicating that a pokemon has an exact hp amount.

    Attributes:
        POKEMON: The pokemon getting the HP set
        CUR_HP: The current HP of the pokemon
        MAX_HP: The maximum HP of the pokemon
        STATUS: The status of the pokemon. Can be None if there is no status
        EFFECT: The reason this health was healed

    Note: Use Case(s)
        - Communicating that a pokemon had its health directly set.

    Info: Message Format(s)
        - |-sethp|POKEMON|HP STATUS|EFFECT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon getting the HP set")

    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: int = Field(None, description="The maximum HP of the pokemon")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    EFFECT: Optional[Effect] = Field(None, description="The reason this health was healed")

    def from_message(battle_message: str) -> "BattleMessage_sethp":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        condition = bm_split[3]

        hp_part = condition.split(" ")[0]

        if "/" in hp_part:
            cur_hp = int(hp_part.split("/")[0])
            max_hp = int(hp_part.split("/")[1])
        else:
            cur_hp = int(hp_part)
            max_hp = None

        if len(condition.split(" ")) > 1:
            status = condition.split(" ")[1]
        else:
            status = None

        if len(bm_split) >= 5 and "[from]" in bm_split[4]:
            # Parse this message assuming the form |-sethp|p2a: Exeggutor|94/100 par|[from] move: Pain Split|[silent]
            from_split = bm_split[4].split(" ")

            if ":" not in bm_split[4]:
                effect_type = None
                effect_name = " ".join(from_split[1:]).strip()
            else:
                effect_type = from_split[1].strip()[:-1]
                effect_name = " ".join(from_split[2:]).strip()

            if len(bm_split) >= 6 and "[of]" in bm_split[5]:
                source = PokemonIdentifier.from_string(bm_split[5][5:])
            else:
                source = None

            effect = Effect(EFFECT_TYPE=effect_type, EFFECT_NAME=effect_name, EFFECT_SOURCE=source)
        else:
            effect = None

        return BattleMessage_sethp(
            BMTYPE=BMType.sethp,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            CUR_HP=cur_hp,
            MAX_HP=max_hp,
            STATUS=status,
            EFFECT=effect,
        )


class BattleMessage_status(BattleMessage):
    """Message communicating that a pokemon has gained a status.

    Attributes:
        POKEMON: The pokemon gaining the status
        STATUS: The status being gained

    Note: Use Case(s)
        - Communicating that a pokemon has gained a status condition.

    Info: Message Format(s)
        - |-status|POKEMON|STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon gaining the status")

    STATUS: DexStatus.ValueType = Field(..., description="The status being gained")

    def from_message(battle_message: str) -> "BattleMessage_status":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        status = bm_split[3]

        return BattleMessage_status(
            BMTYPE=BMType.status, BATTLE_MESSAGE=battle_message, POKEMON=poke, STATUS=cast2dex(status, DexStatus)
        )


class BattleMessage_curestatus(BattleMessage):
    """Message communicating that a pokemon has lost a status.

    Attributes:
        POKEMON: The pokemon losing the status
        STATUS: The status being lost

    Note: Use Case(s)
        - Communicating that a pokemon has lost a status condition.

    Info: Message Format(s)
        - |-curestatus|POKEMON|STATUS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon losing the status")

    STATUS: DexStatus.ValueType = Field(..., description="The status being lost")

    def from_message(battle_message: str) -> "BattleMessage_curestatus":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        status = bm_split[3]

        return BattleMessage_curestatus(
            BMTYPE=BMType.curestatus, BATTLE_MESSAGE=battle_message, POKEMON=poke, STATUS=cast2dex(status, DexStatus)
        )


class BattleMessage_cureteam(BattleMessage):
    """Message communicating that a team has been cured of all status conditions.

    Attributes:
        EFFECT: The effect causing the team to be healed

    Note: Use Case(s)
        - Communicating that all pokemon have been cured.

    Info: Message Format(s)
        - |-cureteam|POKEMON|EFFECT

    Example: Input Example(s)
        - TODO
    """

    EFFECT: Effect = Field(..., description="The effect causing the team to be healed")

    def from_message(battle_message: str) -> "BattleMessage_cureteam":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        eff_source = PokemonIdentifier.from_string(bm_split[2])
        eff_type = bm_split[3].split(" ")[1][:-1]
        eff_name = " ".join(bm_split[3].split(" ")[2:])

        effect = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)

        return BattleMessage_cureteam(BMTYPE=BMType.cureteam, BATTLE_MESSAGE=battle_message, EFFECT=effect)


class BattleMessage_boost(BattleMessage):
    """Message communicating that a pokemon has gained some stat boost.

    Attributes:
        POKEMON: The pokemon getting the boost
        STAT: Which stat is being boosted
        AMOUNT: By how much this stat is being boosted, as an integer. Can be 0 if at cap

    Note: Use Case(s)
        - Communicating that a pokemon received a single stat boost.

    Info: Message Format(s)
        - |-boost|POKEMON|STAT|AMOUNT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(
        ...,
        description="By how much this stat is being boosted, as an integer. Can be 0 if at cap",
    )

    def from_message(battle_message: str) -> "BattleMessage_boost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        stat = bm_split[3]
        amount = bm_split[4]

        return BattleMessage_boost(
            BMTYPE=BMType.boost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            STAT=stat,
            AMOUNT=amount,
        )


class BattleMessage_unboost(BattleMessage):
    """Message communicating that a pokemon has had some stat lowered.

    Attributes:
        POKEMON: The pokemon getting the boost
        STAT: Which stat is being boosted
        AMOUNT: By how much this stat is being unboosted, as an integer. Can be 0 if at cap

    Note: Use Case(s)
        - Communicating that a pokemon received a single stat unboost.

    Info: Message Format(s)
        - |-unboost|POKEMON|STAT|AMOUNT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(
        ...,
        description="By how much this stat is being unboosted, as an integer. Can be 0 if at cap",
    )

    def from_message(battle_message: str) -> "BattleMessage_unboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        stat = bm_split[3]
        amount = bm_split[4]

        return BattleMessage_unboost(
            BMTYPE=BMType.unboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            STAT=stat,
            AMOUNT=amount,
        )


class BattleMessage_setboost(BattleMessage):
    """Message communicating that a pokemon has had some stat set to a certain boost value.

    Attributes:
        POKEMON: The pokemon getting the boost
        STAT: Which stat is being boosted
        AMOUNT: The new value being assigned for this stat boost

    Note: Use Case(s)
        - Communicating that a pokemon received a set stat boost value.

    Info: Message Format(s)
        - |-setboost|POKEMON|STAT|AMOUNT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(..., description="The new value being assigned for this stat boost")

    def from_message(battle_message: str) -> "BattleMessage_setboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        stat = bm_split[3]
        amount = bm_split[4]

        return BattleMessage_setboost(
            BMTYPE=BMType.setboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            STAT=stat,
            AMOUNT=amount,
        )


class BattleMessage_swapboost(BattleMessage):
    """Message communicating that two specific pokemon have had their stat boosts switched.

    Warning:
        Not yet implemented!

    Attributes:
        POKEMON: The pokemon getting the boost

    Note: Use Case(s)
        - Communicating that two pokemon have had their respective stat boosts swapped.

    Info: Message Format(s)
        - |-swapboost|SOURCE|TARGET|STATS

    Example: Input Example(s)
        - TODO
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_swapboost":
        """Create a specific BattleMessage object from a raw message."""
        raise NotImplementedError

        return BattleMessage_swapboost(
            BMTYPE=BMType.swapboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_invertboost(BattleMessage):
    """Message communicating that a pokemon has had its stat boosts inverted.

    Attributes:
        POKEMON: The pokemon getting the boost inverted

    Note: Use Case(s)
        - Communicating that a pokemon has had its stat boosts inverted.

    Info: Message Format(s)
        - |-invertboost|POKEMON

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to invert the boosts of")

    def from_message(battle_message: str) -> "BattleMessage_invertboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_invertboost(
            BMTYPE=BMType.invertboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_clearboost(BattleMessage):
    """Message communicating that a pokemon has had its stat boosts cleared.

    Attributes:
        POKEMON: The pokemon that had its stat boosts cleared.

    Note: Use Case(s):
        - Communicating that a pokemon has had its stat boosts cleared.

    Info: Message Format(s):
        - |-clearboost|POKEMON

    Example: Input Example(s)
        - |-clearboost|p1a: Pikachu
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the boosts of")

    def from_message(battle_message: str) -> "BattleMessage_clearboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_clearboost(
            BMTYPE=BMType.clearboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_clearallboost(BattleMessage):
    """Message communicating that all pokemon have had their stat boosts cleared.

    Note: Use Case(s):
        - Communicating that all pokemon have had their stat boosts cleared.

    Info: Message Format(s):
        - |-clearallboost

    Example: Input Example(s)
        - |-clearallboost
    """

    def from_message(battle_message: str) -> "BattleMessage_clearallboost":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_clearallboost(
            BMTYPE=BMType.clearallboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_clearpositiveboost(BattleMessage):
    """Message communicating that a pokemon has had its positive stat boosts cleared.

    Attributes:
        POKEMON: The pokemon that had its positive stat boosts cleared.
        EFFECT: The effect causing this positive boost clearance

    Note: Use Case(s):
        - Communicating that a pokemon has had its positive stat boosts cleared.

    Info: Message Format(s):
        - |-clearpositiveboost|TARGET|EFF_SOURCE|EFFECT

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the positive boosts of")

    EFFECT: Effect = Field(..., description="Details about the effect that is causing this positive boost clearance")

    def from_message(battle_message: str) -> "BattleMessage_clearpositiveboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        eff_source = PokemonIdentifier.from_string(bm_split[3])
        eff_type = bm_split[4].split(" ")[0][:-1]
        eff_name = " ".join(bm_split[4].split(" ")[1:])

        eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)

        return BattleMessage_clearpositiveboost(
            BMTYPE=BMType.clearpositiveboost, BATTLE_MESSAGE=battle_message, POKEMON=poke, EFFECT=eff
        )


class BattleMessage_clearnegativeboost(BattleMessage):
    """Message communicating that a pokemon has had its negative stat boosts cleared.

    Attributes:
        POKEMON: The pokemon that had its negative stat boosts cleared.

    Note: Use Case(s):
        - Communicating that a pokemon has had its negative stat boosts cleared.

    Info: Message Format(s):
        - |-clearnegativeboost|POKEMON

    Example: Input Example(s)
        - TODO
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the negative boosts of")

    def from_message(battle_message: str) -> "BattleMessage_clearnegativeboost":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_clearnegativeboost(
            BMTYPE=BMType.clearnegativeboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_copyboost(BattleMessage):
    """Message communicating that a pokemon has had its stat boosts copied.

    Warning:
        Not yet implemented!

    Attributes:
        POKEMON: The pokemon that had its stat boosts copied.

    Note: Use Case(s):
        - Communicating that a pokemon has had its stat boosts copied.

    Info: Message Format(s):
        - |-copyboost|SOURCE|TARGET

    Example: Input Example(s)
        - TODO
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_copyboost":
        """Create a specific BattleMessage object from a raw message."""
        raise NotImplementedError

        return BattleMessage_copyboost(
            BMTYPE=BMType.copyboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_weather(BattleMessage):
    """Message communicating that the weather has changed.

    Attributes:
        WEATHER: The weather being set

    Note: Use Case(s):
        - Communicating that the weather has changed.

    Info: Message Format(s):
        - |-weather|WEATHER|EFFECT

    Example: Input Example(s)
        - TODO
    """

    WEATHER: DexWeather.ValueType = Field(..., description="The weather being set")

    EFFECT: Optional[Effect] = Field(None, description="Optionally, the effect that caused this weather")

    def from_message(battle_message: str) -> "BattleMessage_weather":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        weather = bm_split[2]

        if ("[upkeep]" not in battle_message) and (len(bm_split) >= 4) and ("[from]" in bm_split[3]):
            from_split = bm_split[3].split(" ")

            if ":" not in bm_split[3]:
                effect_type = None
                effect_name = " ".join(from_split[1:]).strip()
            else:
                effect_type = from_split[1].strip()[:-1]
                effect_name = " ".join(from_split[2:]).strip()

            if len(bm_split) >= 5 and "[of]" in bm_split[4]:
                source = PokemonIdentifier.from_string(bm_split[4][5:])
            else:
                source = None

            effect = Effect(EFFECT_TYPE=effect_type, EFFECT_NAME=effect_name, EFFECT_SOURCE=source)
        else:
            effect = None

        return BattleMessage_weather(
            BMTYPE=BMType.weather,
            BATTLE_MESSAGE=battle_message,
            WEATHER=cast2dex(weather, DexWeather),
            EFFECT=effect,
        )


class BattleMessage_fieldstart(BattleMessage):
    """Message communicating that a field condition has started.

    Attributes:
        EFFECT: The effect starting for the field.

    Note: Use Case(s):
        - Communicating that a field condition has started.

    Info: Message Format(s):
        - |-fieldstart|CONDITION

    Example: Input Example(s)
        - TODO
    """

    EFFECT: Effect = Field(
        ...,
        description="The Effect starting for the field.",
    )

    def from_message(battle_message: str) -> "BattleMessage_fieldstart":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        eff_type = bm_split[2].split(" ")[0][:-1]
        eff_name = " ".join(bm_split[2].split(" ")[1:])

        if "[from]" in battle_message:
            # In this case we want to pull the effect name from this from to set as the sec_effect
            # TODO: Add a secondary effect type for all uses of sec_effect (why didn't I think of this earlier :<<<<)
            sec_effect_name = " ".join(bm_split[3].split(" ")[1:])

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[4].split(" ")[1:]))
            else:
                eff_source = None
        else:
            sec_effect_name = None

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[3].split(" ")[1:]))
            else:
                eff_source = None

        eff = Effect(
            EFFECT_NAME=eff_name, EFFECT_SOURCE=eff_source, EFFECT_TYPE=eff_type, SEC_EFFECT_NAME=sec_effect_name
        )

        return BattleMessage_fieldstart(BMTYPE=BMType.fieldstart, BATTLE_MESSAGE=battle_message, EFFECT=eff)


class BattleMessage_fieldend(BattleMessage):
    """
    |-fieldend|CONDITION
    """

    EFFECT: Effect = Field(
        ...,
        description="The Effect ending for the field.",
    )

    def from_message(battle_message: str) -> "BattleMessage_fieldend":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        if ":" in bm_split[2]:
            eff_type = bm_split[2].split(" ")[0][:-1]
            eff_name = " ".join(bm_split[2].split(" ")[1:])
        else:
            eff_type = "move"
            eff_name = bm_split[2]

        eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type)

        return BattleMessage_fieldend(BMTYPE=BMType.fieldend, BATTLE_MESSAGE=battle_message, EFFECT=eff)


class BattleMessage_sidestart(BattleMessage):
    """
    |-sidestart|SIDE|CONDITION
    """

    PLAYER: str = Field(..., description="The player id of the impacted player", pattern=r"p[1-4]")

    # TODO: Add validator for side conditions
    CONDITION: str = Field(..., description="The field condition starting")

    def from_message(battle_message: str) -> "BattleMessage_sidestart":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        player = bm_split[2].split(":")[0]

        if ":" in bm_split[3]:
            condition = " ".join(bm_split[3].split(" ")[1:])
        else:
            condition = bm_split[3]

        return BattleMessage_sidestart(
            BMTYPE=BMType.sidestart, BATTLE_MESSAGE=battle_message, PLAYER=player, CONDITION=condition
        )


class BattleMessage_sideend(BattleMessage):
    """
    |-sideend|SIDE|CONDITION

    |-sideend|SIDE|CONDITION|[from]

    |-sideend|SIDE|CONDITION|[of]
    """

    PLAYER: str = Field(..., description="The player id of the impacted player", pattern=r"p[1-4]")

    # TODO: Add validator for side conditions
    CONDITION: str = Field(..., description="The field condition starting")

    EFFECT: Optional[Effect] = Field(None, description="The effect that is causing the conditon to end")

    def from_message(battle_message: str) -> "BattleMessage_sideend":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        player = bm_split[2].split(":")[0]

        if ":" in bm_split[3]:
            condition = " ".join(bm_split[3].split(" ")[1:])
        else:
            condition = bm_split[3]

        if "[of]" in battle_message and "[from]" not in battle_message:
            eff_type = "volatile"
            eff_name = "existence"

            eff_source = PokemonIdentifier.from_string(" ".join(bm_split[4].split(" ")[1:]))

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)
        elif "[from]" in battle_message:
            eff_type = bm_split[4].split(" ")[1][:-1]
            eff_name = " ".join(bm_split[4].split(" ")[2:])

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[5].split(" ")[1:]))
            else:
                eff_source = None

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)
        else:
            eff = None

        return BattleMessage_sideend(
            BMTYPE=BMType.sideend, BATTLE_MESSAGE=battle_message, PLAYER=player, CONDITION=condition, EFFECT=eff
        )


class BattleMessage_swapsideconditions(BattleMessage):
    """
    |-swapsideconditions
    """

    def from_message(battle_message: str) -> "BattleMessage_swapsideconditions":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_swapsideconditions(
            BMTYPE=BMType.swapsideconditions,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_volstart(BattleMessage):
    """
    |-start|POKEMON|MOVE

    |-start|POKEMON|MOVE|MOVE

    |-start|POKEMON|VOLATILE

    |-start|POKEMON|typechange|TYPE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon this volatile effect is started for")

    EFFECT: Optional[Effect] = Field(None, description="Optionally, the effect that caused this volatile status")

    def from_message(battle_message: str) -> "BattleMessage_volstart":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        if bm_split[3] == "typechange":
            # Special case and formatting for typechange notification
            sec_effect_name = bm_split[4]

            if "[from]" in battle_message:
                from_str = bm_split[5]

                eff_type = from_str.split(" ")[1][:-1]
                eff_name = " ".join(from_str.split(" ")[2:])

                if "[of]" in battle_message:
                    of_str = bm_split[6]
                    eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                else:
                    eff_source = None
            else:
                eff_type = "volatile"
                eff_name = "typechange"
                eff_source = None

        elif bm_split[3] == bm_split[3].lower():
            # TODO: Replace with better volatile checking if needed

            if "[from]" in battle_message:
                sec_effect_name = bm_split[3]

                for from_str in bm_split:
                    if "[from]" in from_str:
                        break

                eff_type = from_str.split(" ")[1][:-1]
                eff_name = " ".join(from_str.split(" ")[2:])

                if "[of]" in battle_message:
                    for of_str in bm_split:
                        if "[of]" in of_str:
                            break

                    eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                else:
                    eff_source = None
            else:
                eff_name = bm_split[3]
                eff_type = "volatile"
                sec_effect_name = None
                eff_source = None
        elif ":" in bm_split[3]:
            # This means that the move here in bm_split[3] is being used ON the POKEMON, not BY
            # This also means there is not secondary effect of this one, since we didn't see [from]
            eff_type = bm_split[3].split(":")[0]
            eff_name = " ".join(bm_split[3].split(" ")[1:])
            sec_effect_name = None

            if "[of]" in battle_message:
                for of_str in bm_split:
                    if "[of]" in of_str:
                        break

                eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
            else:
                eff_source = None
        else:
            # Theres a couple of options from here. It could either be:
            #   A - |-start|POKEMON|MOVE
            #   B - |-start|POKEMON|MOVE|MOVE
            #   C - |-start|POKEMON|MOVE|[from] OR |-start|POKEMON|MOVE|[from]|[of]
            #   D - |-start|POKEMON|MOVE|MOVE|[from] OR |-start|POKEMON|MOVE|MOVE|[from]|[of]
            # Double moves are for things like disable or mimic. In these cases, the first move is the disable/mimic/etc
            # while the second move is the thing `being` disabled/mimic'd/etc
            move1 = bm_split[3]

            if len(bm_split) < 5:
                # Process case A here
                eff_type = "move"
                eff_name = move1
                sec_effect_name = None
                eff_source = None
            elif "[from]" not in battle_message:
                # Process cases B here
                eff_type = "move"
                eff_name = move1
                sec_effect_name = bm_split[4]
                eff_source = None
            else:
                if "[from]" in bm_split[4]:
                    # Process case C here
                    eff_type = bm_split[4].split(" ")[1][:-1]
                    eff_name = " ".join(bm_split[4].split(" ")[1:])
                    sec_effect_name = move1

                    if "[of]" in battle_message:
                        for of_str in bm_split:
                            if "[of]" in of_str:
                                break

                        eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                    else:
                        eff_source = None
                else:
                    # Process case D here
                    move1 = bm_split[4]

                    eff_type = bm_split[5].split(" ")[1][:-1]
                    eff_name = " ".join(bm_split[5].split(" ")[1:])
                    sec_effect_name = move1

                    if "[of]" in battle_message:
                        for of_str in bm_split:
                            if "[of]" in of_str:
                                break

                        eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                    else:
                        eff_source = None

        eff = Effect(
            EFFECT_TYPE=eff_type,
            EFFECT_NAME=eff_name,
            SEC_EFFECT_NAME=sec_effect_name,
            EFFECT_SOURCE=eff_source,
        )

        return BattleMessage_volstart(
            BMTYPE=BMType.volstart,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            EFFECT=eff,
        )


class BattleMessage_volend(BattleMessage):
    """
    |-end|POKEMON|EFFECT
    """

    POKEMON: PokemonIdentifier = Field(
        ..., description="The pokemon whose volatile status is ending. Can be slotless in some cases."
    )

    EFFECT: Effect = Field(..., description="The effect that is ending for the pokemon")

    SILENT: bool = Field(..., description="Whether this message is silent or not")

    def from_message(battle_message: str) -> "BattleMessage_volend":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        silent = "[silent]" in battle_message

        if bm_split[3] == bm_split[3].lower():
            # TODO: Replace with better volatile checking if needed

            if "[from]" in battle_message:
                sec_effect_name = bm_split[3]

                for from_str in bm_split:
                    if "[from]" in from_str:
                        break

                eff_type = from_str.split(" ")[1][:-1]
                eff_name = " ".join(from_str.split(" ")[2:])

                if "[of]" in battle_message:
                    for of_str in bm_split:
                        if "[of]" in of_str:
                            break

                    eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                else:
                    eff_source = None
            else:
                eff_name = bm_split[3]
                eff_type = "volatile"
                sec_effect_name = None
                eff_source = None
        elif ":" in bm_split[3]:
            # This means that the move here in bm_split[3] was being used ON the POKEMON, not BY
            # This also means there is not secondary effect of this one, since we didn't see [from]
            eff_type = bm_split[3].split(":")[0]
            eff_name = " ".join(bm_split[3].split(" ")[1:])
            sec_effect_name = None

            if "[of]" in battle_message:
                for of_str in bm_split:
                    if "[of]" in of_str:
                        break

                eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
            else:
                eff_source = None
        else:
            # Theres a couple of options from here. It could either be:
            # A - |-end|POKEMON|MOVE
            # B - |-end|POKEMON|MOVE|[DETAIL]
            # C - |-end|POKEMON|MOVE|[from] OR |-end|POKEMON|MOVE|[from]|[of]
            # We will assign MOVE to EFFECT_NAME unless there is a from, in which case it will become the secondary
            # If there is not a [from] but instead a [DETAIL], MOVE will be the EFFECT_NAME instead
            move = bm_split[3]

            if len(bm_split) < 5:
                # Process case A here
                eff_type = "move"
                eff_name = move
                sec_effect_name = None
                eff_source = None
            elif "[from]" not in battle_message:
                # Process cases B here
                eff_type = "move"
                eff_name = move
                sec_effect_name = bm_split[4]
                eff_source = None
            else:
                eff_type = bm_split[4].split(" ")[1][:-1]
                eff_name = " ".join(bm_split[4].split(" ")[1:])
                sec_effect_name = move

                if "[of]" in battle_message:
                    for of_str in bm_split:
                        if "[of]" in of_str:
                            break

                    eff_source = PokemonIdentifier.from_string(" ".join(of_str.split(" ")[1:]))
                else:
                    eff_source = None

        eff = Effect(
            EFFECT_TYPE=eff_type,
            EFFECT_NAME=eff_name,
            SEC_EFFECT_NAME=sec_effect_name,
            EFFECT_SOURCE=eff_source,
        )

        return BattleMessage_volend(
            BMTYPE=BMType.volend, BATTLE_MESSAGE=battle_message, POKEMON=poke, SILENT=silent, EFFECT=eff
        )


class BattleMessage_crit(BattleMessage):
    """
    |-crit|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_crit":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_crit(
            BMTYPE=BMType.crit,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_supereffective(BattleMessage):
    """
    |-supereffective|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_supereffective":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_supereffective(
            BMTYPE=BMType.supereffective,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_resisted(BattleMessage):
    """
    |-resisted|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_resisted":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_resisted(
            BMTYPE=BMType.resisted,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_immune(BattleMessage):
    """
    |-immune|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_immune":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_immune(
            BMTYPE=BMType.immune,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_item(BattleMessage):
    """
    |-item|POKEMON|ITEM|[from]EFFECT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon whose item is revealed")

    ITEM: str = Field(..., description="The item being revealed")

    EFFECT: Optional[Effect] = Field(
        None, description="The effect that revealed the item, if applicable. Not used when auto-revealed (air balloon)"
    )

    def from_message(battle_message: str) -> "BattleMessage_item":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        item = bm_split[3]

        if len(bm_split) > 4:
            # This means there is at least a [from] clause and possibly also a [of] clause

            from_str = bm_split[4]

            eff_type = from_str.split(" ")[1][:-1]
            eff_name = " ".join(from_str.split(" ")[2:])

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[5].split(" ")[1:]))
            else:
                eff_source = None

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)
        else:
            eff = None

        return BattleMessage_item(
            BMTYPE=BMType.item, BATTLE_MESSAGE=battle_message, POKEMON=poke, ITEM=item, EFFECT=eff
        )


class BattleMessage_enditem(BattleMessage):
    """
    |-enditem|POKEMON|ITEM|[from]EFFECT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon whose item is destroyed")

    ITEM: str = Field(..., description="The item being destroyed")

    EFFECT: Optional[Effect] = Field(
        None,
        description="The effect that destroyed the item, if applicable.",
    )

    def from_message(battle_message: str) -> "BattleMessage_enditem":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        item = bm_split[3]

        # We do some quick filtering on the bm_split to get rid of any single detail things like [silent] or [eat]
        bm_split = [bm for bm in bm_split if len(bm.strip()) > 0 and bm.strip()[0] != "[" and bm.strip()[-1] != "]"]

        if len(bm_split) > 4:
            # This means there is at least a [from] clause and possibly also a [of] clause
            # However, enditem uses weird |[from] ATTRIBUTE|[move] MOVE or |[from] ATTRIBUTE syntax sometimes

            if ":" in bm_split[4] and "[from]" in bm_split[4]:
                # this implies that bm_split[4] is a standard syntax from statement, which we can process as normal
                from_str = bm_split[4]

                eff_type = from_str.split(" ")[1][:-1]
                eff_name = " ".join(from_str.split(" ")[2:])

                if "[of]" in battle_message:
                    eff_source = PokemonIdentifier.from_string(" ".join(bm_split[5].split(" ")[1:]))
                else:
                    eff_source = None

                eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)
            elif "[from]" in bm_split[4] and len(bm_split) > 5:
                # This implies the weird split formatting syntax mentioned above
                # EX: |-enditem|p2a: Ditto|Sitrus Berry|[from] stealeat|[move] Bug Bite|[of] p1a: Ariados
                # For our purposes, we will set stealeat as the sec_effect, Bug Bite as eff_name, move as eff_type, and
                # p1a: Ariados as eff_source

                sec_effect = " ".join(bm_split[4].split(" ")[1:])
                eff_type = bm_split[5].split(" ")[0][1:-1]
                eff_name = " ".join(bm_split[5].split(" ")[1:])

                if "[of]" in battle_message:
                    eff_source = PokemonIdentifier.from_string(" ".join(bm_split[6].split(" ")[1:]))
                else:
                    eff_source = None

                eff = Effect(
                    EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source, SEC_EFFECT_NAME=sec_effect
                )
            else:
                eff = None
        else:
            eff = None

        return BattleMessage_enditem(
            BMTYPE=BMType.enditem, BATTLE_MESSAGE=battle_message, POKEMON=poke, ITEM=item, EFFECT=eff
        )


class BattleMessage_ability(BattleMessage):
    """
    |-ability|POKEMON|ABILITY|[from] EFFECT|[of] POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon whose ability is being shown")

    ABILITY: DexAbility.ValueType = Field(..., description="The ability being revealed")

    EFFECT: Optional[Effect] = Field(
        None, description="If an effect caused this to be revealed, this will contain details"
    )

    def from_message(battle_message: str) -> "BattleMessage_ability":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        ability = bm_split[3]

        if len(bm_split) >= 5 and "[from]" in bm_split[4]:
            # Parse this message assuming the form:
            #  |-ability|p1a: Gardevoir|Swarm|[from] ability: Trace|[of] p2a: Leavanny
            from_split = bm_split[4].split(" ")

            if len(from_split) == 2:
                effect_type = None
                effect_name = from_split[1].strip()
            else:
                effect_type = from_split[1].strip()[:-1]
                effect_name = from_split[2].strip()

            if len(bm_split) >= 6 and "[of]" in bm_split:
                source = PokemonIdentifier.from_string(bm_split[5][5:])
            else:
                source = None

            effect = Effect(EFFECT_TYPE=effect_type, EFFECT_NAME=effect_name, EFFECT_SOURCE=source)
        else:
            effect = None

        return BattleMessage_ability(
            BMTYPE=BMType.ability,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            ABILITY=cast2dex(ability, DexAbility),
            EFFECT=effect,
        )


class BattleMessage_endability(BattleMessage):
    """
    |-endability|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon whose ability is being suppressed")

    def from_message(battle_message: str) -> "BattleMessage_endability":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_endability(BMTYPE=BMType.endability, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_transform(BattleMessage):
    """
    |-transform|SOURCE|TARGET|

    |-transform|SOURCE|TARGET|[from]
    """

    SOURCE: PokemonIdentifier = Field(..., description="The pokemon transforming")
    TARGET: PokemonIdentifier = Field(..., description="The pokemon it's transforming into")

    EFFECT: Optional[Effect] = Field(..., description="The optional effect explaining the transformation")

    def from_message(battle_message: str) -> "BattleMessage_transform":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        source = PokemonIdentifier.from_string(bm_split[2])
        target = PokemonIdentifier.from_string(bm_split[3])

        if "[from]" in battle_message:
            eff_type = bm_split[4].split(" ")[1][:-1]
            eff_name = " ".join(bm_split[4].split(" ")[2:])

            if "[of]" in battle_message:
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[5].split(" ")[1:]))
            else:
                eff_source = None

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)

        else:
            eff = None

        return BattleMessage_transform(
            BMTYPE=BMType.transform, BATTLE_MESSAGE=battle_message, SOURCE=source, TARGET=target, EFFECT=eff
        )


class BattleMessage_mega(BattleMessage):
    """
    |-mega|POKEMON|MEGASTONE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_mega":
        """Create a specific BattleMessage object from a raw message."""
        raise NotImplementedError

        return BattleMessage_mega(
            BMTYPE=BMType.mega,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_primal(BattleMessage):
    """
    |-primal|POKEMON|ITEM
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon going primal")
    ITEM: str = Field(..., description="The held item that is being used")

    def from_message(battle_message: str) -> "BattleMessage_primal":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        item = bm_split[3]

        return BattleMessage_primal(BMTYPE=BMType.primal, BATTLE_MESSAGE=battle_message, POKEMON=poke, ITEM=item)


class BattleMessage_burst(BattleMessage):
    """
    |-burst|POKEMON|SPECIES|ITEM
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_burst":
        """Create a specific BattleMessage object from a raw message."""
        raise NotImplementedError

        return BattleMessage_burst(
            BMTYPE=BMType.burst,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_zpower(BattleMessage):
    """
    |-zpower|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon using the Z Move")

    def from_message(battle_message: str) -> "BattleMessage_zpower":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_zpower(BMTYPE=BMType.zpower, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_zbroken(BattleMessage):
    """
    |-zbroken|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon whose Z move is over")

    def from_message(battle_message: str) -> "BattleMessage_zbroken":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_zbroken(BMTYPE=BMType.zbroken, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_activate(BattleMessage):
    """
    |-activate|POKEMON|EFFECT

    |-activate|POKEMON|VOLATILE
    |-activate|POKEMON|MOVE|EFFECT
    |-activate|POKEMON|ABILITY|EFFECT
    |-activate|POKEMON|ITEM|EFFECT

    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon the effect is about")

    EFFECT: Effect = Field(..., description="The effect detailed in this activation")

    def from_message(battle_message: str) -> "BattleMessage_activate":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        if bm_split[3].lower() == bm_split[3]:
            # This means this is a volatile status (like confusion)
            eff = Effect(EFFECT_TYPE="volatile", EFFECT_NAME=bm_split[3])
        else:
            if ":" not in bm_split[3]:
                # This means it's a move, though this branch is only for older formats
                eff_type = "move"
                eff_name = bm_split[3]
            else:
                # This means that an effect cause is described here
                eff_type = bm_split[3].split(" ")[0][:-1]
                eff_name = " ".join(bm_split[3].split(" ")[1:])

            if len(bm_split) > 4 and "[of]" in bm_split[4]:
                # process the source poke information, the break because "[of]" is a last block only message
                eff_source = PokemonIdentifier.from_string(" ".join(bm_split[4].split(" ")[1:]))
                sec_effect_name = None
            elif len(bm_split) > 4 and ("[damage]" in bm_split[4] or "[consumed]" in bm_split[4]):
                # These are redundant as we'll see messages elsewhere with more helpful info
                # At least this tells us there is no "[of]" part so it saves us even needing to look :/
                sec_effect_name = None
                eff_source = None
            elif len(bm_split) > 4:
                # This means theres a secondary part to the effect, such as a move being mimic'd or an ability being
                # overwritten with Mummy
                # In general, EFFECT_NAME should be the `more` relevant thing. So if you're activating the ability Mummy
                # and losing Battle Armorthen we would have Mummy be the EFFECT_NAME and SEC_EFFECT_NAME is
                # Battle Armor. This is because we know for sure what category the primary EFFECT_NAME belongs to as
                # it is told to us directly, but theoretically the secondary could be any type and we are not informed
                # Lastly, if you're reading this, you have my deepest apologies, we're in this mess together at least!
                sec_effect_name = bm_split[4]

                if "[of]" in battle_message:
                    for bm_part in bm_split:
                        if "[of]" in bm_part:
                            eff_source = PokemonIdentifier.from_string(" ".join(bm_part.split(" ")[1:]))
                            break
                else:
                    eff_source = None
            else:
                # No other information here, so we just create the effect and return
                sec_effect_name = None
                eff_source = None

            eff = Effect(
                EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source, SEC_EFFECT_NAME=sec_effect_name
            )

        return BattleMessage_activate(BMTYPE=BMType.activate, BATTLE_MESSAGE=battle_message, POKEMON=poke, EFFECT=eff)


class BattleMessage_hint(BattleMessage):
    """
    |-hint|MESSAGE
    """

    MESSAGE: str = Field(..., description="The message sent to you as a hint")

    def from_message(battle_message: str) -> "BattleMessage_hint":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_hint(BMTYPE=BMType.hint, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_center(BattleMessage):
    """
    |-center
    """

    def from_message(battle_message: str) -> "BattleMessage_center":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_center(
            BMTYPE=BMType.center,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_message(BattleMessage):
    """
    |-message|MESSAGE
    """

    MESSAGE: str = Field(..., description="The message sent as part of this notification")

    def from_message(battle_message: str) -> "BattleMessage_message":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_message(BMTYPE=BMType.message, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_combine(BattleMessage):
    """
    |-combine
    """

    def from_message(battle_message: str) -> "BattleMessage_combine":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_combine(
            BMTYPE=BMType.combine,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_waiting(BattleMessage):
    """
    |-waiting|SOURCE|TARGET
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_waiting":
        """Create a specific BattleMessage object from a raw message."""
        raise NotImplementedError

        return BattleMessage_waiting(
            BMTYPE=BMType.waiting,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_prepare(BattleMessage):
    """
    |-prepare|POKEMON|MOVE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon preparing the move")

    MOVE: str = Field(..., description="The move being prepared")

    def from_message(battle_message: str) -> "BattleMessage_prepare":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        move = bm_split[3]

        return BattleMessage_prepare(BMTYPE=BMType.prepare, BATTLE_MESSAGE=battle_message, POKEMON=poke, MOVE=move)


class BattleMessage_mustrecharge(BattleMessage):
    """
    |-mustrecharge|POKEMON
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_mustrecharge":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_mustrecharge(
            BMTYPE=BMType.mustrecharge,
            BATTLE_MESSAGE=battle_message,
            POKEMON=bm_split[2],
        )


class BattleMessage_nothing(BattleMessage):
    """
    |-nothing
    """

    def from_message(battle_message: str) -> "BattleMessage_nothing":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_nothing(
            BMTYPE=BMType.nothing,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_hitcount(BattleMessage):
    """
    |-hitcount|POKEMON|NUM
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon being hit multiple times. Can be slotless")
    NUM: int = Field(..., description="The number of hits as an integer")

    def from_message(battle_message: str) -> "BattleMessage_hitcount":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        num = bm_split[3]

        return BattleMessage_hitcount(BMTYPE=BMType.hitcount, BATTLE_MESSAGE=battle_message, POKEMON=poke, NUM=num)


class BattleMessage_singlemove(BattleMessage):
    """
    |-singlemove|POKEMON|MOVE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon using this single move")

    MOVE: DexMove.ValueType = Field(..., description="The move being used")

    def from_message(battle_message: str) -> "BattleMessage_singlemove":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        move = bm_split[3]

        return BattleMessage_singlemove(
            BMTYPE=BMType.singlemove, BATTLE_MESSAGE=battle_message, POKEMON=poke, MOVE=cast2dex(move, DexMove)
        )


class BattleMessage_singleturn(BattleMessage):
    """
    |-singleturn|POKEMON|MOVE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon using this single move")

    MOVE: DexMove.ValueType = Field(..., description="The move being used")

    def from_message(battle_message: str) -> "BattleMessage_singleturn":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        move = bm_split[3]

        if ":" in move:
            move = move.split(":")[-1].strip()

        return BattleMessage_singleturn(
            BMTYPE=BMType.singleturn, BATTLE_MESSAGE=battle_message, POKEMON=poke, MOVE=cast2dex(move, DexMove)
        )


class BattleMessage_formechange(BattleMessage):
    """
    |-formechange|POKEMON|SPECIES
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon swapping in, replacing the slot")

    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")

    EFFECT: Optional[Effect] = Field(None, description="Optionally, what caused the formechange")

    def from_message(battle_message: str) -> "BattleMessage_formechange":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        species = bm_split[3].strip()

        if "[from]" in battle_message:
            from_str = bm_split[-1]

            eff_type = from_str.split(" ")[1][:-1]
            eff_name = " ".join(from_str.split(" ")[2:])

            eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type)
        else:
            eff = None

        return BattleMessage_formechange(
            BMTYPE=BMType.formechange,
            BATTLE_MESSAGE=battle_message,
            POKEMON=poke,
            SPECIES=cast2dex(species, DexPokemon),
            EFFECT=eff,
        )


class BattleMessage_terastallize(BattleMessage):
    """
    |terastallize|POKEMON|TYPE
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon doing the terastallization")

    TYPE: DexType.ValueType = Field()

    def from_message(battle_message: str) -> "BattleMessage_terastallize":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        tera_type = cast2dex(bm_split[3], DexType)

        return BattleMessage_terastallize(
            BMTYPE=BMType.terastallize, BATTLE_MESSAGE=battle_message, POKEMON=poke, TYPE=tera_type
        )


class BattleMessage_fieldactivate(BattleMessage):
    """
    |-fieldactivate|EFFECT
    """

    EFFECT: Effect = Field(..., description="The effect causing the field activation")

    def from_message(battle_message: str) -> "BattleMessage_fieldactivate":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        eff_type = bm_split[2].split(" ")[0][:-1]
        eff_name = " ".join(bm_split[2].split(" ")[1:])

        eff = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type)

        return BattleMessage_fieldactivate(BMTYPE=BMType.fieldactivate, BATTLE_MESSAGE=battle_message, EFFECT=eff)


class BattleMessage_error(BattleMessage):
    """
    |error|MESSAGE
    """

    MESSAGE: str = Field(..., description="The error message sent by showdown")

    def from_message(battle_message: str) -> "BattleMessage_error":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_error(BMTYPE=BMType.error, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_bigerror(BattleMessage):
    """
    |bigerror|MESSAGE
    """

    MESSAGE: str = Field(..., description="The error message sent by showdown")

    def from_message(battle_message: str) -> "BattleMessage_bigerror":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_bigerror(BMTYPE=BMType.bigerror, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_init(BattleMessage):
    """
    |init|battle
    """

    def from_message(battle_message: str) -> "BattleMessage_init":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_init(BMTYPE=BMType.init, BATTLE_MESSAGE=battle_message)


class BattleMessage_deinit(BattleMessage):
    """
    |deinit
    """

    def from_message(battle_message: str) -> "BattleMessage_deinit":
        """Create a specific BattleMessage object from a raw message."""
        return BattleMessage_deinit(BMTYPE=BMType.deinit, BATTLE_MESSAGE=battle_message)


class BattleMessage_title(BattleMessage):
    """
    |title|TITLE
    """

    TITLE: str = Field(..., description="The title of this match as shown on pokemon showdown")

    def from_message(battle_message: str) -> "BattleMessage_title":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_title(BMTYPE=BMType.title, BATTLE_MESSAGE=battle_message, TITLE=bm_split[2])


class BattleMessage_join(BattleMessage):
    """
    |join|USERNAME
    """

    USERNAME: str = Field(..., description="The username of the joining player")

    def from_message(battle_message: str) -> "BattleMessage_join":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_join(BMTYPE=BMType.join, BATTLE_MESSAGE=battle_message, USERNAME=bm_split[2])


class BattleMessage_leave(BattleMessage):
    """
    |leave|USERNAME
    """

    USERNAME: str = Field(..., description="The username of the leaving player")

    def from_message(battle_message: str) -> "BattleMessage_leave":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_leave(BMTYPE=BMType.leave, BATTLE_MESSAGE=battle_message, USERNAME=bm_split[2])


class BattleMessage_raw(BattleMessage):
    """
    |raw|MESSAGE
    """

    MESSAGE: str = Field(..., description="The raw message from Showdown. Typically used for rating changes.")

    def from_message(battle_message: str) -> "BattleMessage_raw":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        return BattleMessage_raw(BMTYPE=BMType.raw, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_anim(BattleMessage):
    """
    |-anim|SOURCE|MOVE|TARGET|[notarget]OR[blank]
    """

    SOURCE: PokemonIdentifier = Field(..., description="The pokemon using the move")
    TARGET: PokemonIdentifier = Field(
        ...,
        description="The pokemon being targeted by the move. If there is no target then this will instead be slotless",
    )

    MOVE: DexMove.ValueType = Field(..., description="The move being used")

    NO_TARGET: bool = Field(False, description="Whether the move is labeled as notarget or not")

    def from_message(battle_message: str) -> "BattleMessage_anim":
        """Create a specific BattleMessage object from a raw message."""
        bm_split = battle_message.split("|")

        source = PokemonIdentifier.from_string(bm_split[2])
        move = bm_split[3]

        if len(bm_split) > 5 and bm_split[5] == "[notarget]":
            no_target = True
            target = PokemonIdentifier.from_slot_string(bm_split[4])
        else:
            no_target = False
            target = PokemonIdentifier.from_string(bm_split[4])

        return BattleMessage_anim(
            BMTYPE=BMType.anim,
            BATTLE_MESSAGE=battle_message,
            SOURCE=source,
            TARGET=target,
            MOVE=cast2dex(move, DexMove),
            NO_TARGET=no_target,
        )


bmtype_to_bmclass: Dict[BMType, Type["BattleMessage"]] = {
    BMType.player: BattleMessage_player,
    BMType.teamsize: BattleMessage_teamsize,
    BMType.gametype: BattleMessage_gametype,
    BMType.gen: BattleMessage_gen,
    BMType.tier: BattleMessage_tier,
    BMType.rated: BattleMessage_rated,
    BMType.rule: BattleMessage_rule,
    BMType.clearpoke: BattleMessage_clearpoke,
    BMType.poke: BattleMessage_poke,
    BMType.start: BattleMessage_start,
    BMType.teampreview: BattleMessage_teampreview,
    BMType.empty: BattleMessage_empty,
    BMType.request: BattleMessage_request,
    BMType.inactive: BattleMessage_inactive,
    BMType.inactiveoff: BattleMessage_inactiveoff,
    BMType.upkeep: BattleMessage_upkeep,
    BMType.turn: BattleMessage_turn,
    BMType.win: BattleMessage_win,
    BMType.tie: BattleMessage_tie,
    BMType.expire: BattleMessage_expire,
    BMType.t: BattleMessage_t,
    BMType.move: BattleMessage_move,
    BMType.switch: BattleMessage_switch,
    BMType.drag: BattleMessage_drag,
    BMType.detailschange: BattleMessage_detailschange,
    BMType.replace: BattleMessage_replace,
    BMType.swap: BattleMessage_swap,
    BMType.cant: BattleMessage_cant,
    BMType.faint: BattleMessage_faint,
    BMType.fail: BattleMessage_fail,
    BMType.block: BattleMessage_block,
    BMType.notarget: BattleMessage_notarget,
    BMType.miss: BattleMessage_miss,
    BMType.damage: BattleMessage_damage,
    BMType.heal: BattleMessage_heal,
    BMType.sethp: BattleMessage_sethp,
    BMType.status: BattleMessage_status,
    BMType.curestatus: BattleMessage_curestatus,
    BMType.cureteam: BattleMessage_cureteam,
    BMType.boost: BattleMessage_boost,
    BMType.unboost: BattleMessage_unboost,
    BMType.setboost: BattleMessage_setboost,
    BMType.swapboost: BattleMessage_swapboost,
    BMType.invertboost: BattleMessage_invertboost,
    BMType.clearboost: BattleMessage_clearboost,
    BMType.clearallboost: BattleMessage_clearallboost,
    BMType.clearpositiveboost: BattleMessage_clearpositiveboost,
    BMType.clearnegativeboost: BattleMessage_clearnegativeboost,
    BMType.copyboost: BattleMessage_copyboost,
    BMType.weather: BattleMessage_weather,
    BMType.fieldstart: BattleMessage_fieldstart,
    BMType.fieldend: BattleMessage_fieldend,
    BMType.sidestart: BattleMessage_sidestart,
    BMType.sideend: BattleMessage_sideend,
    BMType.swapsideconditions: BattleMessage_swapsideconditions,
    BMType.volstart: BattleMessage_volstart,
    BMType.volend: BattleMessage_volend,
    BMType.crit: BattleMessage_crit,
    BMType.supereffective: BattleMessage_supereffective,
    BMType.resisted: BattleMessage_resisted,
    BMType.immune: BattleMessage_immune,
    BMType.item: BattleMessage_item,
    BMType.enditem: BattleMessage_enditem,
    BMType.ability: BattleMessage_ability,
    BMType.endability: BattleMessage_endability,
    BMType.transform: BattleMessage_transform,
    BMType.mega: BattleMessage_mega,
    BMType.primal: BattleMessage_primal,
    BMType.burst: BattleMessage_burst,
    BMType.zpower: BattleMessage_zpower,
    BMType.zbroken: BattleMessage_zbroken,
    BMType.activate: BattleMessage_activate,
    BMType.hint: BattleMessage_hint,
    BMType.center: BattleMessage_center,
    BMType.message: BattleMessage_message,
    BMType.mess: BattleMessage_message,
    BMType.combine: BattleMessage_combine,
    BMType.waiting: BattleMessage_waiting,
    BMType.prepare: BattleMessage_prepare,
    BMType.mustrecharge: BattleMessage_mustrecharge,
    BMType.nothing: BattleMessage_nothing,
    BMType.hitcount: BattleMessage_hitcount,
    BMType.singlemove: BattleMessage_singlemove,
    BMType.singleturn: BattleMessage_singleturn,
    BMType.formechange: BattleMessage_formechange,
    BMType.terastallize: BattleMessage_terastallize,
    BMType.fieldactivate: BattleMessage_fieldactivate,
    BMType.error: BattleMessage_error,
    BMType.bigerror: BattleMessage_bigerror,
    BMType.init: BattleMessage_init,
    BMType.deinit: BattleMessage_deinit,
    BMType.title: BattleMessage_title,
    BMType.j: BattleMessage_join,
    BMType.J: BattleMessage_join,
    BMType.join: BattleMessage_join,
    BMType.l: BattleMessage_leave,
    BMType.leave: BattleMessage_leave,
    BMType.L: BattleMessage_leave,
    BMType.raw: BattleMessage_raw,
    BMType.anim: BattleMessage_anim,
}
