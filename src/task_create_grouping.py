import os
import yaml

import numpy as np
import pandas as pd

from src.config import SRC
from src.config import BLD
from src.shared import draw_groupings
from src.shared import score_grouping_df
from src.shared import update_grouping_df
from src.shared import pick_best_candidate


def read_names_df(path):
    names = pd.read_csv(path)
    return names


def read_config_kwargs(path):
    with open(path) as f:
        kwargs = yaml.load(f, Loader=yaml.FullLoader)
    return kwargs


def read_grouping_df(path, names):
    if os.stat(path).st_size == 0:
        grouping_df = create_grouping_df(names)
    else:
        grouping_df = pd.read_csv(path, index_col="id", header=0)
        grouping_df.columns.name = "id"
        grouping_df.columns = grouping_df.columns.astype(int)
    return grouping_df


def extract_current_members(names):
    """Extract current members from names data frame.

    Args:
        names (pd.DataFrame): names.csv data file converted to pd.DataFrame
    
    Returns:
        members (pd.Series): Series containing ids of individuals that participate.

    """
    members = names.query("joins == 1")["id"]
    return members


def create_grouping_df(names):
    id_ = names["id"]
    n = len(id_)
    grouping = pd.DataFrame(np.zeros((n, n), dtype=int), columns=id_, index=id_)
    return grouping


def update_grouping_df_file(updated_grouping_df, path):
    updated_grouping_df.to_csv(path)


def write_pick(pick, names, path):
    names = names.set_index("id")
    texts = [", ".join(names["name"].loc[group].values) for group in pick]
    
    text = ""
    for k, text_ in enumerate(texts):
        text += f"Group {k}: {text_}\n"

    with open(path, "w") as f:
        f.write(text)


if __name__ == "__main__":
    depends_on = {
            "config": SRC / "config.yaml",
            "names": SRC / "data" / "names.csv",
            "groupings": SRC / "data" / "previous_groupings.csv",
    }
    produces = BLD / "grouping.txt"

    kwargs = read_config_kwargs(depends_on["config"])

    names = read_names_df(depends_on["names"])
    members = extract_current_members(names)

    grouping_df = read_grouping_df(depends_on["groupings"], names)
    candidates = draw_groupings(members, **kwargs)

    updated_grouping_df, minimum = pick_best_candidate(candidates, grouping_df)

    update_grouping_df_file(updated_grouping_df, depends_on["groupings"])
    write_pick(minimum, names, produces)
