from itertools import combinations
from typing import List, Union, Dict

import numpy as np
import pandas as pd


def find_optimal_matching(
    candidates: List[List[pd.DataFrame]],
    matchings_history: pd.DataFrame,
    penalty_func: callable,
    mixing_multiplier: Dict[str, float],
    assortative_matching: bool,
) -> List[pd.DataFrame]:
    """Find best matching from list of candidates.

    Args:
        candidates (list): List of matching candidates.
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.
        mixing_multiplier (Dict[str, float]): Multiplier determining how many members
            of different status want to stay in the same group. Positive values favor
            assortative matchings, negative values favor mixed matchings.
            Can only be used if assortative_matching is True.
        assortative_matching (bool): Whether to use assortative matching.

    Returns:
        List[pd.DataFrame]: Matching that minimizes the criterion.

    """
    criterion_values = []
    for matching in candidates:
        updated_history = update_matchings_history(matchings_history, matching)
        score = _compute_history_score(updated_history, penalty_func)
        if assortative_matching:
            score += _compute_assortativity_score(matching, mixing_multiplier)
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
    matching: List[pd.DataFrame], mixing_multiplier: Dict[str, float]
) -> float:
    """Compute assortativity score.

    Scores the matching by the fact whether the members of each group want an
    assortative or mixed group.

    Args:
        matching (list): Matching.
        mixing_multiplier (Dict[str, float]): Multiplier determining how many members
            of different status want to stay in the same group. Positive values favor
            assortative matchings, negative values favor mixed matchings.

    Returns:
        float: The corresponding score.

    """
    # check if group has more than one status
    statuses_columns = [col for col in matching[0].columns if "status" in col]

    score = 0.0
    for group in matching:
        for status in statuses_columns:
            unique_status = group[status].dropna().unique()
            n_unique_status = len(unique_status)
            if n_unique_status > 1:
                wants_assortative = 1 - group.wants_mixing
                wants_assortative *= mixing_multiplier[status] * n_unique_status
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
        ids (np.ndarray): Integer array with indices over which we group.
        min_size (int): Minimum group size.

    Returns:
        List[List[int]]: Splitted ids.

    """
    n_chunks = len(ids) // min_size
    chunks = np.array_split(ids, n_chunks)
    chunks = [chunk.tolist() for chunk in chunks]
    return chunks


def update_min_size_using_n_groups(
    min_size: int,
    n_groups: int,
    n_participants: int,
) -> int:
    """Determine group size from number of groups.

    Args:
        min_size (int): Minimum group size.
        n_groups (int): Number of groups.
        n_participants (int): Number of participants.

    Returns:
        int: New min_size.

    """
    updated_min_size = n_participants // n_groups

    if min_size > updated_min_size:
        raise ValueError(
            f"There are not enough participants ({n_participants}) to create "
            f"{n_groups} groups with at least {min_size} members. Please decrease"
            "n_groups or decrease min_size."
        )

    return updated_min_size


def get_number_of_excluded_participants(
    min_size: int,
    max_size: int,
    n_groups: Union[int, None],
    n_participants: int,
) -> int:
    """Determine number of excluded participants using min_size, max_size and n_groups.

    Args:
        min_size (int): Updated minimum group size.
        max_size (int or None): Maximum group size.
        n_groups (int or None): Number of groups.
        n_participants (int): Number of participants.

    Returns:
        - int: Number of participants to exclude.
        - bool: Whether group_size needs to be consolidated again with n_groups and
        number of participants.

    """
    n_to_exclude = 0
    requires_consolidation = False

    if n_groups is not None:
        n_to_exclude = max(0, n_participants - n_groups * max_size)

        if n_to_exclude > 0:
            # need to adjust group_size to n_groups and new number of participants
            requires_consolidation = True

    elif max_size == min_size:
        n_to_exclude = n_participants % max_size

    return n_to_exclude, requires_consolidation
