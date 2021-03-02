from itertools import combinations
from itertools import count

import numpy as np


def find_best_matching(candidates, matchings_history, penalty_func=None):
    """Find best (matching) candidate from list given some metric.

    Args:
        candidates (list): List of matching candidates.
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.

    Returns:
        best_matching (list): Matching with lowest loss.

    """
    scores = np.empty(len(candidates))
    for k, candidate in enumerate(candidates):
        updated_history = update_matchings_history(matchings_history, candidate)
        scores[k] = score_matchings_history(updated_history)

    best_matching = candidates[np.argmin(scores)]
    return best_matching


def score_matchings_history(matchings_history, penalty_func=None):
    """Score grouping matrix.

    Scores grouping matrix such that having many large values is penalized.

    Args:
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.

    Returns:
        score (float): Score of grouping matrix.

    """
    penalty_func = np.exp if penalty_func is None else penalty_func

    values = matchings_history.values
    tril = np.tril(values).flatten()

    counts = np.bincount(tril)

    score = np.sum(counts * penalty_func(np.arange(len(counts))))
    return score


def update_matchings_history(matchings_history, matching):
    """Update grouping matrix using new grouping candidate.

    Args:
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        matching (list): Matching.

    Returns:
        updated_history (pd.DataFrame): Updated grouping matrix where group
            membership is noted as +1 in the respective column-row of grouping matrix.

    """
    updated_history = matchings_history.copy()

    for group in matching:
        for comb in combinations(group, 2):
            updated_history.loc[comb[0], comb[1]] += 1
            updated_history.loc[comb[1], comb[0]] += 1

    return updated_history


def draw_candidate_matchings(members, min_size, n_candidates, initial_seed=0):
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
    for _ in range(n_candidates):
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
