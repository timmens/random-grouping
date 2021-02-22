"""Create random groups of (minimum) size 3 for multiple dates.

"""
import random
import yaml
import numpy as np

# CONFIG INFORMATION

CURRENT_DATE = 5

date_0 = {
    "members": {
        0: "Antonia E",
        1: "Daniel",
        2: "Fabio",
        3: "Joern",
        4: "Luis",
        5: "Malin",
        6: "Mark",
        7: "Melina",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        11: "Philipp H",
        12: "Philipp S",
        13: "Sebastian",
        14: "Tim",
        15: "Timothy",
    },
    "grouping": [{6, 5, 4}, {0, 13, 14}, {15, 1, 7}, {2, 12, 11}, {8, 9, 10, 3},],
}

date_1 = {
    "members": {
        0: "Antonia E",
        1: "Daniel",
        2: "Fabio",
        3: "Joern",
        4: "Luis",
        5: "Malin",
        6: "Mark",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        12: "Philipp S",
        13: "Sebastian",
        14: "Tim",
        15: "Timothy",
        16: "Alexandros",  # new members from here
        17: "Miriam",
        18: "Bilge",
        19: "Julius",
        20: "Marcel",
    },
    "grouping": [{18, 0, 4, 2}, {14, 10, 12}, {9, 8, 5}, {20, 1, 17}, {19, 3, 15}, {13, 16, 6}],
}

date_2 = {
    "members": {
        1: "Daniel",
        2: "Fabio",
        3: "Joern",
        4: "Luis",
        6: "Mark",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        12: "Philipp S",
        13: "Sebastian",
        14: "Tim",
        15: "Timothy",
        16: "Alexandros",
        17: "Miriam",
        18: "Bilge",
        19: "Julius",
        20: "Marcel",
        21: "Lorenzo",
    },
    "grouping": [{18, 14, 15}, {8, 17, 4}, {10, 12, 21}, {16, 19, 6}, {9, 2, 20}, {1, 3, 13}]
}

date_3 = {
    "members": {
        1: "Daniel",
        4: "Luis",
        6: "Mark",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        12: "Philipp S",
        13: "Sebastian",
        14: "Tim",
        15: "Timothy",
        16: "Alexandros",
        17: "Miriam",
        18: "Bilge",
        19: "Julius",
        20: "Marcel",
        21: "Lorenzo",
    },
   "grouping": [{13,4,12,20}, {9,19,15}, {16, 1,14}, {8, 18, 21}, {17, 10, 6}]
}

date_4 = {
    "members": {
        1: "Daniel",
        2: "Fabio",
        4: "Luis",
        6: "Mark",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        12: "Philipp S",
        13: "Sebastian",
        14: "Tim",
        15: "Timothy",
        16: "Alexandros",
        17: "Miriam",
        21: "Lorenzo",
    },
    "grouping": [{1, 10, 4, 9}, {8, 2, 13, 6}, {16, 17, 15}, {12, 21, 14}]
}

date_5 = {
    "members": {
        1: "Daniel",
        2: "Fabio",
        4: "Luis",
        8: "Oleksii",
        9: "Paul B",
        10: "Paul G",
        12: "Philipp S",
        14: "Tim",
        15: "Timothy",
        16: "Alexandros",
        17: "Miriam",
        21: "Lorenzo",
    },
    "grouping": [{16,9,15}, {1,10,4}, {8,17,21}, {2,12,14}]
}

# ALGORITHM


def create_chunks(l, min_size):
    """Split list in chunks of given (minimum) size."""
    n_chunks = len(l) // min_size
    chunks = np.array_split(l, n_chunks)
    chunks = [set(chunk.tolist()) for chunk in chunks]
    return chunks


def check_chunk_equality(grouping0, grouping1):
    """Check for equality of at least on chunk."""
    equality_check = False
    for chunk0 in grouping0:
        for chunk1 in grouping1:
            if chunk0 == chunk1:
                equality_check = True
                break
    return equality_check


def get_current_members():
    var_name = f"date_{CURRENT_DATE}"
    date_dict = globals()[var_name]
    members = date_dict["members"]
    return members


def shuffle_members(members):
    members_id = list(members.keys())
    random.shuffle(members_id)
    return members_id


def get_previous_groupings():
    var_names = [f"date_{t}" for t in range(CURRENT_DATE)]
    groupings = [globals()[var_name]["grouping"] for var_name in var_names]
    return groupings


def create_random_chunks(members, min_size=3):
    shuffled = shuffle_members(members)
    chunks = create_chunks(shuffled, min_size)
    return chunks


def create_new_grouping(members, previous_groupings):
    while True:
        candidate = create_random_chunks(members)
        for old_grouping in previous_groupings:
            if check_chunk_equality(candidate, old_grouping):
                continue
        break
    return candidate


def grouping_to_name(grouping, members):
    named_grouping = {
        f"group{g}": [members[id_] for id_ in group] for g, group in enumerate(grouping)
    }
    return named_grouping


def write_results(grouping, named_grouping):
    grouping = {f"group{g}": list(group) for g, group in enumerate(grouping)}
    results = {
        "named_grouping": named_grouping,
        "grouping": grouping,
    }
    with open("results.yaml", "w") as outfile:
        yaml.dump(results, outfile)


if __name__ == "__main__":
    members = get_current_members()
    previous_groupings = get_previous_groupings()
    grouping = create_new_grouping(members, previous_groupings)
    named_grouping = grouping_to_name(grouping, members)
    write_results(grouping, named_grouping)
