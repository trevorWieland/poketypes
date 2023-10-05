from statics import MAX_MON_IDX_PER_GEN, MAX_MOVE_IDX_PER_GEN


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
        if "num" not in value:
            assert "inherit" in value and value["inherit"], (gen, move, value)
        elif value["num"] > MAX_MOVE_IDX_PER_GEN[gen]:
            continue

        if move not in this_gen_data:
            this_gen_data[move] = value
        elif this_gen_data[move].get("inherit", False):
            this_gen_data[move] = {**value, **this_gen_data[move]}
            this_gen_data[move].pop("inherit")

    return this_gen_data


def merge(data_type, gen, this_gen_data, next_gen_data):
    merge_dict = {
        "pokedex": merge_pokedex,
        "moves": merge_moves,
    }

    if merge_dict.get(data_type) is None:
        return None

    return merge_dict[data_type](gen, this_gen_data, next_gen_data)
