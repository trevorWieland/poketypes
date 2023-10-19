from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .dexdata_pb2 import (
    DexAbility,
    DexItem,
    DexMove,
    DexMoveCategory,
    DexMoveTarget,
    DexPokemon,
    DexStat,
    DexType,
    DexWeather,
)


class PokedexMove(BaseModel):
    """
    Pokedex class for Moves.

    Contains information about move type, accuracy, base power, etc.
    """

    # TODO: Finish adding remaining fields (pseudoWeathers, volatile conditions, secondaries, etc)

    # Identification fields
    name: str = Field(..., description="Friendly string name of this move")
    id: DexMove.ValueType = Field(..., description="The DexMove ID of this move")

    # Mandatory fields
    base_power: int = Field(..., description="The base power of the move")
    pp: int = Field(..., description="The pp of this move")
    priority: int = Field(..., description="The priority of the move", ge=-6, le=6)
    crit_ratio: int = Field(1, description="The crit ratio of the move (e.g. 2 = twice the chance to crit)")

    category: DexMoveCategory.ValueType = Field(..., description="The move category as a DexMoveCategory")
    target: DexMoveTarget.ValueType = Field(..., description="The target type of this move")
    mtype: DexType.ValueType = Field(..., description="The type of the move")

    # Standard boolean fields
    breaks_protect: bool = Field(False, description="Whether the move breaks target protect")
    ignore_ability: bool = Field(False, description="Whether the move ignores target ability")
    ignore_defensive: bool = Field(False, description="Whether the move ignores target defensive boosts")
    ignore_evasion: bool = Field(False, description="Whether the move ignores target evasion boosts")
    ignore_immunity: bool = Field(False, description="Whether the move ignores target immunity to this move type")
    multiaccuracy: bool = Field(False, description="Whether the multihit move is all or nothing")
    ohko: bool = Field(False, description="Whether the move is a one-hit-ko")
    stalling_move: bool = Field(False, description="Whether the move is considered a stalling move")
    will_crit: bool = Field(False, description="Whether the move will 100% crit if it lands")
    has_crash_damage: bool = Field(False, description="Whether the move does damage to its user on failure")
    has_sheer_force: bool = Field(False, description="The move is always boosted by sheer-force without losing benefit")
    selfdestruct_always: bool = Field(False, description="Whether this move always causes the user to faint")
    selfdestruct_ifhit: bool = Field(
        False, description="Whether the move causes the user to faint *if and only if* it hits"
    )
    steals_boosts: bool = Field(False, description="Whether the move steals the targets boosts")
    level_damage: bool = Field(False, description="Whether the move does damage based on the level of the user")
    force_switch: bool = Field(False, description="Whether the move forces the target to switch out")
    mindblown_recoil: bool = Field(False, description="Whether the move has special 'Mind Blown' style recoil")
    struggle_recoil: bool = Field(False, description="Whether the move has special 'Struggle' style recoil")
    smart_target: bool = Field(False, description="Whether the move uses smart targetting")
    thaws_target: bool = Field(False, description="Whether the move thaws target as a special effect")
    tracks_target: bool = Field(False, description="Whether the move ignores `draw-in` move/abilities.")
    selfswitch_standard: bool = Field(
        False, description="Whether the move is a typical self-switching move. Teleport/U-Turn/etc"
    )
    selfswitch_volatile: bool = Field(
        False, description="Whether the move is a volatile-keeping self-switching move. Baton Pass"
    )
    selfswitch_shedtail: bool = Field(
        False, description="Whether the move is a substitue creating self-switching move. Shed Tail"
    )
    sleep_usable: bool = Field(False, description="Whether the move can be used when sleeping")
    no_metronome: bool = Field(False, description="Whether the move can *NOT* be used as a result of metronome")
    no_sketch: bool = Field(False, description="Whether the move can *NOT* be copied as a result of sketch")
    no_ppboosts: bool = Field(False, description="Whether the move can *NOT* have its pp boosted beyond default")

    # Move Flag information (Normally appears in move.flags)
    # TODO: Add better descriptions for each flag
    flag_allyanim: bool = Field(False, description="MOVE FLAG: allyanim")
    flag_bite: bool = Field(False, description="MOVE FLAG: bite")
    flag_bullet: bool = Field(False, description="MOVE FLAG: bullet")
    flag_bypasssub: bool = Field(False, description="MOVE FLAG: bypasssub")
    flag_cantusetwice: bool = Field(False, description="MOVE FLAG: cantusetwice")
    flag_charge: bool = Field(False, description="MOVE FLAG: charge")
    flag_contact: bool = Field(False, description="MOVE FLAG: contact")
    flag_dance: bool = Field(False, description="MOVE FLAG: dance")
    flag_defrost: bool = Field(False, description="MOVE FLAG: defrost")
    flag_distance: bool = Field(False, description="MOVE FLAG: distance")
    flag_failcopycat: bool = Field(False, description="MOVE FLAG: failcopycat")
    flag_failencore: bool = Field(False, description="MOVE FLAG: failencore")
    flag_failinstruct: bool = Field(False, description="MOVE FLAG: failinstruct")
    flag_failmefirst: bool = Field(False, description="MOVE FLAG: failmefirst")
    flag_failmimic: bool = Field(False, description="MOVE FLAG: failmimic")
    flag_futuremove: bool = Field(False, description="MOVE FLAG: futuremove")
    flag_gravity: bool = Field(False, description="MOVE FLAG: gravity")
    flag_heal: bool = Field(False, description="MOVE FLAG: heal")
    flag_mirror: bool = Field(False, description="MOVE FLAG: mirror")
    flag_mustpressure: bool = Field(False, description="MOVE FLAG: mustpressure")
    flag_noassist: bool = Field(False, description="MOVE FLAG: noassist")
    flag_nonsky: bool = Field(False, description="MOVE FLAG: nonsky")
    flag_noparentalbond: bool = Field(False, description="MOVE FLAG: noparentalbond")
    flag_nosleeptalk: bool = Field(False, description="MOVE FLAG: nosleeptalk")
    flag_pledgecombo: bool = Field(False, description="MOVE FLAG: pledgecombo")
    flag_powder: bool = Field(False, description="MOVE FLAG: powder")
    flag_protect: bool = Field(False, description="MOVE FLAG: protect")
    flag_pulse: bool = Field(False, description="MOVE FLAG: pulse")
    flag_punch: bool = Field(False, description="MOVE FLAG: punch")
    flag_recharge: bool = Field(False, description="MOVE FLAG: recharge")
    flag_reflectable: bool = Field(False, description="MOVE FLAG: reflectable")
    flag_slicing: bool = Field(False, description="MOVE FLAG: slicing")
    flag_snatch: bool = Field(False, description="MOVE FLAG: snatch")
    flag_sound: bool = Field(False, description="MOVE FLAG: sound")
    flag_wind: bool = Field(False, description="MOVE FLAG: wind")

    # Optional fields
    accuracy: Optional[int] = Field(
        None, description="The accuracy of this move. Optional if the move bypasses accuracy"
    )
    multihit: Optional[Tuple[int, int]] = Field(
        None, description="The move hits multiple times from slot0 - slot1 times inclusive. Optional"
    )
    drain: Optional[Tuple[int, int]] = Field(
        None, description="The move drains hp: (slot0 / slot1) times damage dealt. Optional"
    )
    heal: Optional[Tuple[int, int]] = Field(
        None, description="The move directly heals hp: (slot0 / slot1) times maximum health. Optional"
    )
    recoil: Optional[Tuple[int, int]] = Field(
        None, description="The move recoils back hp: (slot0 / slot1) times damage dealt. Optional"
    )
    boosts: Optional[Dict[DexStat.ValueType, int]] = Field(
        None, description="Any boosts for the target this move provides (100%). Optional"
    )
    direct_damage: Optional[int] = Field(None, description="An integer exact amount of damage the move does. Optional")
    weather: Optional[DexWeather.ValueType] = Field(None, description="The weather started by this move. Optional")


