import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional

from randomgroups.algorithm import draw_candidate_matchings
from randomgroups.algorithm import find_optimal_matching
from randomgroups.algorithm import update_matchings_history
from randomgroups.io import format_matching_as_str
from randomgroups.io import read_names
from randomgroups.io import read_or_create_matchings_history
from randomgroups.io import write_matching
from randomgroups.io import write_matchings_history


def create_matching(
    names_path: Union[str, Path] = None,
    matchings_history_path: Union[str, Path] = None,
    output_path: Union[str, Path] = None,
    min_size: int = 2,
    n_groups: Optional[int] = None,
    max_size: Optional[int] = None,
    penalty_func: callable = np.exp,
    faculty_multiplier: float = 3.0,
    assortative_matching: bool = False,
    n_draws: int = 1_000,
    seed: int = 12345,
    return_results: bool = False,
    overwrite: bool = False,
):
    """Create matching.

    Args:
        names_path (str or pathlib.Path): Local path to or URL of names data file.
        matchings_history_path (str or pathlib.Path): Path to matchings history file.
        output_path (str or pathlib.Path): Output path. If None output is not written.
        min_size (int): Minimum group size.
        n_groups (int or None): Number of groups to create. If None, min_size is used to determine the number of groups.
        max_size (int or None): Setting a maximal group size can lead to participants being excluded (the participants
            with the most matchings in history file). If None, no maximum size is enforced.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.
        faculty_multiplier (float): Multiplier determining how much faculty members
            want to stay in the same group.
        assortative_matching (bool): Whether to use assortative matching.
        n_draws (int): Number of candidate groups to try during loss minimization.
        seed (int): Seed from which to start the seed generator.
        return_results (bool): Indicates whether the results should be returned.
        overwrite (bool): Whether to overwrite output files.

    Returns:
        if return_results is True, returns dictionary with entries:
        - best_matching_str (str)
        - best_matching (list)
        - updated_history (pd.DataFrame)

    """
    # ==================================================================================
    # Input validation
    # ==================================================================================

    if output_path is None and return_results is False:
        raise ValueError(
            "No output path is given and return_results is set to False. Please either "
            "pass a valid output path or set return_results to True."
        )

    names_path = Path(names_path)
    matchings_history_path = Path(matchings_history_path)
    output_path = None if output_path is None else Path(output_path)

    test_penalties = penalty_func(np.array([1, 2, 3]))
    if not isinstance(test_penalties, np.ndarray) or len(test_penalties) != 3:
        raise ValueError(
            "penalty_func must return a numpy array of the same length as the input "
            "array."
        )

    # check if max_size is valid
    if max_size is not None and min_size > max_size:
        raise ValueError(
            f"min_size ({min_size}) must be smaller than max_size ({max_size})."
        )

    # ==================================================================================
    # Read and verify data
    # ==================================================================================

    names = read_names(names_path)

    participants = names.query("joins == 1").set_index("id")
    participants = participants.convert_dtypes()

    if not participants.index.is_unique:
        raise ValueError("id column in names table is not unique.")
    if len(participants) < min_size:
        raise ValueError("There are less participants than 'min_size'.")

    if "status" not in names.columns and assortative_matching:
        raise ValueError(
            "Assortative matching is requested but 'status' column is not present in "
            "names table."
        )

    matchings_history = read_or_create_matchings_history(
        names=names,
        path=matchings_history_path,
    )
    matchings_history = _add_new_individuals(
        matchings_history=matchings_history,
        names=names,
    )

    # ==================================================================================
    # Adapt min_size if max_size or n_groups is set
    # ==================================================================================

    # if n_groups is set, we set min_size accordingly to get n_groups
    if n_groups is not None:
        group_min_size = len(participants) // n_groups
        if min_size > group_min_size:
            raise ValueError(
                f"There are not enough participants ({len(participants)}) to create "
                f"{n_groups} groups with at least {min_size} members. "
                "Please decrease n_groups or decrease min_size."
            )
        else:
            min_size = group_min_size

    # we check if max_size is set
    if max_size is not None:
        n_to_exclude = 0
        if n_groups is not None:
            # n_groups is set, need to adjust min_size accordingly
            # already checked that min_size < max_size
            n_to_exclude = len(participants) - n_groups * max_size
            if n_to_exclude > 0:
                min_size = (len(participants) - n_to_exclude) // n_groups
        elif max_size == min_size:
            # check if we need to exclude participants in order to have groups size = max_size
            n_to_exclude = len(participants) % max_size
        else:
            # if n_groups is not set:
            # groups produced by the algorithm will be maximal of size min_size+1
            # only if max_size == min_size we need to do something
            pass

        if n_to_exclude > 0:
            # we exclude those people with most matchings (and first to appear in the name list)
            # this is not optimal with regard to mixing people
            n_matches = (
                matchings_history.loc[participants.index]
                .sum(axis=1)
                .sort_values(ascending=False)
            )
            included_ids = n_matches[n_to_exclude:].index
            print(
                "Excluded participants:",
                participants.loc[n_matches[:n_to_exclude].index, "name"].to_list(),
            )
            participants = participants.loc[included_ids]

    # ==================================================================================
    # Algorithm: Optimization using random sampling
    # ==================================================================================

    rng = np.random.default_rng(seed)

    list_of_matchings = draw_candidate_matchings(
        participants=participants, min_size=min_size, n_draws=n_draws, rng=rng
    )

    optimal_matching = find_optimal_matching(
        candidates=list_of_matchings,
        matchings_history=matchings_history,
        penalty_func=penalty_func,
        faculty_multiplier=faculty_multiplier,
        assortative_matching=assortative_matching,
    )

    # ==================================================================================
    # Prepare results
    # ==================================================================================

    updated_history = update_matchings_history(matchings_history, optimal_matching)

    matching_str_repr = format_matching_as_str(optimal_matching)

    if output_path is not None:
        write_matchings_history(
            history=updated_history, path=output_path, overwrite=overwrite
        )
        write_matching(text=matching_str_repr, path=output_path, overwrite=overwrite)

    if return_results:
        results = {
            "matching_str": matching_str_repr,
            "matching": optimal_matching,
            "updated_history": updated_history,
        }
        return results


def _add_new_individuals(matchings_history, names):
    """Add new individuals to matchings_history data frame.

    Args:
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        names (pd.DataFrame): names.csv file converted to pd.DataFrame

    Returns:
        updated (pd.DataFrame): Like matchings_history but with new individuals.

    """
    matchings_history_id = matchings_history.index.values
    names_id = names["id"].values

    new_ids = np.setdiff1d(names_id, matchings_history_id)

    n_new = len(new_ids)
    n_old = len(matchings_history)

    if n_new == 0:
        updated = matchings_history.copy()
    else:
        updated = np.zeros((n_old + n_new, n_old + n_new), dtype=int)
        updated[:n_old, :n_old] = matchings_history.values
        updated = pd.DataFrame(
            updated,
            index=names_id,
            columns=names_id,
        )

    return updated
