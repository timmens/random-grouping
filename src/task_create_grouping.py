"""Create grouping."""
import numpy as np
import pandas as pd

from src.config import SRC


def create_grouping_matrix():
    path = SRC / "data" / "names.csv" 
    names = pd.read_csv(path)
    id_ = names["id"]
    n = len(id_)
    grouping = pd.DataFrame(np.zeros((n, n)), columns=id_, index=id_)
    return grouping



def read_grouping_matrix():
    path = SRC / "data" / "previous_groupings.csv"
    if path.is_file():
        grouping_matrix = pd.read_csv(path)
    else:
        grouping_matrix = create_grouping_matrix()
    return grouping_matrix
