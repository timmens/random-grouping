import pytask

from src.algorithm import draw_candidate_matchings
from src.algorithm import find_best_matching
from src.config import BLD
from src.config import SRC
from src.read_and_write import read_config
from src.read_and_write import read_matchings_history
from src.read_and_write import read_names
from src.read_and_write import write_file


def format_matching_as_str(matching, names, path):
    """Format matching in human readable string.

    Args:
        matching (list): Matching in list form. (BETTER EXPLAINATION)
        names (pd.DataFrame): names df, see func ``read_names``
        path (pathlib.Path): Filepath to write to.

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

    participants = get_participants(names)

    candidates = draw_candidate_matchings(participants, config)
    updated_history, best_matching = find_best_matching(candidates, matchings_history)

    updated_history.to_csv(produces[0])

    text = format_matching_as_str(best_matching, names)
    write_file(text, produces[1])
