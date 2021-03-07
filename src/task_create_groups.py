import numpy as np
import pandas as pd
import pytask

from src.algorithm import draw_candidate_matchings
from src.algorithm import find_best_matching
from src.algorithm import update_matchings_history
from src.config import BLD
from src.config import SRC
from src.read_and_write import read_config
from src.read_and_write import read_matchings_history
from src.read_and_write import read_names
from src.read_and_write import write_file


def format_matching_as_str(matching, names):
    """Format matching in human readable string.

    Args:
        matching (list): Matching in list form. (BETTER EXPLAINATION)
        names (pd.DataFrame): names df, see func ``read_names``

    Returns:
        text (str): The formatted text as string.

    """
    names = names.set_index("id").copy()
    texts = [", ".join(names["name"].loc[group].values) for group in matching]

    text = ""
    for k, text_ in enumerate(texts):
        text += f"Group {k}: {text_}\n"

    return text


def get_participants(names):
    """Extract current participants from names data frame.

    Args:
        names (pd.DataFrame): names.csv file converted to pd.DataFrame

    Returns:
        participants (pd.Series): Series containing ids of individuals that will join.

    """
    participants = names.query("joins == 1")["id"]
    return participants


def add_new_individuals(matchings_history, names):
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


@pytask.mark.build
@pytask.mark.depends_on(SRC / "data" / "matchings_history.csv")
@pytask.mark.produces(
    [
        BLD / "matchings_history.csv",
        BLD / "matching.txt",
    ]
)
def task_create_matchings(depends_on, produces):  # noqa: D103
    config = read_config()
    names = read_names()
    matchings_history = read_matchings_history()

    matchings_history = add_new_individuals(matchings_history, names)
    participants = get_participants(names)

    candidates = draw_candidate_matchings(
        participants, config["min_size"], config["n_candidates"], config["initial_seed"]
    )
    best_matching = find_best_matching(candidates, matchings_history)

    updated_history = update_matchings_history(matchings_history, best_matching)
    updated_history.to_csv(produces[0])

    text = format_matching_as_str(best_matching, names)
    write_file(text, produces[1])
