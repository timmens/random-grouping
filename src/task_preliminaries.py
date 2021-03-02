import numpy as np
import pandas as pd
import pytask

from src.config import SRC
from src.read_and_write import read_names


def create_matchings_history(names):
    """Create first instance of matchings history using names data file.

    Returns:
        matchings_history (pd.DataFrame):

    """
    id_ = names["id"]
    n = len(id_)
    matchings_history = pd.DataFrame(
        np.zeros((n, n), dtype=int), columns=id_, index=id_
    )
    return matchings_history


@pytask.mark.preliminaries
@pytask.mark.produces(SRC / "data" / "matchings_history.csv")
def task_preliminaries(produces):  # noqa: D103
    if not produces.is_file():
        names = read_names()
        matchings_history = create_matchings_history(names)
        matchings_history.to_csv(produces)
