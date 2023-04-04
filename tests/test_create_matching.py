from randomgroups.create_matching import (
    create_matching,
    _add_new_individuals,
    _exclude_participants_with_most_matchings,
)
import pandas as pd
from pathlib import Path
import numpy as np
import pytest


def assert_frame_equal(left, right):
    pd.testing.assert_frame_equal(
        left, right, check_dtype=False, check_index_type=False, check_column_type=False
    )


TEST_DATA = Path(__file__).parent.joinpath("data")


# ======================================================================================
# Create Matching
# ======================================================================================


def test_create_matching():
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


def test_create_matching_one_group():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        n_groups=1,
        n_draws=10,
        return_results=True,
    )
    matching = result["matching"]
    assert len(matching) == 1
    assert set(matching[0].name) == {"Antonia", "Daniel", "Fabio", "Lukas"}


def test_create_matching_two_groups():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        n_groups=2,
        n_draws=10,
        return_results=True,
    )
    expected_groups = [
        {"Antonia", "Lukas"},
        {"Daniel", "Fabio"},
    ]
    for group in result["matching"]:
        assert set(group.name) in expected_groups


def test_create_matching_too_few_participants():
    with pytest.raises(ValueError, match="There are not enough participants"):
        create_matching(
            # only 4 participants
            names_path=TEST_DATA.joinpath("names.csv"),
            matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
            min_size=2,
            n_groups=3,
            n_draws=10,
            return_results=True,
        )


def test_create_matching_max_size_exclusion():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        n_groups=1,
        max_size=2,
        n_draws=10,
        return_results=True,
    )
    # Antonia and Daniel need to be excluded (most matches)
    matching = result["matching"]
    assert len(matching) == 1
    assert set(matching[0].name) == {"Fabio", "Lukas"}


def test_create_matching_max_size_no_exclusion():
    result = create_matching(
        names_path=TEST_DATA.joinpath("names.csv"),
        matchings_history_path=TEST_DATA.joinpath("matchings_history.csv"),
        min_size=2,
        max_size=2,
        n_draws=10,
        return_results=True,
    )
    # no one should be excluded since enough people are available
    expected_groups = [
        {"Antonia", "Lukas"},
        {"Daniel", "Fabio"},
    ]
    for group in result["matching"]:
        assert set(group.name) in expected_groups


# ======================================================================================
# Helper functions
# ======================================================================================


def test_add_new_individuals():
    names = pd.DataFrame({"name": ["a", "b"], "id": [1, 2]})
    matchings_history = pd.DataFrame([[0]], index=[1], columns=[1])
    expected = pd.DataFrame([[0, 0], [0, 0]], index=[1, 2], columns=[1, 2])
    got = _add_new_individuals(matchings_history=matchings_history, names=names)
    assert_frame_equal(expected, got)


def test_exclude_participants_with_most_matchings():
    participants = pd.DataFrame({"name": ["a", "b", "c"]}, index=[1, 2, 3])
    matchings_history = pd.DataFrame(
        [[0, 1, 2], [1, 0, 2], [2, 2, 0]], index=[1, 2, 3], columns=[1, 2, 3]
    )
    expected = participants.loc[[1, 2]]
    got = _exclude_participants_with_most_matchings(
        participants=participants, matchings_history=matchings_history, n_to_exclude=1
    )
    assert_frame_equal(expected, got)


def test_exclude_participants_with_most_matchings_no_exclusion():
    got = _exclude_participants_with_most_matchings(
        participants="xyz", matchings_history=None, n_to_exclude=0
    )
    assert got == "xyz"
