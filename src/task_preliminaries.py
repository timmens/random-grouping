import numpy as np
import pandas as pd

from src.config import BLD
from src.read_and_write import read_names_df


def create_bld_folder():
    """Create BLD folder structure if not exist."""
    p = BLD / "history"
    p.mkdir(parents=True, exist_ok=True)


def create_matchings_file():
    """Create matching history file if not exist."""
    p = BLD / "matching_history.csv"
    if not p.is_file():
        names = read_names_df()
        df = create_matchings_df(names)
        df.to_csv(p)


def create_matchings_df(names):
    """Create matching history data frame using names df."""
    id_ = names["id"]
    n = len(id_)
    matchings = pd.DataFrame(np.zeros((n, n), dtype=int), columns=id_, index=id_)
    return matchings


def main():  # noqa: D103
    create_bld_folder()
    create_matchings_file()


if __name__ == "__main__":
    main()
