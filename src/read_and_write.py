from pathlib import Path

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

    if config["matchings_history_path"] is not None:
        config["matchings_history_path"] = Path(config["matchings_history_path"])

    return config


def read_matchings_history():
    """Read matchings history.

    Returns:
        matchings_history (pd.DataFrame): df with columns and rows equal to the 'id'
            column in names df (see func ``read_names``). Cell entries represent number
            meetings of the row individual with the column indidivual.

    """
    config = read_config()
    p = config["matchings_history_path"]
    p = p if p is not None else SRC / "data" / "matchings_history.csv"

    matchings_history = pd.read_csv(p, index_col="id", header=0, dtype=int)
    matchings_history.columns.name = "id"
    matchings_history.columns = matchings_history.columns.astype(int)
    return matchings_history


def write_file(to_write, path):
    """Write string to path.

    Args:
        to_write (str): String which we want to write to path.
        path (pathlib.Path): Filepath to write to.

    Returns:
        None

    """
    with open(path, "w") as f:
        f.write(to_write)
