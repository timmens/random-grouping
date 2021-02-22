"""Create grouping candidate."""
import numpy as np


def create_chunks(l, min_size):
    n_chunks = len(l) // min_size
    chunks = np.array_split(l, n_chunks)
    chunks = [set(chunk.tolist()) for chunk in chunks]
    return chunks

def shuffle_members(members):
    members = members.copy()
    np.random.shuffle(members)
    return members

def create_grouping_candidate(members, min_size, seed):
    np.random.seed(seed)
    shuffled = shuffle_members(members)
    chunks = create_chunks(shuffled, min_size)
    return chunks
