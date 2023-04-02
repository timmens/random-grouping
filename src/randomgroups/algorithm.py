from itertools import combinations
from typing import List

import numpy as np
import pandas as pd


def find_optimal_matching(
    candidates: List[List[pd.DataFrame]],
    matchings_history: pd.DataFrame,
    penalty_func: callable,
    faculty_multiplier: float,
    assortative_matching: bool,
) -> List[pd.DataFrame]:
    """Find best matching from list of candidates.

    Args:
        candidates (list): List of matching candidates.
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.
        faculty_multiplier (float): Multiplier determining how much faculty members
            want to stay in the same group.
        assortative_matching (bool): Whether to use assortative matching.

    Returns:
        List[pd.DataFrame]: Matching that minimizes the criterion.

    """
    criterion_values = []
    for matching in candidates:
        updated_history = update_matchings_history(matchings_history, matching)
        score = _compute_history_score(updated_history, penalty_func)
        if assortative_matching:
            score += _compute_assortativity_score(matching, faculty_multiplier)
        criterion_values.append(score)

    optimal_matching = candidates[np.argmin(criterion_values)]
    return optimal_matching


def _compute_history_score(
    matchings_history: pd.DataFrame, penalty_func: callable
) -> float:
    """Compute score of grouping matrix.

    Scores grouping matrix such that having many large values are penalized.

    Args:
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.

    Returns:
        score (float): Score of grouping matrix.

    """
    values = matchings_history.values
    tril_indices = np.tril_indices(len(values), k=-1)
    tril = values[tril_indices]

    counts = np.bincount(tril)

    score = np.sum(counts * penalty_func(np.arange(len(counts))))
    return score


def _compute_assortativity_score(
    matching: List[pd.DataFrame], faculty_multiplier: float
) -> float:
    """Compute assortativity score.

    Scores the matching by the fact whether the members of each group want an
    assortative or mixed group.

    Args:
        matching (list): Matching.
        faculty_multiplier (float): Multiplier determining how much faculty members
            want to stay in the same group.

    Returns:
        float: The corresponding score.

    """
    score = 0.0
    for group in matching:
        if len(group.status.unique()) > 1:
            wants_assortative = 1 - group.wants_mixing
            wants_assortative.loc[group.status == "faculty"] *= faculty_multiplier
            score += wants_assortative.mean()

    return score


def update_matchings_history(
    matchings_history: pd.DataFrame, matching: List[pd.DataFrame]
) -> pd.DataFrame:
    """Update grouping matrix using matching.

    Args:
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        matching (List[pd.DataFrame]): Matching.

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


def draw_candidate_matchings(
    participants: pd.DataFrame, min_size: int, n_draws: int, rng: np.random.Generator
) -> List[List[pd.DataFrame]]:
    """Create multiple random groupings in list-format.

    Args:
        participants (pd.DataFrame): Subsetted names data frame.
        min_size (int): Minimum group size.
        n_draws (int): Number of draws.
        rng (np.random.Generator): Random number generator.

    Returns:
        List[List[pd.DataFrame]]: List of candidate matching.

    """
    candidates = [
        _create_candidate_matching(participants, min_size, rng=rng)
        for _ in range(n_draws)
    ]
    return candidates


def _create_candidate_matching(
    participants: pd.DataFrame, min_size: int, rng: np.random.Generator
) -> List[pd.DataFrame]:
    """Create single matching candidate.

    Args:
        participants (pd.DataFrame): Subsetted names data frame.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to simulate.
        rng (np.random.Generator): Random number generator.

    Returns:
        List[pd.DataFrame]: Matching candidate.

    """
    ids = participants.index.values.copy()
    rng.shuffle(ids)
    id_chunks = _create_chunks(ids, min_size)
    matching = [participants.loc[chunk].copy() for chunk in id_chunks]
    return matching


def _create_chunks(ids: np.ndarray, min_size: int) -> List[List[int]]:
    """Create chunks of subgroups of list of ids.

    Args:
        ids (np.ndarray): Integer array with indeces over which we group.
        min_size (int): Minimum group size.

    Returns:
        List[List[int]]: Splitted ids.

    """
    n_chunks = len(ids) // min_size
    chunks = np.array_split(ids, n_chunks)
    chunks = [chunk.tolist() for chunk in chunks]
    return chunks
