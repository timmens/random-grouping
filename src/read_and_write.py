import pandas as pd
import yaml

from src.config import CONFIG
from src.config import SRC


def read_names():
    """Read names file.

    Reads names file if stored locally and downloads it if url is given instead.

    Returns:
        names (pd.DataFrame): df with columns 'id'(int), 'names'(str) and 'joins'(0/1).

    """
    config = read_config()
    stored_locally = config["is_names_file_stored_local"]
    link = config["names_file_url"]  # noqa: F841

    if stored_locally:
        names = pd.read_csv(SRC / "data" / "names.csv")
    else:
        raise NotImplementedError("Download of names.csv file is not implemented yet.")

    return names


def read_config():
    """Read config file.

    Is located at root of project and contains parameters for the algorithm.

    Returns:
        config (dict): Configuration dictionary. See file ``config.yaml``.

    """
    with open(CONFIG) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def read_matchings_history():
    """Read matchings history.

    Returns:
        matchings_history (pd.DataFrame): df with columns and rows equal to the 'id'
            column in names df (see func ``read_names``). Cell entries represent number
            meetings of the row individual with the column indidivual.

    """
    p = SRC / "data" / "matchings_history.csv"
    matchings_history = pd.read_csv(p, index_col="id", header=0, dtype=int)
    matchings_history.columns.name = "id"
    matchings_history.columns = matchings_history.columns.astype(int)
    return matchings_history


def write_matching_to_txt(matching, names, path):
    """Write (group) matching to txt file.

    Writes group matching in human readable form.

    Args:
        matching (list): Matching in list form. (BETTER EXPLAINATION)
        names (pd.DataFrame): names df, see func ``read_names``
        path (pathlib.Path): Filepath to write to.

    Returns:
        None

    """
    names = names.set_index("id").copy()
    texts = [", ".join(names["name"].loc[group].values) for group in matching]

    text = ""
    for k, text_ in enumerate(texts):
        text += f"Group {k}: {text_}\n"

    with open(path, "w") as f:
        f.write(text)
