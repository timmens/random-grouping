from pathlib import Path

import click
import numpy as np
import pandas as pd


def read_names(names_path, file_type="csv"):
    """Read names file.

    Reads names file if stored locally and downloads it if url is given instead. This
    exepects that the file is directly downloadable from the url. For example, if you
    want to download a google sheet you have to publish the document in the file
    settings of the google to get a "direct-download" link.

    Args:
        names_path (str or pathlib.Path): File path to or URL of names data file.
        file_type (str): File type. Default csv. Currently supported: ["csv", "xlsx"].

    Returns:
        names (pd.DataFrame): df with columns 'id'(int), 'names'(str), 'joins'(0/1),
            'status'(student/faculty) and 'wants_mixing'(0/1).

    """
    if names_path is None:
        raise ValueError(
            "Argument 'names_path' is None. Please pass a valid names path."
        )
    if file_type in ("excel", "xlsx"):
        file_type = "excel"
    read_file = getattr(pd, f"read_{file_type}")
    names = read_file(names_path)
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
    if matchings_history_path is None:
        matchings_history = _create_matchings_history(names)
    else:
        matchings_history = pd.read_csv(
            matchings_history_path, index_col="id", header=0, dtype=int
        )
        matchings_history.columns.name = "id"
        matchings_history.columns = matchings_history.columns.astype(int)

    return matchings_history


def write_matchings_history(updated_history, output_path, overwrite=False):
    """Write matchings history to file.

    Args:
        updated_history (pd.DataFrame): Updated matchings history.
        output_path (str or pathlib.Path): Output path.
        overwrite (bool): If False, check if file exists and ask for overwrite.

    Returns:
        None

    """
    output_path = Path(output_path)
    p = output_path / "updated_matchings_history.csv"
    if not overwrite and p.is_file():
        fname = click.prompt(
            f"File {p} exists. Please enter other name or nothing to overwrite.",
            type=str,
            default="",
        )
        fname = fname if len(fname) > 0 else "updated_matchings_history.csv"
        p = (output_path / fname).with_suffix(".csv")
    updated_history.to_csv(p)


def write_matching(text, output_path, overwrite=False):
    """Write single matching to file.

    Args:
        text (str): Formatted matching as str.
        output_path (str or pathlib.Path): Output path.
        overwrite (bool): If False, check if file exists and ask for overwrite.

    Returns:
        text (str): The best matching nicely formatted.

    """
    output_path = Path(output_path)
    p = output_path / "matching.txt"
    if not overwrite and p.is_file():
        fname = click.prompt(
            f"File {p} exists. Please enter other name or nothing for overwrite.",
            type=str,
            default="",
        )
        fname = fname if len(fname) > 0 else "matching.txt"
        p = (output_path / fname).with_suffix(".txt")

    write_file(text, p)
    return None


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


def format_matching_as_str(matching):
    """Format matching in human readable string.

    Args:
        matching (list): Matching in list form.

    Returns:
        text (str): The formatted text as string.

    """
    texts = [", ".join(group["name"].values) for group in matching]
    text = ""
    for k, text_ in enumerate(texts):
        text += f"Group {k}: {text_}\n"
    return text
