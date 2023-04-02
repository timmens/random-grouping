from randomgroups.io import (
    read_names,
    read_or_create_matchings_history,
    write_matching,
    write_matchings_history,
    _create_matchings_history,
)

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np


# ======================================================================================
# Reading of data
# ======================================================================================


def test_read_names(tmp_path):
    names = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
        }
    )
    names.to_csv(tmp_path.joinpath("names.csv"), index=False)
    got = read_names(path=tmp_path.joinpath("names.csv"))
    assert_frame_equal(names, got, check_dtype=False)


def test_read_names_excel(tmp_path):
    names = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
        }
    )
    names.to_excel(tmp_path.joinpath("names.xlsx"), index=False)
    got = read_names(path=tmp_path.joinpath("names.xlsx"))
    assert_frame_equal(names, got, check_dtype=False)


def test_read_names_invalid_filetype(tmp_path):
    with pytest.raises(ValueError):
        read_names(path=tmp_path.joinpath("names.xyz"))


def test_read_or_create_matchings_history_names():
    names = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
        }
    )
    got = read_or_create_matchings_history(names=names)
    expected = _create_matchings_history(names)
    assert_frame_equal(expected, got, check_dtype=False)


def test_read_or_create_matchings_history_path(tmp_path):
    history = pd.DataFrame(np.arange(4).reshape(2, 2), columns=[1, 2], index=[1, 2])
    history.to_csv(tmp_path.joinpath("matchings_history.csv"))
    got = read_or_create_matchings_history(
        path=tmp_path.joinpath("matchings_history.csv")
    )
    assert_frame_equal(history, got, check_dtype=False)


# ======================================================================================
# Writing of data
# ======================================================================================


def test_write_matchings_history(tmp_path):
    history = pd.DataFrame(np.arange(4).reshape(2, 2), columns=[1, 2], index=[1, 2])
    write_matchings_history(history, path=tmp_path, overwrite=False)
    read = read_or_create_matchings_history(
        path=tmp_path.joinpath("updated_matchings_history.csv")
    )
    assert_frame_equal(history, read, check_dtype=False)


def test_write_matching(tmp_path):
    text = "This is\na test.\n"
    write_matching(text, path=tmp_path, overwrite=False)
    assert tmp_path.joinpath("matching.txt").is_file()
    assert tmp_path.joinpath("matching.txt").read_text() == text


def test_write_matching_overwrite(tmp_path):
    old_text = "This was a test.\n"
    tmp_path.joinpath("matching.txt").write_text(old_text)
    new_text = "This is\na test.\n"
    write_matching(new_text, path=tmp_path, overwrite=True)
    assert tmp_path.joinpath("matching.txt").is_file()
    assert tmp_path.joinpath("matching.txt").read_text() == new_text


def test_write_matching_overwrite_user_input(tmp_path, monkeypatch):
    old_text = "This was a test.\n"
    tmp_path.joinpath("matching.txt").write_text(old_text)
    new_text = "This is\na test.\n"
    monkeypatch.setattr("click.prompt", lambda *args, **kwargs: "new_matching.txt")
    write_matching(new_text, path=tmp_path, overwrite=False)
    assert tmp_path.joinpath("new_matching.txt").is_file()
    assert tmp_path.joinpath("new_matching.txt").read_text() == new_text


# ======================================================================================
# Helper functions
# ======================================================================================


def test_format_matching_as_str():
    pass


def test_create_matchings_history():
    names = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
        }
    )
    expected = pd.DataFrame(np.zeros((2, 2), dtype=int), columns=[1, 2], index=[1, 2])
    got = _create_matchings_history(names)
    assert_frame_equal(expected, got)
