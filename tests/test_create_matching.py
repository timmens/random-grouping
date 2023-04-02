from randomgroups.create_matching import create_matching, _add_new_individuals
import pandas as pd
from pandas.testing import assert_frame_equal
from pathlib import Path
import numpy as np


TEST_DATA = Path(__file__).parent / "data"


def test_add_new_individuals():
    names = pd.DataFrame({"name": ["a", "b"], "id": [1, 2]})
    matchings_history = pd.DataFrame([[0]], index=[1], columns=[1])
    expected = pd.DataFrame([[0, 0], [0, 0]], index=[1, 2], columns=[1, 2])
    got = _add_new_individuals(matchings_history=matchings_history, names=names)
    assert_frame_equal(expected, got, check_dtype=False)


def test_create_matching_test():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        n_draws=10,
        return_results=True,
    )
    expected_groups = [
        {"Antonia", "Lukas"},
        {"Daniel", "Fabio"},
    ]
    for group in result["matching"]:
        assert set(group.name) in expected_groups


def test_create_matching_test_concave_penalty():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        penalty_func=lambda x: -np.exp(x),
        n_draws=10,
        return_results=True,
    )
    expected_groups = [
        {"Antonia", "Daniel"},
        {"Lukas", "Fabio"},
    ]
    for group in result["matching"]:
        assert set(group.name) in expected_groups
