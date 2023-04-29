import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional, Dict

from randomgroups.algorithm import draw_candidate_matchings
from randomgroups.algorithm import find_optimal_matching
from randomgroups.algorithm import update_matchings_history
from randomgroups.algorithm import update_min_size_using_n_groups
from randomgroups.algorithm import get_number_of_excluded_participants
from randomgroups.io import format_matching_as_str
from randomgroups.io import read_names
from randomgroups.io import read_or_create_matchings_history
from randomgroups.io import write_matching
from randomgroups.io import write_matchings_history


def create_matching(
    names_path: Union[str, Path],
    matchings_history_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    min_size: int = 2,
    n_groups: Optional[int] = None,
    max_size: Optional[int] = None,
    penalty_func: callable = np.exp,
    mixing_multiplier: Union[float, Dict[str, float]] = 3.0,
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
        n_groups (int or None): Number of groups to create.
            If None, min_size is used to determine the number of groups.
        max_size (int or None): Setting a maximal group size can lead to participants
            being excluded (the participants with the most matchings in history file).
            If None, no maximum size is enforced.
        penalty_func (callable): Penalty function, defaults to np.exp. Is applied to
            punish large values in matchings_history.
        mixing_multiplier (float, Dict[str, float]): Multiplier determining how many
            members of different status want to stay in the same group. Positive values
            favor assortative matchings, negative values favor mixed matchings. Can be
            a dict with statuses as keys and can only be used if
            assortative_matching is True.
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
    matchings_history_path = (
        None if matchings_history_path is None else Path(matchings_history_path)
    )
    output_path = None if output_path is None else Path(output_path)

    test_penalties = penalty_func(np.array([1, 2]))
    if not isinstance(test_penalties, np.ndarray) or len(test_penalties) != 2:
        raise ValueError(
            "penalty_func must return a numpy array of the same length as the input "
            "array."
        )

    if max_size is not None and min_size > max_size:
        raise ValueError(
            f"min_size ({min_size}) must be smaller than max_size ({max_size})."
        )

    # ==================================================================================
    # Read and verify data
    # ==================================================================================

    names = read_names(names_path)

    all_participants = names.query("joins == 1").set_index("id")
    all_participants = all_participants.convert_dtypes()

    if not all_participants.index.is_unique:
        raise ValueError("id column in names table is not unique.")
    if len(all_participants) < min_size:
        raise ValueError("There are less participants than 'min_size'.")

    if assortative_matching:
        # check if group has at least one or more statuses
        statuses_columns = [col for col in names.columns if "status" in col]
        if len(statuses_columns) == 0:
            raise ValueError(
                "Assortative matching is requested but 'status' column is not "
                "present in names table."
            )

        # check if mixing_multiplier is valid
        if isinstance(mixing_multiplier, (float, int)):
            mixing_multiplier = {
                status: mixing_multiplier for status in statuses_columns
            }
        elif set(mixing_multiplier.keys()) != set(statuses_columns):
            raise ValueError(
                "'mixing_multiplier' must be a float or a dict with keys "
                "equal to the statuses."
            )

        # check if wants_mixing column is specified
        # if not, assume that no-one wants mixing
        # (otherwise one should set assortative_matching=False)
        if "wants_mixing" not in all_participants.columns:
            all_participants["wants_mixing"] = 0

    matchings_history = read_or_create_matchings_history(
        names=names,
        path=matchings_history_path,
    )
    matchings_history = _add_new_individuals(
        matchings_history=matchings_history,
        names=names,
    )

    # ==================================================================================
    # Consolidate group size options
    # ==================================================================================

    if n_groups is not None:
        updated_min_size = update_min_size_using_n_groups(
            min_size=min_size,
            n_groups=n_groups,
            n_participants=len(all_participants),
        )
    else:
        updated_min_size = min_size

    if max_size is not None:
        n_to_exclude, requires_consolidation = get_number_of_excluded_participants(
            min_size=updated_min_size,
            max_size=max_size,
            n_groups=n_groups,
            n_participants=len(all_participants),
        )

        if requires_consolidation:
            updated_min_size = update_min_size_using_n_groups(
                min_size=min_size,
                n_groups=n_groups,
                n_participants=len(all_participants) - n_to_exclude,
            )
    else:
        n_to_exclude = 0

    # ==================================================================================
    # Exclude participants if necessary
    # ==================================================================================

    participants = _exclude_participants_with_most_matchings(
        all_participants,
        matchings_history=matchings_history,
        n_to_exclude=n_to_exclude,
    )

    excluded_participants = set(all_participants.name) - set(participants.name)

    # ==================================================================================
    # Algorithm: Optimization using random sampling
    # ==================================================================================

    rng = np.random.default_rng(seed)

    list_of_matchings = draw_candidate_matchings(
        participants=participants,
        min_size=updated_min_size,
        n_draws=n_draws,
        rng=rng,
    )

    optimal_matching = find_optimal_matching(
        candidates=list_of_matchings,
        matchings_history=matchings_history,
        penalty_func=penalty_func,
        mixing_multiplier=mixing_multiplier,
        assortative_matching=assortative_matching,
    )

    # ==================================================================================
    # Prepare results
    # ==================================================================================

    updated_history = update_matchings_history(matchings_history, optimal_matching)

    matching_str_repr = format_matching_as_str(
        matching=optimal_matching,
        excluded_participants=excluded_participants,
    )

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


def _exclude_participants_with_most_matchings(
    participants: pd.DataFrame, matchings_history: pd.DataFrame, n_to_exclude: int
) -> pd.DataFrame:
    """Subset participants to match group size and number of groups.

    Args:
        participants (pd.DataFrame): DataFrame containing participant information.
        matchings_history (pd.DataFrame): Square df containing group information. Index
            and column is given by the 'id' column in src/data/names.csv.
        n_to_exclude (int): Number of participants to exclude.

    Returns:
        pd.DataFrame: Updated participants DataFrame.

    """
    if n_to_exclude > 0:
        all_matches = matchings_history.sum(axis=0)
        matches = all_matches.loc[participants.index]
        # exclude participants with most matchings
        to_include = matches.sort_values(ascending=False).index[n_to_exclude:]
        participants = participants.loc[to_include]

    return participants
