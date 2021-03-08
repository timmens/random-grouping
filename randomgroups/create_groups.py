from src.algorithm import draw_candidate_matchings
from src.algorithm import find_best_matching
from src.algorithm import update_matchings_history
from src.read_and_write import read_names
from src.read_and_write import read_or_create_matchings_history
from src.read_and_write import write_matching
from src.read_and_write import write_matchings_history


def create_groups(
    names_file_path=None,
    names_file_url=None,
    matchings_history_path=None,
    output_path=None,
    min_size=3,
    n_candidates=500,
    return_results=False,
    initial_seed=0,
):
    """Create groupings.

    Args:
        names_file_path (str or pathlib.Path): Local path to names data file.
        names_file_url (str): URL to names data file.
        matchings_history_path (str or pathlib.Path): Path to matchings history file.
        output_path (str or pathlib.Path): Output path.
        min_size (int): Minimum group size.
        n_candidates (int): Number of candidate groups to try during loss minimization.
        initial_seed (int): Seed to pass to the seed generator.

    Returns:
        best_matching (list) and updated_history (pd.DataFrame) if argument
        return_results is True, else None.

    """
    if output_path is None and return_results is False:
        raise ValueError(
            "No output path is given and return_results is set to False. Please"
            "either pass a valid output path or set return_results to True."
        )

    names = read_names(names_file_path, names_file_url)
    matchings_history = read_or_create_matchings_history(matchings_history_path, names)

    participants = get_participants(names)

    candidates = draw_candidate_matchings(
        participants, min_size, n_candidates, initial_seed
    )
    best_matching = find_best_matching(candidates, matchings_history)

    updated_history = update_matchings_history(matchings_history, best_matching)

    write_matchings_history(updated_history, output_path)
    write_matching(best_matching, names, output_path)

    results = (best_matching, updated_history) if return_results else None
    return results


def get_participants(names):
    """Extract current participants from names data frame.

    Args:
        names (pd.DataFrame): names.csv file converted to pd.DataFrame

    Returns:
        participants (pd.Series): Series containing ids of individuals that will join.

    """
    participants = names.query("joins == 1")["id"]
    return participants
