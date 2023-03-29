import numpy as np
import pandas as pd

from randomgroups.algorithm import draw_candidate_matchings
from randomgroups.algorithm import find_best_matching
from randomgroups.algorithm import update_matchings_history
from randomgroups.read_and_write import format_matching_as_str
from randomgroups.read_and_write import read_names
from randomgroups.read_and_write import read_or_create_matchings_history
from randomgroups.read_and_write import write_matching
from randomgroups.read_and_write import write_matchings_history


def create_matching(
    names_path=None,
    matchings_history_path=None,
    output_path=None,
    min_size=3,
    n_groups=None,
    max_size=None,
    n_candidates=1_000,
    matching_params=None,
    seed=0,
    return_results=False,
):
    """Create matching.

    Args:
        names_path (str or pathlib.Path): Local path to or URL of names data file.
        matchings_history_path (str or pathlib.Path): Path to matchings history file.
        output_path (str or pathlib.Path): Output path. If None output is not written.
        min_size (int): Minimum group size. If None, n_groups is used to determine the number of groups.
        n_groups (int or None): Number of groups to create. If None, min_size is used to determine the number of groups.
        max_size (int or None): Setting a maximal group size can lead to participants being excluded (the participants
            with the most matchings in history file). If None, no maximum size is enforced.
        n_candidates (int): Number of candidate groups to try during loss minimization.
        matching_params (dict): Parameters that govern the behavior of the matching
            criterion. Default None. For details see ``_add_defaults_params``.
        seed (int): Seed from which to start the seed generator.
        return_results (bool): Indicates whether the results should be returned.

    Returns:
        if return_results is True, returns dictionary with entries:
        - best_matching_str (str)
        - best_matching (list)
        - updated_history (pd.DataFrame)

    """
    if output_path is None and return_results is False:
        raise ValueError(
            "No output path is given and return_results is set to False. Please "
            "either pass a valid output path or set return_results to True."
        )

    if min_size is None and n_groups is None:
        raise ValueError(
            "Either min_size or n_groups must be set to determine the minimal size of groups."
        )

    matching_params = _add_default_params(matching_params)

    names = read_names(names_path)
    matchings_history = read_or_create_matchings_history(matchings_history_path, names)

    matchings_history = _add_new_individuals(matchings_history, names)

    participants = names.query("joins == 1").set_index("id")
    participants = participants.convert_dtypes()
    if not participants.index.is_unique:
        raise ValueError("ID column in names csv-file is not unique.")

    # if n_groups is set, we set min_size accordingly to get n_groups
    if n_groups is not None:
        group_min_size = len(participants) // n_groups
        if min_size is not None and min_size > group_min_size:
            raise ValueError(
                f"There are not enough participants ({len(participants)}) to create "
                f"{n_groups} groups with at least {min_size} members. "
                "Please decrease n_groups or increase min_size, or set one of them to None."
            )
        else:
            min_size = group_min_size

    # now min_size is set (either by n_groups or by the user)
    if len(participants) < min_size:
        raise ValueError("There are less participants than 'min_size'.")

    # we check if max_size is set
    if max_size is not None:
        # check if max_size is valid
        if max_size < min_size:
            raise ValueError(
                f"max_size ({max_size}) must be greater than min_size ({min_size}). "
                f"This can also happen if n_groups is set too small."
            )
        elif max_size == min_size:
            # check if we need to exclude participants in order to have groups size = max_size
            n_excluded = len(participants) % max_size
            if n_excluded > 0:
                # we exclude those people with most matchings (and first to appear in the name list)
                # this is not optimal with regard to mixing people
                n_matches = matchings_history.loc[participants.index].sum(axis=1).sort_values(ascending=False)
                included_ids = n_matches[n_excluded:].index
                print('Excluded participants:', participants.loc[n_matches[:n_excluded].index, 'name'].to_list())
                participants = participants.loc[included_ids]
        else:
            # groups produced by the algorithm will be maximal of size min_size+1
            # only if max_size == min_size we need to do something
            pass

    #  we first draw many 'candidate' matchings that do not consider any criterion; then
    #  we filter out the matching that best fulfills the required criteria
    candidates = draw_candidate_matchings(participants, min_size, n_candidates, seed)
    best_matching = find_best_matching(candidates, matchings_history, matching_params)

    updated_history = update_matchings_history(matchings_history, best_matching)

    best_matching_str = format_matching_as_str(best_matching)
    if output_path is not None:
        write_matchings_history(updated_history, output_path)
        write_matching(best_matching_str, output_path)

    results = None
    if return_results:
        results = {
            "best_matching_str": best_matching_str,
            "best_matching": best_matching,
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
        to_append = pd.DataFrame(np.zeros(n_new, n_old), dtype=int, index=new_ids)
        updated = pd.concat((matchings_history, to_append), axis=0)
        updated = pd.concat((updated, to_append), axis=1)

    return updated


def _add_default_params(matching_params):
    param_names = ["faculty_multiplier"]
    defaults = {
        "faculty_multiplier": 3,
    }

    if matching_params is None:
        matching_params = defaults
    else:
        for param in param_names:
            if param not in matching_params.keys():
                matching_params[param] = defaults[param]

    return matching_params
