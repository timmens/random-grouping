import numpy as np
import pandas as pd
import yaml


def read_names_df(path):
    """To be written."""
    names = pd.read_csv(path)
    return names


def read_config_kwargs(path):
    """To be written."""
    with open(path) as f:
        kwargs = yaml.load(f, Loader=yaml.FullLoader)
    return kwargs


def read_grouping_df(path, names):
    """To be written."""
    if not path.is_file():
        grouping_df = create_grouping_df(names)
    else:
        grouping_df = pd.read_csv(path, index_col="id", header=0, dtype=int)
        grouping_df.columns.name = "id"
        grouping_df.columns = grouping_df.columns.astype(int)
    return grouping_df


def create_grouping_df(names):
    """To be written."""
    id_ = names["id"]
    n = len(id_)
    grouping = pd.DataFrame(np.zeros((n, n), dtype=int), columns=id_, index=id_)
    return grouping


def update_grouping_df_file(updated_grouping_df, path):
    """To be written."""
    updated_grouping_df.to_csv(path)


def write_pick(pick, names, path):
    """To be written."""
    path.parent.mkdir(parents=True, exist_ok=True)

    names = names.set_index("id")
    texts = [", ".join(names["name"].loc[group].values) for group in pick]

    text = ""
    for k, text_ in enumerate(texts):
        text += f"Group {k}: {text_}\n"

    with open(path, "w") as f:
        f.write(text)
