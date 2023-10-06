from statics import MAX_MON_IDX_PER_GEN, MAX_MOVE_IDX_PER_GEN, MAX_ABILITY_IDX_PER_GEN


def merge_pokedex(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges pokemon-related data, dropping pokemon not in this gen/earlier, and overwriting as needed
    """
    for mon, value in next_gen_data.items():
        if value.get("num", 9999) > MAX_MON_IDX_PER_GEN[gen]:
            # Skips pokemon without a pokedex number / from a later gen
            continue
        elif value.get("num", -1) < 1:
            # Skips fakemon
            continue
        elif value.get("gen", gen) > gen:
            # If gen is given, use gen
            continue
        elif gen == 8 and "Paldea" in value.get("forme", ""):
            # Filter out paldean formes for older gens
            continue
        elif (
            gen == 7
            and "Gmax" in value.get("forme", "")
            or "Galar" in value.get("forme", "")
            or "Hisui" in value.get("forme", "")
        ):
            # Filter out Gmax/Galar/Hisui formes for older gens
            continue
        elif (
            gen == 6
            and "Alola" in value.get("forme", "")
            or "Starter" in value.get("forme", "")
            or "Totem" in value.get("forme", "")
        ):
            # Filter out Alola/LGPE/Totem formes for older gens
            continue
        elif gen == 5 and "Mega" in value.get("forme", ""):
            # Filter out Mega formes for older gens
            continue

        if mon not in this_gen_data:
            # Note: This doesn't mean the pokemon is from after this gen,
            # it just means from gen_next -> this_gen there is no differences for this pokemon
            this_gen_data[mon] = value
        elif this_gen_data[mon].get("inherit", False):
            # If inherit is True, then we want to take mostly data from later gens and update it with current gen data
            this_gen_data[mon] = {**value, **this_gen_data[mon]}
            this_gen_data[mon].pop("inherit")

        # Mechanic filtering
        if gen == 4:
            # Hidden Abilities were introduced in gen 5
            this_gen_data[mon]["abilities"].pop("H", None)
        elif gen == 2:
            # Abilities were introduced in gen 3
            this_gen_data[mon]["abilities"] = {0: "No Ability"}

    return this_gen_data


def merge_moves(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges move-related data, dropping moves not in this gen/earlier, and overwriting as needed
    """
    for move, value in next_gen_data.items():
        if value["num"] > MAX_MOVE_IDX_PER_GEN[gen] or value["num"] < 1:
            continue

        if move not in this_gen_data:
            this_gen_data[move] = value
        elif this_gen_data[move].get("inherit", False):
            this_gen_data[move] = {**value, **this_gen_data[move]}
            this_gen_data[move].pop("inherit")

    return this_gen_data


def merge_abilities(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges abilities data, dropping abilities not in this gen/earlier, and overwriting as needed
    """
    for ability, value in next_gen_data.items():
        if value.get("num") is None:
            continue

        if value["num"] > MAX_ABILITY_IDX_PER_GEN[gen] or value["num"] < 0:
            continue

        if ability not in this_gen_data:
            this_gen_data[ability] = value
        elif this_gen_data[ability].get("inherit", False):
            this_gen_data[ability] = {**value, **this_gen_data[ability]}
            this_gen_data[ability].pop("inherit")

    return this_gen_data


def merge_typechart(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges typechart-related data, including type-effectiveness
    """

    if this_gen_data is None:
        return next_gen_data

    for t, t_data in next_gen_data.items():
        if t not in this_gen_data:
            this_gen_data[t] = t_data
        elif this_gen_data[t].get("inherit", False):
            this_gen_data[t] = {**t_data, **this_gen_data[t]}
            this_gen_data[t].pop("inherit")

    return this_gen_data


def merge_natures(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges nature-related data
    """

    # natures were introduced in gen 3
    if gen < 3:
        return None

    if this_gen_data is None:
        return next_gen_data

    for n, n_data in next_gen_data.items():
        if n not in this_gen_data:
            this_gen_data[n] = n_data
        elif this_gen_data[n].get("inherit", False):
            this_gen_data[n] = {**n_data, **this_gen_data[n]}
            this_gen_data[n].pop("inherit")

    return this_gen_data


def merge_items(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges item-related data
    """

    if this_gen_data is None:
        return next_gen_data

    for item, item_data in next_gen_data.items():
        if item_data["gen"] > gen:
            continue

        if item not in this_gen_data:
            this_gen_data[item] = item_data
        elif this_gen_data[item].get("inherit", False):
            this_gen_data[item] = {**item_data, **this_gen_data[item]}
            this_gen_data[item].pop("inherit")

    return this_gen_data


def merge_learnsets(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges learnset related data
    """

    if this_gen_data is None:
        return next_gen_data

    for poke, learnset_data in next_gen_data.items():
        if len(learnset_data.get("learnset", [])) == 0:
            continue

        # Remove learn methods from future gens
        learnset = {
            move: [lm for lm in learn_methods if int(lm[0]) <= gen]
            for move, learn_methods in learnset_data["learnset"].items()
        }
        # Remove irrelevant moves (moves that can only be learned in future gens)
        learnset = {move: learn_methods for move, learn_methods in learnset.items() if len(learn_methods) > 0}

        # If we have removed every move, this must be a future pokemon
        if len(learnset.keys()) == 0:
            continue

        new_learnset_data = learnset_data
        new_learnset_data["learnset"] = learnset

        if poke not in this_gen_data:
            this_gen_data[poke] = new_learnset_data
        elif this_gen_data[poke].get("inherit", False):
            this_gen_data[poke] = {**new_learnset_data, **this_gen_data[poke]}
            this_gen_data[poke].pop("inherit")

    return this_gen_data


def merge_conditions(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges conditions data, though we just keep the latest since all that changes is functional
    """

    return next_gen_data


def merge_formats(gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Specifically merges format data, though we just keep the raw current gen since there is no inherit function
    """

    return this_gen_data


MERGE_DICT = {
    "pokedex": merge_pokedex,
    "moves": merge_moves,
    "typechart": merge_typechart,
    "items": merge_items,
    "learnsets": merge_learnsets,
    "natures": merge_natures,
    "abilities": merge_abilities,
    "conditions": merge_conditions,
    "formats-data": merge_formats,
}


def merge(data_type, gen, this_gen_data, next_gen_data):
    """
    Merges detailed data from `next_gen_data` into `this_gen_data`, dropping irrelevant data

    Automatically identifies which merge_function to use based on data_type

    If no merge_function is available, will return None
    """

    if MERGE_DICT.get(data_type) is None:
        return None

    return MERGE_DICT[data_type](gen, this_gen_data, next_gen_data)
