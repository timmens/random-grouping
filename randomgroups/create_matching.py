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
    n_candidates=1_000,
    matching_params=None,
    seed=0,
    return_results=False,
    overwrite=True,
):
    """Create matching.

    Args:
        names_path (str or pathlib.Path): Local path to or URL of names data file.
        matchings_history_path (str or pathlib.Path): Path to matchings history file.
        output_path (str or pathlib.Path): Output path. If None output is not written.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to try during loss minimization.
        matching_params (dict): Parameters that govern the behavior of the matching
            criterion. Default None. For detais see ``_add_defaults_params``.
        seed (int): Seed from which to start the seed generator.
        return_results (bool): Indicates whether the results should be returned.
        overwrite (bool): Whether to check for overwrite of files.

    Returns:
        if return_results is True, returns dictionary with entries:
        - best_matching_str (str)
        - best_matching (list)
        - updated_history (pd.DataFrame)

    """
    if output_path is None and return_results is False:
        raise ValueError(
            "No output path is given and return_results is set to False. Please"
            "either pass a valid output path or set return_results to True."
        )

    matching_params = _add_default_params(matching_params)

    names = read_names(names_path)
    matchings_history = read_or_create_matchings_history(matchings_history_path, names)

    matchings_history = _add_new_individuals(matchings_history, names)

    participants = names.query("joins == 1").set_index("id")
    participants = participants.convert_dtypes()
    if not participants.index.is_unique:
        raise ValueError("ID column in names csv-file is not unique.")
    if len(participants) < min_size:
        raise ValueError("There are less participants than 'min_size'.")

    #  we first draw many 'candidate' matchings that do not consider any criterion; then
    #  we filter out the matching that best fulfills the required criteria
    candidates = draw_candidate_matchings(participants, min_size, n_candidates, seed)
    best_matching = find_best_matching(candidates, matchings_history, matching_params)

    updated_history = update_matchings_history(matchings_history, best_matching)

    best_matching_str = format_matching_as_str(best_matching)
    if output_path is not None:
        write_matchings_history(updated_history, output_path, overwrite)
        write_matching(best_matching_str, output_path, overwrite)

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
