from pathlib import Path
from typing import List, Set

import click
import numpy as np
import pandas as pd


# ======================================================================================
# Reading of data
# ======================================================================================


def read_names(path: Path) -> pd.DataFrame:
    """Read names file.

    Reads names file if stored locally and downloads it if url is given instead. This
    expects that the file is directly downloadable from the url. For example, if you
    want to download a google sheet you have to publish the document in the file
    settings of the google to get a "direct-download" link.

    Args:
        path (pathlib.Path): File path to (or URL of) names data file.

    Returns:
        pd.DataFrame: data frame with columns
        - 'id' (int): Unique identifier of individual.
        - 'names' (str): Name of individual.
        - 'joins' {0, 1}: Whether individual joins the matching.
        - 'status' {student, faculty}: Status of individual.
        - 'wants_mixing' {0, 1}: Whether individual prefers to stay in its status group.

    """
    file_type_to_pandas_func = {
        "xls": "excel",
        "xlsx": "excel",
        "dta": "stata",
    }

    file_type = path.suffix[1:]
    read_file = getattr(pd, f"read_{file_type}", None)

    if read_file is None:
        # Try to get read_xxx function for non-standard file types.
        func_name = f"read_{file_type_to_pandas_func.get(file_type, '')}"
        read_file = getattr(pd, func_name, None)

    if read_file is None:
        raise ValueError(
            f"Error in reading names file from path {path}. File type {file_type} is"
            "not supported. Please use a file format supported by pandas' read_xxx "
            "functions."
        )

    names_df = read_file(path)
    return names_df


def read_or_create_matchings_history(
    names: pd.DataFrame = None, path: Path = None
) -> pd.DataFrame:
    """Read or create matchings history.

    If matchings history file exists read, if not create using names data frame.

    Args:
        names (pd.DataFrame): Data frame containing names and ids.
        path (pathlib.Path): Path to matchings_history file.

    Returns:
        pd.DataFrame: data frame with columns and rows equal to the 'id' column in names
        Cell entries represent the number of meetings of the row individual with the
        column individual.

    """
    if path is None:
        matchings_history = _create_matchings_history(names)
    else:
        matchings_history = pd.read_csv(path, index_col=0, header=0, dtype=int)
        matchings_history.columns = matchings_history.columns.astype(int)

    return matchings_history


# ======================================================================================
# Writing of data
# ======================================================================================


def write_matchings_history(
    history: pd.DataFrame, path: Path, overwrite: bool = False
) -> None:
    """Write matchings history to file.

    Args:
        history (pd.DataFrame): Updated matchings history.
        path (pathlib.Path): Output path.
        overwrite (bool): If True, overwrite existing files, otherwise ask for new name.

    """
    file_path = path.joinpath("updated_matchings_history.csv")

    if not overwrite and file_path.is_file():
        file_name = _ask_for_new_file_name(
            existing_file=file_path, default="updated_matchings_history.csv"
        )
        file_path = path.joinpath(file_name).with_suffix(".csv")

    history.to_csv(file_path)


def write_matching(text: str, path: Path, overwrite: bool = False) -> None:
    """Write single matching to file.

    Args:
        text (str): Formatted matching as str.
        path (pathlib.Path): Output path.
        overwrite (bool): If True, overwrite existing files, otherwise ask for new name.

    """
    file_path = path.joinpath("matching.txt")

    if not overwrite and file_path.is_file():
        file_name = _ask_for_new_file_name(
            existing_file=file_path, default="matching.txt"
        )
        file_path = path.joinpath(file_name).with_suffix(".txt")

    file_path.write_text(text)


# ======================================================================================
# Helper functions
# ======================================================================================


def _ask_for_new_file_name(existing_file: Path, default: str) -> str:
    """Ask for new file name via click prompt.

    Args:
        existing_file (pathlib.Path): Path to existing file.
        default (str): Default new file name.

    Returns:
        str: New file name.

    """
    new_file_name = click.prompt(
        f"File {existing_file} exists. Please "
        f"enter other name or nothing to overwrite.",
        type=str,
        default=default,
    )
    return new_file_name


def _create_matchings_history(names: pd.DataFrame) -> pd.DataFrame:
    """Create first instance of matchings history using names data frame.

    Args:
        names (pd.DataFrame): Data frame containing names and ids.

    Returns:
        pd.DataFrame: Matching history corresponding to names data frame.

    """
    matchings_history = pd.DataFrame(
        np.zeros((len(names), len(names)), dtype=int),
        columns=names.id.values,
        index=names.id.values,
    )
    return matchings_history


def format_matching_as_str(
    matching: List[pd.DataFrame], excluded_participants: Set[str]
) -> str:
    """Format matching in human readable string.

    Args:
        matching (List[pd.DataFrame]): Matching.
        excluded_participants (set[str]): Set of excluded participants.

    Returns:
        str: The formatted text as string.

    """
    texts = [", ".join(group.name.values) for group in matching]
    formatted = ""
    for k, text in enumerate(texts):
        formatted += f"Group {k}: {text}\n"

    if len(excluded_participants) > 0:
        excluded_str = f"Excluded participants: {', '.join(excluded_participants)}"
        formatted = formatted + "\n" + excluded_str

    return formatted
