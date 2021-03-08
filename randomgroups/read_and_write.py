from pathlib import Path

import click
import numpy as np
import pandas as pd


def read_names(names_file_path, names_file_url):
    """Read names file.

    Reads names file if stored locally and downloads it if url is given instead.

    Args:
        names_file_path (str or pathlib.Path): File to names data file.
        names_file_url (str or pathlib.Path): URL of names data file.

    Returns:
        names (pd.DataFrame): df with columns 'id'(int), 'names'(str) and 'joins'(0/1).

    """
    if names_file_path is None:
        if names_file_url is None:
            raise ValueError(
                "Both arguments 'names_file_path' and 'names_file_url' are None."
                "Please enter a valid path to the names data file."
            )
        else:
            raise NotImplementedError(
                "Downloading of names data file is not implemented yet."
            )
    else:
        if names_file_url is None:
            names = pd.read_csv(names_file_path)
        else:
            raise ValueError(
                "Both arguments 'names_file_path' and 'names_file_url' are *not* "
                "None. Please enter only one path to the names data file."
            )
    return names


def read_or_create_matchings_history(matchings_history_path, names):
    """Read or create matchings history.

    If matchings history file exists read if not create using names data frame.

    Args:
        matchings_history_path (str or pathlib.Path): Path to matchings_history file.
        names (pd.DataFrame): df with columns 'id'(int), 'names'(str) and 'joins'(0/1).

    Returns:
        matchings_history (pd.DataFrame): df with columns and rows equal to the 'id'
            column in names df (see func ``read_names``). Cell entries represent number
            meetings of the row individual with the column indidivual.

    """
    p = Path(matchings_history_path)

    if p.is_file():
        matchings_history = pd.read_csv(p, index_col="id", header=0, dtype=int)
        matchings_history.columns.name = "id"
        matchings_history.columns = matchings_history.columns.astype(int)
    else:
        matchings_history = _create_matchings_history(names)

    return matchings_history


def write_matchings_history(updated_history, output_path):
    """Write matchings history to file.

    Args:
        updated_history (pd.DataFrame): Updated matchings history.
        output_path (str or pathlib.Path): Output path.

    Returns:
        None

    """
    p = Path(output_path) / "updated_matchings_history.csv"
    if p.is_file():
        fname = click.prompt(
            f"File {p} exists. Please enter other name or nothing to overwrite.",
            type=str,
        )
        fname = fname if len(fname) > 0 else "updated_matchings_history.csv"
        p = output_path / fname
    updated_history.to_csv(p)


def write_matching(best_matching, names, output_path):
    """Write single matching to file.

    Args:
        best_matching (list): Matching returned by func algorithm.find_best_matching
        names (pd.DataFrame): Names data frame.
        output_path (str or pathlib.Path): Output path.

    Returns:
        None

    """
    p = Path(output_path) / "matching.txt"
    if p.is_file():
        fname = click.prompt(
            f"File {p} exists. Please enter other name or nothing for overwrite.",
            type=str,
        )
        fname = fname if len(fname) > 0 else "matching.txt"
        p = output_path / fname

    text = _format_matching_as_str(best_matching, names)
    write_file(text, p)


def _create_matchings_history(names):
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


def write_file(to_write, path):
    """Write string to path.

    Args:
        to_write (str): String which we want to write to path.
        path (str or pathlib.Path): Filepath to write to.

    Returns:
        None

    """
    with open(path, "w") as f:
        f.write(to_write)


def _format_matching_as_str(matching, names):
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