class PokedexItem(BaseModel):
    """
    Pokedex class for Items.

    Contains basic information about items
    """

    # Identification fields
    name: str = Field(..., description="Friendly string name of this item")
    id: DexItem.ValueType = Field(..., description="The DexItem ID of this item")

    is_gem: bool = Field(False, description="Whether the item is a gem or not")

    # Berry stuff
    is_berry: bool = Field(False, description="Whether the item is a berry")
    naturalgift_base_power: Optional[int] = Field(
        None, description="If this item is usable with Natural Gift, what is the base power"
    )
    naturalgift_type: Optional[DexType.ValueType] = Field(
        None, description="If this item is usable with Natural Gift, what is the type"
    )

    item_users: List[DexPokemon.ValueType] = Field([], description="A list of intended holders of this item")

    # ZMove stuff
    zmove_to: Optional[DexMove.ValueType] = Field(None, description="What move this zmove transforms the move *into*")
    zmove_from: Optional[DexMove.ValueType] = Field(None, description="What special move this zmove transforms")

    # Mega stuff
    mega_evolves: Optional[DexPokemon.ValueType] = Field(
        None, description="Which base-forme pokemon this megastone evolves from. Optional"
    )
    mega_forme: Optional[DexPokemon.ValueType] = Field(
        None, description="Which mega-forme pokemon this megastone evolves into. Optional"
    )

    ignore_klutz: bool = Field(False, description="Whether the item ignores klutz")

    fling_basepower: Optional[int] = Field(
        None, description="The basepower of fling when flinging this item. None if n/a"
    )


class StatBlock(BaseModel):
    """
    Helper object for containing base stats
    """

    hp_stat: int = Field(..., description="The base hp of the pokemon")
    atk_stat: int = Field(..., description="The base attack of the pokemon")
    def_stat: int = Field(..., description="The base defence of the pokemon")
    spa_stat: int = Field(..., description="The base special attack of the pokemon")
    spd_stat: int = Field(..., description="The base special defence of the pokemon")
    spe_stat: int = Field(..., description="The base speed of the pokemon")


class PokedexPokemon(BaseModel):
    """
    Pokedex class for Pokemon.

    Contains information about pokemon
    """

    # TODO: Most of the work still needs to be done

    # Identification fields
    name: str = Field(..., description="Friendly string name of this pokemon")
    id: DexPokemon.ValueType = Field(..., description="The DexPokemon ID of this pokemon")

    base_name: str = Field(..., description="Friendly string name of this pokemon's base forme")
    base_id: DexPokemon.ValueType = Field(..., description="The DexPokemon ID of this pokemon's base forme")

    types: List[DexType.ValueType] = Field(..., description="The types of this pokemon")

    base_stats: StatBlock = Field(..., description="The base stat block of this pokemon")

    abilities: List[DexAbility.ValueType] = Field(..., description="The list of abilities this pokemon can have")
