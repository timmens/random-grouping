from itertools import combinations
from itertools import count

import numpy as np


def find_best_matching(
    candidates, matchings_history, matching_params, penalty_func=None
):
    """Find best matching from list of candidates.

    Args:
        candidates (list): List of matching candidates.
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        matching_params (dict): Parameters that govern the behavior of the matching
            criterion. Default None. For detais see ``_add_defaults_params``.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.

    Returns:
        best_matching (list): Matching that minimizes the criterion.

    """
    criterion = np.empty(len(candidates))
    for k, candidate in enumerate(candidates):
        updated_history = update_matchings_history(matchings_history, candidate)
        score_for_history = _compute_history_score(updated_history, penalty_func)
        score_for_assortativity = _compute_assortativity_score(
            candidate, matching_params
        )
        criterion[k] = score_for_history + score_for_assortativity

    best_matching = candidates[np.argmin(criterion)]
    return best_matching


def _compute_history_score(matchings_history, penalty_func=None):
    """Compute score of grouping matrix.

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


def _compute_assortativity_score(matching, matching_params):
    """Compute assortativity score.

    Scores the matching by the fact whether the members of each group want an
    assortative or mixed group.

    Args:
        matching (list): Matching.
        matching_params (dict): Dictionary containig matching parameters.

    Returns:
        score (float): The corresponding score.

    """
    score = 0
    for group in matching:

        group = group.copy()
        wants_assortative = 1 - group.wants_mixing
        wants_assortative.loc[group.status == "faculty"] *= matching_params[
            "faculty_multiplier"
        ]

        if len(group.status.unique()) > 1:
            score += wants_assortative.mean()

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
        for comb in combinations(group.index.values, 2):
            updated_history.loc[comb[0], comb[1]] += 1
            updated_history.loc[comb[1], comb[0]] += 1

    return updated_history


def draw_candidate_matchings(participants, min_size, n_candidates, seed=0):
    """Create multiple random groupings in list-format.

    Args:
        participants (pd.DataFrame): d:f with columns 'id'(int), 'names'(str),
            'joins'(0/1), 'status'(student/faculty) and 'wants_mixing'(0/1)'. But only
            rows with joins equal to 1 are selected.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to simulate.
        seed (int): Initial seed to pass to the seed generator.

    Returns:
        candidates (list): List of candidate groupings.

    """
    seed_counter = count(seed)

    candidates = []
    for _ in range(n_candidates):
        matching = _create_candidate_matching(
            participants, min_size, next(seed_counter)
        )
        candidates.append(matching)

    return candidates


def _create_candidate_matching(participants, min_size, seed):
    """Create single matching candidate.

    Args:
        participants (pd.DataFrame): d:f with columns 'id'(int), 'names'(str),
            'joins'(0/1), 'status'(student/faculty) and 'wants_mixing'(0/1)'. But only
            rows with joins equal to 1 are selected.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to simulate.
        initial_seed (int): Initial seed to pass to the seed generator.

    Returns:
        candidate (list): Matching candidate.

    """
    np.random.seed(seed)
    ids = participants.index.values.copy()
    np.random.shuffle(ids)
    id_chunks = _create_chunks(ids, min_size)
    candidate = [participants.loc[chunk].copy() for chunk in id_chunks]
    return candidate


def _create_chunks(ids, min_size):
    """Create chunks of subgroups of list of ids.

    Args:
        ids (np.ndarray): Integer array with indeces over which we group.
        min_size (int): Minimum group size.

    Returns:
        chunks (list-like): Grouping candidate.

    Example:
    >>> ids = np.arange(10)
    >>> _create_chunks(ids, min_size=3)
    [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

    """
    n_chunks = len(ids) // min_size
    chunks = np.array_split(ids, n_chunks)
    chunks = [chunk.tolist() for chunk in chunks]
    return chunks
