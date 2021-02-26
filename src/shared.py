import numpy as np
import pandas as pd

from itertools import count
from itertools import combinations


def pick_best_candidate(candidates, grouping_df):
    scores = np.empty(len(candidates))
    for k, candidate in enumerate(candidates):
        updated_grouping_df = update_grouping_df(grouping_df, candidate)
        scores[k] = score_grouping_df(updated_grouping_df)

    minimum = candidates[np.argmin(scores)]
    updated_grouping_df = update_grouping_df(grouping_df, minimum)
    return updated_grouping_df, minimum 


def score_grouping_df(grouping_df, penalty_func=None):
    """Score grouping matrix.

    Scores grouping matrix such that having many large values is penalized.

    Args:
        grouping_df (pd.DataFrame): Square df containing group information. Index
            and column is given by the "id" column in SRC.data.names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in grouping_df.
    
    Returns:
        score (float): Score of grouping matrix.

    """
    penalty_func = np.exp if penalty_func is None else penalty_func

    values = grouping_df.values
    tril = np.tril(values).flatten()

    counts = np.bincount(tril)

    score = np.sum(counts * penalty_func(np.arange(len(counts))))
    return score


def update_grouping_df(grouping_df, new_grouping_candidate):
    """Update grouping matrix using new grouping candidate.

    Args:
        grouping_df (pd.DataFrame): Square df containing group information. Index
            and column is given by the "id" column in SRC.data.names.csv.
        new_grouping_candidate (list-like): Grouping candidate.

    Returns:
        updated_grouping_df (pd.DataFrame): Updated grouping matrix where group
            membership is noted as +1 in the respective column-row of grouping matrix.

    """
    updated_grouping_df = grouping_df.copy()
    
    for group in new_grouping_candidate:
        for comb in combinations(group, 2):
            updated_grouping_df.loc[comb[0], comb[1]] += 1
            updated_grouping_df.loc[comb[1], comb[0]] += 1  # So that matrix is symmetric

    return updated_grouping_df


def draw_groupings(members, min_size, n_candidates, initial_seed=0):
    """Create multiple random groupings in list-format.

    Args:
        members (pd.Series): Integer series with indeces over which we group.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to simulate.
        initial_seed (int): Initial seed to pass to the seed generator.

    Returns:
        candidates (list-like): List of candidate groupings.

    """
    seed_counter = count(initial_seed)
    
    candidates = []
    for i in range(n_candidates):
        grouping = create_grouping_candidate(members, min_size, next(seed_counter))
        candidates.append(grouping)

    return candidates


def create_grouping_candidate(members, min_size, seed):
    """Create single grouping candidate.

    Args:
        members (pd.Series): Integer series with indeces over which we group.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to simulate.
        initial_seed (int): Initial seed to pass to the seed generator.

    Returns:
        candidate (list-like): Grouping candidate.

    """
    np.random.seed(seed)
    members = members.values.copy()
    np.random.shuffle(members)
    candidate = create_chunks(members, min_size)
    return candidate


def create_chunks(members, min_size):
    """Create chunks of subgroups of list of members.

    Args:
        members (np.ndarray): Integer array with indeces over which we group.
        min_size (int): Minimum group size.

    Returns:
        chunks (list-like): Grouping candidate.

    """
    n_chunks = len(members) // min_size
    chunks = np.array_split(members, n_chunks)
    chunks = [set(chunk.tolist()) for chunk in chunks]
    return chunks
