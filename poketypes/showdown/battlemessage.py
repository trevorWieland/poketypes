from __future__ import annotations

import json
from datetime import datetime
from enum import Enum, unique
from typing import Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel, Field

from ..dex import (
    DexAbility,
    DexCondition,
    DexGen,
    DexItem,
    DexMove,
    DexPokemon,
    DexStat,
    DexStatus,
    DexType,
    DexWeather,
    cast2dex,
)


@unique
class BMType(str, Enum):
    """
    See https://github.com/smogon/pokemon-showdown/blob/master/sim/SIM-PROTOCOL.md for the full list of battle message types
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
    l = "l"
    L = "L"
    leave = "leave"
    raw = "raw"
    anim = "-anim"

    # Internal error case
    unknown = "unknown"


class PokeStat(str, Enum):
    attack = "atk"
    defence = "def"
    special_attack = "spa"
    special_defence = "spd"
    speed = "spe"

    hp = "hp"

    evasion = "evasion"
    accuracy = "accuracy"


class PokemonIdentifier(BaseModel):
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
        return PokemonIdentifier(IDENTITY=ident.split(":")[1].strip().upper(), PLAYER=ident.split(":")[0])

    @staticmethod
    def from_slot_string(slot: str) -> "PokemonIdentifier":
        return PokemonIdentifier(
            IDENTITY=slot.split(":")[1].strip().upper(), PLAYER=slot[:2].split(":")[0], SLOT=slot[2]
        )

    @staticmethod
    def from_string(string: str) -> "PokemonIdentifier":
        if len(string.split(":")[0]) == 3:
            return PokemonIdentifier(
                IDENTITY=string.split(":")[1].strip().upper(), PLAYER=string[:2].split(":")[0], SLOT=string[2]
            )
        else:
            return PokemonIdentifier(IDENTITY=string.split(":")[1].strip().upper(), PLAYER=string.split(":")[0])


class EffectType(str, Enum):
    ability = "ability"
    item = "item"
    move = "move"
    status = "status"
    weather = "weather"
    condition = "condition"
    volatile = "volatile"
    pokemon = "pokemon"


class Effect(BaseModel):
    """
    A helper class for many Battle Message types that rely on something happening due to an
    ability / item / weather / status / etc
    """

    EFFECT_TYPE: Optional[EffectType] = Field(None, description="The category of effect causing this.")

    # TODO: Add a validator for EFFECT_NAME
    EFFECT_NAME: str = Field(..., description="The name of the effect")

    # TODO: Add a validator for secondary effect name
    SEC_EFFECT_NAME: Optional[str] = Field(
        None,
        description="Any extra ability/item/move/status/weather/condition/volatile that is being impacted by this effect. Recommended to use something else if you can",
    )

    EFFECT_SOURCE: Optional[PokemonIdentifier] = Field(
        None, description="If the effect is being caused by another different pokemon, then this will be that pokemon"
    )


class BattleMessage(BaseModel):
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
        """
        Creates a specific BattleMessage object from a raw message.

        For example, given a message '|faint|p2a: Umbreon', this will create a new BattleMessage_faint with fields extracted from the text properly

        You should use the base class `BattleMessage.from_message` directly, as this will auto-identify which kind of battle message is being sent and create that
        """

        if battle_message.strip() == "" or (
            battle_message.split("|")[1] == "request" and battle_message.split("|")[2] == ""
        ):
            return BattleMessage(BMTYPE=BMType.empty, BATTLE_MESSAGE="")

        try:
            bmtype = BMType(battle_message.split("|")[1])
            bm_class = bmtype_to_bmclass[bmtype]
        except ValueError as e:
            print(
                f"Failed to identify which BMType we should use for battle message key {battle_message.split('|')[1]}. This is probably an error!"
            )
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="UNKNOWN_BMTYPE")

            return bm
        except KeyError as e:
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
        except Exception as e:
            print(f"BMType {bmtype} failed to build from message {battle_message} due to a(n) {type(e)}: {e}")
            print()

            bm = BattleMessage(BMTYPE="unknown", BATTLE_MESSAGE=battle_message, ERR_STATE="PARSE_ERROR")

        return bm


class BattleMessage_player(BattleMessage):
    """
    |player|PLAYER|USERNAME|AVATAR|RATING
    """

    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")
    USERNAME: str = Field(..., description="The username of the player")
    AVATAR: Union[int, str] = Field(..., description="Either a number id of the user's avatar or a custom value")
    RATING: Optional[int] = Field(None, description="The elo of the player in the current format, if applicable")

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_player":
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
    """
    |teamsize|PLAYER|NUMBER
    """

    PLAYER: str = Field(..., description="The player id of this player", pattern=r"p[1-4]")
    NUMBER: int = Field(..., description="The number of pokemon your opponent has.")

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_teamsize":
        bm_split = battle_message.split("|")

        return BattleMessage_teamsize(
            BMTYPE=BMType.teamsize,
            BATTLE_MESSAGE=battle_message,
            PLAYER=bm_split[2],
            NUMBER=bm_split[3],
        )


class BattleMessage_gametype(BattleMessage):
    """
    |gametype|GAMETYPE
    """

    GAMETYPE: Literal["singles", "doubles", "triples", "multi", "freeforall"] = Field(
        ..., description="The gametype of this format"
    )

    @staticmethod
    def from_message(battle_message: str) -> "BattleMessage_gametype":
        bm_split = battle_message.split("|")

        return BattleMessage_gametype(
            BMTYPE=BMType.gametype,
            BATTLE_MESSAGE=battle_message,
            GAMETYPE=bm_split[2],
        )


class BattleMessage_gen(BattleMessage):
    """
    |gen|GENNUM
    """

    GENNUM: DexGen.ValueType = Field(..., description="The integer generation number of this format")

    def from_message(battle_message: str) -> "BattleMessage_gen":
        bm_split = battle_message.split("|")

        return BattleMessage_gen(
            BMTYPE=BMType.gen,
            BATTLE_MESSAGE=battle_message,
            GENNUM=bm_split[2],
        )


class BattleMessage_tier(BattleMessage):
    """
    |tier|FORMATNAME
    """

    FORMATNAME: str = Field(..., description="The game format of this match")

    def from_message(battle_message: str) -> "BattleMessage_tier":
        bm_split = battle_message.split("|")

        return BattleMessage_tier(
            BMTYPE=BMType.tier,
            BATTLE_MESSAGE=battle_message,
            FORMATNAME=bm_split[2],
        )


class BattleMessage_rated(BattleMessage):
    """
    |rated|MESSAGE
    """

    MESSAGE: Optional[str] = Field(None, description="An optional message used in tournaments")

    def from_message(battle_message: str) -> "BattleMessage_rated":
        bm_split = battle_message.split("|")

        return BattleMessage_rated(
            BMTYPE=BMType.rated,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_rule(BattleMessage):
    """
    |rule|RULE: DESCRIPTION
    """

    RULE: str = Field(..., description="The name of the rule")
    DESCRIPTION: str = Field(..., description="A description of this rule")

    def from_message(battle_message: str) -> "BattleMessage_rule":
        bm_split = battle_message.split("|")

        return BattleMessage_rule(
            BMTYPE=BMType.rule,
            BATTLE_MESSAGE=battle_message,
            RULE=bm_split[2].split(":")[0],
            DESCRIPTION=":".join(bm_split[2].split(":")[1:]).strip(),
        )


class BattleMessage_clearpoke(BattleMessage):
    """
    |clearpoke
    """

    def from_message(battle_message: str) -> "BattleMessage_clearpoke":
        return BattleMessage_clearpoke(
            BMTYPE=BMType.clearpoke,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_poke(BattleMessage):
    """
    |poke|PLAYER|DETAILS|ITEM
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
    """
    |start
    """

    def from_message(battle_message: str) -> "BattleMessage_start":
        return BattleMessage_start(
            BMTYPE=BMType.start,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_teampreview(BattleMessage):
    """
    |teampreview
    """

    def from_message(battle_message: str) -> "BattleMessage_teampreview":
        return BattleMessage_teampreview(
            BMTYPE=BMType.teampreview,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_empty(BattleMessage):
    """
    |
    """

    def from_message(battle_message: str) -> "BattleMessage_empty":
        return BattleMessage_empty(
            BMTYPE=BMType.empty,
            BATTLE_MESSAGE=battle_message,
        )


class RequestPoke(BaseModel):
    """
    A helper class to contain details about a pokemon held in the `side` data of a request.
    """

    IDENT: PokemonIdentifier = Field(..., description="The string pokemon identifier (without slot information)")

    # Details
    SPECIES: DexPokemon.ValueType = Field(..., description="The species for this pokemon, including forme")
    LEVEL: int = Field(100, description="The level of this pokemon")
    GENDER: Optional[Literal["M", "F"]] = Field(None, description="The gender of this pokemon")
    SHINY: bool = Field(False, description="Whether the pokemon is shiny or not")
    TERA: Optional[DexType.ValueType] = Field(
        None,
        description="If this pokemon is teratyped, the string type of the new type. Else None.",
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
    """
    A helper class to contain details about a move held in the active data for a request
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
    """
    A helper class to contain details about all moves available for an active pokemon in a request
    """

    MOVES: List[MoveData] = Field(..., description="A list of available moves for this slot")

    CAN_MEGA: bool = Field(False, description="Whether the pokemon can mega evolve")
    CAN_ZMOVE: bool = Field(False, description="Whether the pokemon can zmove")
    CAN_DYNA: bool = Field(False, description="Whether the pokemon can dynamax")
    CAN_TERA: bool = Field(None, description="Whether the pokemon can teratype")

    TRAPPED: bool = Field(False, description="Whether the user is trapped")


class BattleMessage_request(BattleMessage):
    """
    |request|REQUEST
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
    """
    |inactive|MESSAGE
    """

    MESSAGE: str = Field(..., description="A message related to the battle timer notification")

    def from_message(battle_message: str) -> "BattleMessage_inactive":
        bm_split = battle_message.split("|")

        return BattleMessage_inactive(
            BMTYPE=BMType.inactive,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_inactiveoff(BattleMessage):
    """
    |inactiveoff|MESSAGE
    """

    MESSAGE: str = Field(..., description="A message related to the battle timer notification")

    def from_message(battle_message: str) -> "BattleMessage_inactiveoff":
        bm_split = battle_message.split("|")

        return BattleMessage_inactiveoff(
            BMTYPE=BMType.inactiveoff,
            BATTLE_MESSAGE=battle_message,
            MESSAGE=bm_split[2],
        )


class BattleMessage_upkeep(BattleMessage):
    """
    |upkeep
    """

    def from_message(battle_message: str) -> "BattleMessage_upkeep":
        return BattleMessage_upkeep(
            BMTYPE=BMType.upkeep,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_turn(BattleMessage):
    """
    |turn|NUMBER
    """

    NUMBER: int = Field(..., description="The current turn number")

    def from_message(battle_message: str) -> "BattleMessage_turn":
        bm_split = battle_message.split("|")

        return BattleMessage_turn(
            BMTYPE=BMType.turn,
            BATTLE_MESSAGE=battle_message,
            NUMBER=bm_split[2],
        )


class BattleMessage_win(BattleMessage):
    """
    |win|USER
    """

    USERNAME: str = Field(..., description="The username of the winning player")

    def from_message(battle_message: str) -> "BattleMessage_win":
        bm_split = battle_message.split("|")

        return BattleMessage_win(
            BMTYPE=BMType.win,
            BATTLE_MESSAGE=battle_message,
            USERNAME=bm_split[2],
        )


class BattleMessage_tie(BattleMessage):
    """
    |tie
    """

    def from_message(battle_message: str) -> "BattleMessage_tie":
        return BattleMessage_tie(
            BMTYPE=BMType.tie,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_expire(BattleMessage):
    """
    |expire|
    """

    def from_message(battle_message: str) -> "BattleMessage_expire":
        return BattleMessage_expire(
            BMTYPE=BMType.expire,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_t(BattleMessage):
    """
    |t:|TIMESTAMP
    """

    TIMESTAMP: datetime = Field(..., description="The time of this turn as a datetime (conv from unix seconds)")

    def from_message(battle_message: str) -> "BattleMessage_t":
        bm_split = battle_message.split("|")

        return BattleMessage_t(BMTYPE=BMType.t, BATTLE_MESSAGE=battle_message, TIMESTAMP=int(bm_split[2]))


class BattleMessage_move(BattleMessage):
    """
    |move|POKEMON|MOVE|TARGET|[from]
    """

    # TODO: Add an animation target field based on the [still]/[spread] information. Not needed for AI but needed for animations

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon using the move")
    MOVE: str = Field(..., description="The name of the move used")

    TARGET: Optional[PokemonIdentifier] = Field(
        ...,
        description="The primary target of this move. If notarget, this will be slotless with the original target listed, or even None",
    )

    EFFECT: Optional[Effect] = Field(
        None, description="An optional effect that the move is taken from (Magic bounce, Sleep Talk, etc)"
    )

    def from_message(battle_message: str) -> "BattleMessage_move":
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
    """
    |switch|POKEMON|DETAILS|HP STATUS
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
    """
    |drag|POKEMON|DETAILS|HP STATUS
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
    """
    |detailschange|POKEMON|DETAILS
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
    """
    |replace|POKEMON|DETAILS
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
    """
    |swap|POKEMON|POSITION

    |swap|POKEMON|[from]EFFECT
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
    """
    |cant|POKEMON|REASON|MOVE
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
    """
    |faint|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon fainting")

    def from_message(battle_message: str) -> "BattleMessage_faint":
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_faint(BMTYPE=BMType.faint, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_fail(BattleMessage):
    """
    |-fail|POKEMON

    |-fail|POKEMON|EFFECT

    |-fail|POKEMON|STATUS
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon identifier relevant")

    EFFECT: Optional[Effect] = Field(
        ...,
        description="The effect causing/explaining the failure. Is Optional since sometimes it fails with no explanation",
    )

    def from_message(battle_message: str) -> "BattleMessage_fail":
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        if len(bm_split) > 3:
            # In this case there is more details than just a Pokemon, so we can build and return an Effect
            if "[from]" in battle_message:
                # In this case, our main effect is whatever is detailed in the [from] string, while anything in bm_split[3] is a secondary effect
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
                # In this case, our primary effect is bm_split[3] with potentially any details that come later (like [weak] for substitute) added as secondary
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
    """
    |-block|POKEMON|EFFECT
    """

    POKEMON: PokemonIdentifier = Field(
        ...,
        description="The pokemon that was targeted but blocked something (Doesn't have to be the reason it was blocked)",
    )

    EFFECT: Effect = Field(..., description="The reason this was able to be blocked")

    def from_message(battle_message: str) -> "BattleMessage_block":
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
    """
    |-notarget|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon that has no target")

    def from_message(battle_message: str) -> "BattleMessage_notarget":
        bm_split = battle_message.split("|")

        return BattleMessage_notarget(
            BMTYPE=BMType.notarget,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_miss(BattleMessage):
    """
    |-miss|SOURCE|TARGET

    |-miss|SOURCE
    """

    SOURCE: PokemonIdentifier = Field(..., description="The pokemon missing the attack")

    TARGET: Optional[PokemonIdentifier] = Field(None, description="The pokemon evading (If applicable, can be None)")

    def from_message(battle_message: str) -> "BattleMessage_miss":
        bm_split = battle_message.split("|")

        source = PokemonIdentifier.from_string(bm_split[2])

        if len(bm_split) > 3:
            target = PokemonIdentifier.from_string(bm_split[3])
        else:
            target = None

        return BattleMessage_miss(BMTYPE=BMType.miss, BATTLE_MESSAGE=battle_message, SOURCE=source, TARGET=target)


class BattleMessage_damage(BattleMessage):
    """
    |-damage|POKEMON|HP STATUS
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon being hurt")

    # Condition
    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: Optional[int] = Field(None, description="The maximum HP of the pokemon. None if the pokemon is fainted")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    EFFECT: Optional[Effect] = Field(None, description="The reason this damage was dealt, if not from a move")

    def from_message(battle_message: str) -> "BattleMessage_damage":
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
    """
    |-heal|POKEMON|HP STATUS
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
    """
    |-sethp|POKEMON|HP STATUS|EFFECT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon getting the HP set")

    CUR_HP: int = Field(..., description="The current HP of the pokemon")
    MAX_HP: int = Field(None, description="The maximum HP of the pokemon")
    STATUS: Optional[str] = Field(None, description="The status of the pokemon. Can be None if there is no status")

    EFFECT: Optional[Effect] = Field(None, description="The reason this health was healed, if not from a move")

    def from_message(battle_message: str) -> "BattleMessage_sethp":
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
    """
    |-status|POKEMON|STATUS
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon gaining the status")

    STATUS: DexStatus.ValueType = Field(..., description="The status being gained")

    def from_message(battle_message: str) -> "BattleMessage_status":
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        status = bm_split[3]

        return BattleMessage_status(
            BMTYPE=BMType.status, BATTLE_MESSAGE=battle_message, POKEMON=poke, STATUS=cast2dex(status, DexStatus)
        )


class BattleMessage_curestatus(BattleMessage):
    """
    |-curestatus|POKEMON|STATUS
    """

    POKEMON: PokemonIdentifier = Field(..., description="The main pokemon losing the status")

    STATUS: DexStatus.ValueType = Field(..., description="The status being lost")

    def from_message(battle_message: str) -> "BattleMessage_curestatus":
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        status = bm_split[3]

        return BattleMessage_curestatus(
            BMTYPE=BMType.curestatus, BATTLE_MESSAGE=battle_message, POKEMON=poke, STATUS=cast2dex(status, DexStatus)
        )


class BattleMessage_cureteam(BattleMessage):
    """
    |-cureteam|POKEMON|EFFECT
    """

    EFFECT: Effect = Field(..., description="The effect causing the team to be healed")

    def from_message(battle_message: str) -> "BattleMessage_cureteam":
        bm_split = battle_message.split("|")

        eff_source = PokemonIdentifier.from_string(bm_split[2])
        eff_type = bm_split[3].split(" ")[1][:-1]
        eff_name = " ".join(bm_split[3].split(" ")[2:])

        effect = Effect(EFFECT_NAME=eff_name, EFFECT_TYPE=eff_type, EFFECT_SOURCE=eff_source)

        return BattleMessage_cureteam(BMTYPE=BMType.cureteam, BATTLE_MESSAGE=battle_message, EFFECT=effect)


class BattleMessage_boost(BattleMessage):
    """
    |-boost|POKEMON|STAT|AMOUNT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(
        ...,
        description="By how much this stat is being boosted, as an integer. Can be 0 if at cap",
    )

    def from_message(battle_message: str) -> "BattleMessage_boost":
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
    """
    |-unboost|POKEMON|STAT|AMOUNT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(
        ...,
        description="By how much this stat is being boosted, as an integer. Can be 0 if at cap",
    )

    def from_message(battle_message: str) -> "BattleMessage_unboost":
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
    """
    |-setboost|POKEMON|STAT|AMOUNT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The Pokemon getting the boost")
    STAT: PokeStat = Field(..., description="Which stat is being boosted")
    AMOUNT: int = Field(..., description="The new value being assigned for this stat boost")

    def from_message(battle_message: str) -> "BattleMessage_setboost":
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
    """
    |-swapboost|SOURCE|TARGET|STATS
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_swapboost":
        raise NotImplementedError

        bm_split = battle_message.split("|")

        return BattleMessage_swapboost(
            BMTYPE=BMType.swapboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_invertboost(BattleMessage):
    """
    |-invertboost|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to invert the boosts of")

    def from_message(battle_message: str) -> "BattleMessage_invertboost":
        bm_split = battle_message.split("|")

        return BattleMessage_invertboost(
            BMTYPE=BMType.invertboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_clearboost(BattleMessage):
    """
    |-clearboost|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the boosts of")

    def from_message(battle_message: str) -> "BattleMessage_clearboost":
        bm_split = battle_message.split("|")

        return BattleMessage_clearboost(
            BMTYPE=BMType.clearboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_clearallboost(BattleMessage):
    """
    |-clearallboost
    """

    def from_message(battle_message: str) -> "BattleMessage_clearallboost":
        return BattleMessage_clearallboost(
            BMTYPE=BMType.clearallboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_clearpositiveboost(BattleMessage):
    """
    |-clearpositiveboost|TARGET|EFF_SOURCE|EFFECT
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the positive boosts of")

    EFFECT: Effect = Field(..., description="Details about the effect that is causing this positive boost clearance")

    def from_message(battle_message: str) -> "BattleMessage_clearpositiveboost":
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
    """
    |-clearnegativeboost|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon to clear the negative boosts of")

    def from_message(battle_message: str) -> "BattleMessage_clearnegativeboost":
        bm_split = battle_message.split("|")

        return BattleMessage_clearnegativeboost(
            BMTYPE=BMType.clearnegativeboost,
            BATTLE_MESSAGE=battle_message,
            POKEMON=PokemonIdentifier.from_string(bm_split[2]),
        )


class BattleMessage_copyboost(BattleMessage):
    """
    |-copyboost|SOURCE|TARGET
    """

    POKEMON: str = Field(..., description="The main pokemon identifier relevant")

    def from_message(battle_message: str) -> "BattleMessage_copyboost":
        raise NotImplementedError

        bm_split = battle_message.split("|")

        return BattleMessage_copyboost(
            BMTYPE=BMType.copyboost,
            BATTLE_MESSAGE=battle_message,
        )


class BattleMessage_weather(BattleMessage):
    """
    |-weather|WEATHER|EFFECT
    """

    # TODO: Add a weather validator or Literal
    WEATHER: DexWeather.ValueType = Field(..., description="The Weather")

    EFFECT: Optional[Effect] = Field(None, description="Optionally, the effect that caused this weather")

    def from_message(battle_message: str) -> "BattleMessage_weather":
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
    """
    |-fieldstart|CONDITION
    """

    EFFECT: Effect = Field(
        ...,
        description="The Effect starting for the field.",
    )

    def from_message(battle_message: str) -> "BattleMessage_fieldstart":
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
            ## A - |-start|POKEMON|MOVE
            ## B - |-start|POKEMON|MOVE|MOVE
            ## C - |-start|POKEMON|MOVE|[from] OR |-start|POKEMON|MOVE|[from]|[of]
            ## D - |-start|POKEMON|MOVE|MOVE|[from] OR |-start|POKEMON|MOVE|MOVE|[from]|[of]
            # Double moves are for things like disable or mimic. In these cases, the first move is the disable/mimic/etc
            # while the second move is the thing `being` disabled/mimic'd/etc
            # If we get 2 moves but no from then effect name will be the first move (disable/mimic/etc) and secondary will be the other (the disabled move)
            # If we get 1 move and a from, then the secondary effect will be the move, while the effect name and type will come from the from message
            # If we get 2 moves and a from, then we will drop the disable/mimic move, since the from takes precedence
            # This is a candidate to change in the future if we find we need both the [from] details and both moves listed
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
            ## A - |-end|POKEMON|MOVE
            ## B - |-end|POKEMON|MOVE|[DETAIL]
            ## C - |-end|POKEMON|MOVE|[from] OR |-end|POKEMON|MOVE|[from]|[of]
            # We will assign MOVE to EFFECT_NAME unless there is a from, in which case it will become the secondary effect to the from Effect
            # If there is not a [from] but instead a [DETAIL], MOVE will be the EFFECT_NAME while DETAIL will be the secondary effect
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
        description="The effect that destroyed the item, if applicable. Not used when obvious (White Herb, Berries, gems)",
    )

    def from_message(battle_message: str) -> "BattleMessage_enditem":
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        item = bm_split[3]

        # We do some quick filtering on the bm_split to get rid of any single detail things like [silent] or [eat]
        bm_split = [bm for bm in bm_split if len(bm.strip()) > 0 and bm.strip()[0] != "[" and bm.strip()[-1] != "]"]

        if len(bm_split) > 4:
            # This means there is at least a [from] clause and possibly also a [of] clause
            # However, enditem uses weird |[from] ATTRIBUTE|[move] MOVE or |[from] ATTRIBUTE syntax sometimes, so we need to parse that

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
                # For our purposes, we will set stealeat as the sec_effect, Bug Bit as eff_name, move as eff_type, and p1a: Ariados as eff_source

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
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])
        ability = bm_split[3]

        if len(bm_split) >= 5 and "[from]" in bm_split[4]:
            # Parse this message assuming the form |-ability|p1a: Gardevoir|Swarm|[from] ability: Trace|[of] p2a: Leavanny
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
        raise NotImplementedError

        bm_split = battle_message.split("|")

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
        raise NotImplementedError

        bm_split = battle_message.split("|")

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
        bm_split = battle_message.split("|")

        poke = PokemonIdentifier.from_string(bm_split[2])

        return BattleMessage_zpower(BMTYPE=BMType.zpower, BATTLE_MESSAGE=battle_message, POKEMON=poke)


class BattleMessage_zbroken(BattleMessage):
    """
    |-zbroken|POKEMON
    """

    POKEMON: PokemonIdentifier = Field(..., description="The pokemon whose Z move is over")

    def from_message(battle_message: str) -> "BattleMessage_zbroken":
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

    # ACTIVE_TYPE: Literal["VOLATILE", "MOVE", "ABILITY", "ITEM"] = Field(..., description="What kind of activation this is signifying")

    EFFECT: Effect = Field(..., description="The effect detailed in this activation")

    def from_message(battle_message: str) -> "BattleMessage_activate":
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
                # This means theres a secondary part to the effect, such as a move being mimic'd or an ability being overwritten with Mummy
                # In general, EFFECT_NAME should be the `more` relevant thing. So if you're activating the ability Mummy and losing Battle Armor
                ## then we would have Mummy be the EFFECT_NAME and SEC_EFFECT_NAME is Battle Armor. This is because we know for sure what category the
                ## primary EFFECT_NAME belongs to as it is told to us directly, but theoretically the secondary could be any type and we are not informed
                ## Lastly, if you're reading this, you have my deepest apologies, we're in this mess together at least!
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
        bm_split = battle_message.split("|")

        return BattleMessage_hint(BMTYPE=BMType.hint, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_center(BattleMessage):
    """
    |-center
    """

    def from_message(battle_message: str) -> "BattleMessage_center":
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
        bm_split = battle_message.split("|")

        return BattleMessage_message(BMTYPE=BMType.message, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_combine(BattleMessage):
    """
    |-combine
    """

    def from_message(battle_message: str) -> "BattleMessage_combine":
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
        raise NotImplementedError

        bm_split = battle_message.split("|")

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
        bm_split = battle_message.split("|")

        return BattleMessage_error(BMTYPE=BMType.error, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_bigerror(BattleMessage):
    """
    |bigerror|MESSAGE
    """

    MESSAGE: str = Field(..., description="The error message sent by showdown")

    def from_message(battle_message: str) -> "BattleMessage_bigerror":
        bm_split = battle_message.split("|")

        return BattleMessage_bigerror(BMTYPE=BMType.bigerror, BATTLE_MESSAGE=battle_message, MESSAGE=bm_split[2])


class BattleMessage_init(BattleMessage):
    """
    |init|battle
    """

    def from_message(battle_message: str) -> "BattleMessage_init":
        return BattleMessage_init(BMTYPE=BMType.init, BATTLE_MESSAGE=battle_message)


class BattleMessage_deinit(BattleMessage):
    """
    |deinit
    """

    def from_message(battle_message: str) -> "BattleMessage_deinit":
        return BattleMessage_deinit(BMTYPE=BMType.deinit, BATTLE_MESSAGE=battle_message)


class BattleMessage_title(BattleMessage):
    """
    |title|TITLE
    """

    TITLE: str = Field(..., description="The title of this match as shown on pokemon showdown")

    def from_message(battle_message: str) -> "BattleMessage_title":
        bm_split = battle_message.split("|")

        return BattleMessage_title(BMTYPE=BMType.title, BATTLE_MESSAGE=battle_message, TITLE=bm_split[2])


class BattleMessage_join(BattleMessage):
    """
    |join|USERNAME
    """

    USERNAME: str = Field(..., description="The username of the joining player")

    def from_message(battle_message: str) -> "BattleMessage_join":
        bm_split = battle_message.split("|")

        return BattleMessage_join(BMTYPE=BMType.join, BATTLE_MESSAGE=battle_message, USERNAME=bm_split[2])


class BattleMessage_leave(BattleMessage):
    """
    |leave|USERNAME
    """

    USERNAME: str = Field(..., description="The username of the leaving player")

    def from_message(battle_message: str) -> "BattleMessage_leave":
        bm_split = battle_message.split("|")

        return BattleMessage_leave(BMTYPE=BMType.leave, BATTLE_MESSAGE=battle_message, USERNAME=bm_split[2])


class BattleMessage_raw(BattleMessage):
    """
    |raw|MESSAGE
    """

    MESSAGE: str = Field(..., description="The raw message from Showdown. Typically used for rating changes.")

    def from_message(battle_message: str) -> "BattleMessage_raw":
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

if __name__ == "__main__":
    # message = '|request|{"forceSwitch":[true],"side":{"name":"colress-gpt","id":"p2","pokemon":[{"ident":"p2: Espeon","details":"Espeon, L81, M","condition":"0 fnt","active":true,"stats":{"atk":111,"def":144,"spa":256,"spd":201,"spe":224},"moves":["hiddenpowerfire","signalbeam","psychic","calmmind"],"baseAbility":"magicbounce","item":"lifeorb","pokeball":"pokeball"},{"ident":"p2: Blaziken","details":"Blaziken, L76, F","condition":"247/247","active":false,"stats":{"atk":226,"def":150,"spa":211,"spd":150,"spe":166},"moves":["highjumpkick","stoneedge","swordsdance","flareblitz"],"baseAbility":"speedboost","item":"lifeorb","pokeball":"pokeball"},{"ident":"p2: Dustox","details":"Dustox, L90, M","condition":"254/254","active":false,"stats":{"atk":95,"def":177,"spa":141,"spd":213,"spe":168},"moves":["sludgebomb","bugbuzz","quiverdance","roost"],"baseAbility":"shielddust","item":"blacksludge","pokeball":"pokeball"},{"ident":"p2: Scizor","details":"Scizor, L80, F","condition":"243/243","active":false,"stats":{"atk":254,"def":206,"spa":134,"spd":174,"spe":150},"moves":["roost","bugbite","pursuit","bulletpunch"],"baseAbility":"technician","item":"lifeorb","pokeball":"pokeball"},{"ident":"p2: Registeel","details":"Registeel, L82","condition":"265/265","active":false,"stats":{"atk":170,"def":293,"spa":170,"spd":293,"spe":129},"moves":["ironhead","sleeptalk","rest","toxic"],"baseAbility":"clearbody","item":"leftovers","pokeball":"pokeball"},{"ident":"p2: Skuntank","details":"Skuntank, L86, M","condition":"317/317","active":false,"stats":{"atk":209,"def":164,"spa":171,"spd":154,"spe":194},"moves":["crunch","taunt","suckerpunch","poisonjab"],"baseAbility":"aftermath","item":"blacksludge","pokeball":"pokeball"}]},"noCancel":true,"rqid":7}'

    # bm = BattleMessage_request.from_message(message)

    # print(bm)

    message = """|request|{"active":[{"moves":[{"move":"Thunderbolt","id":"thunderbolt","pp":23,"maxpp":24,"target":"normal","disabled":false},{"move":"Confuse Ray","id":"confuseray","pp":16,"maxpp":16,"target":"normal","disabled":false},{"move":"Psychic","id":"psychic","pp":15,"maxpp":16,"target":"normal","disabled":false},{"move":"Explosion","id":"explosion","pp":8,"maxpp":8,"target":"normal","disabled":false}]}],"side":{"name":"colress-gpt","id":"p1","pokemon":[{"ident":"p1: Haunter","details":"Haunter, L71","condition":"210/210 slp","active":true,"stats":{"atk":142,"def":134,"spa":234,"spd":234,"spe":205},"moves":["thunderbolt","confuseray","psychic","explosion"],"baseAbility":"noability","item":"","pokeball":"pokeball"},{"ident":"p1: Kangaskhan","details":"Kangaskhan, L73","condition":"27/304","active":false,"stats":{"atk":211,"def":189,"spa":131,"spd":131,"spe":204},"moves":["earthquake","surf","bodyslam","hyperbeam"],"baseAbility":"noability","item":"","pokeball":"pokeball"},{"ident":"p1: Dugtrio","details":"Dugtrio, L73","condition":"201/201","active":false,"stats":{"atk":189,"def":145,"spa":175,"spd":175,"spe":248},"moves":["bodyslam","earthquake","slash","rockslide"],"baseAbility":"noability","item":"","pokeball":"pokeball"},{"ident":"p1: Raticate","details":"Raticate, L76","condition":"0 fnt","active":false,"stats":{"atk":198,"def":166,"spa":151,"spd":151,"spe":223},"moves":["blizzard","hyperbeam","bodyslam","superfang"],"baseAbility":"noability","item":"","pokeball":"pokeball"},{"ident":"p1: Nidoran-F","details":"Nidoran-F, L93","condition":"0 fnt","active":false,"stats":{"atk":178,"def":188,"spa":165,"spd":165,"spe":167},"moves":["doublekick","bodyslam","blizzard","thunderbolt"],"baseAbility":"noability","item":"","pokeball":"pokeball"},{"ident":"p1: Articuno","details":"Articuno, L70","condition":"0 fnt","active":false,"stats":{"atk":125,"def":210,"spa":245,"spd":245,"spe":189},"moves":["icebeam","reflect","rest","blizzard"],"baseAbility":"noability","item":"","pokeball":"pokeball"}]},"rqid":62}"""

    bm = BattleMessage_request.from_message(message)

    print(bm.model_dump_json(indent=4))
