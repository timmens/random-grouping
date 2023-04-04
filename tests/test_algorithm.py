import numpy as np
import pytest
from randomgroups.algorithm import (
    _create_chunks,
    _create_candidate_matching,
    _compute_history_score,
    update_matchings_history,
    update_min_size_using_n_groups,
    get_number_of_excluded_participants,
)
import pandas as pd
from collections import namedtuple
from pandas.testing import assert_frame_equal


def test_compute_history_score_no_matchings():
    matchings_history = pd.DataFrame(np.zeros((2, 2), dtype=int))
    got = _compute_history_score(matchings_history, penalty_func=np.exp)
    assert np.allclose(got, 1.0)


def test_compute_history_score_one_matching():
    matchings_history = pd.DataFrame(np.ones((2, 2), dtype=int))
    got = _compute_history_score(matchings_history, penalty_func=np.exp)
    assert np.allclose(got, np.exp(1.0))


def test_compute_history_score():
    matchings_history = pd.DataFrame(
        [
            [0, 2, 1],
            [2, 0, 0],
            [1, 0, 0],
        ]
    )
    got = _compute_history_score(matchings_history, penalty_func=lambda x: x)
    assert np.allclose(got, 3.0)


def test_create_chunks():
    ids = np.arange(10)
    got = _create_chunks(ids, min_size=3)
    expected = [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert got == expected


def test_create_candidate_matching():
    participants = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
        },
        index=[0, 1],
    )
    rng = namedtuple("rng", "shuffle")(shuffle=lambda x: None)
    matching = _create_candidate_matching(participants, min_size=1, rng=rng)
    assert len(matching) == 2
    assert matching[0].index.values[0] == 0
    assert matching[1].loc[1, "name"] == "Bob"


def test_create_candidate_matching_shuffled():
    participants = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
        },
        index=[0, 1],
    )
    rng = namedtuple("rng", "shuffle")(shuffle=lambda x: np.flip(x))
    matching = _create_candidate_matching(participants, min_size=1, rng=rng)
    assert len(matching) == 2
    assert matching[1].index.values[0] == 1
    assert matching[0].loc[0, "name"] == "Alice"


def test_update_matchings_history():
    matchings_history = pd.DataFrame(np.zeros((3, 3), dtype=int))
    matching = [
        pd.DataFrame({"name": ["Alice", "Bob"]}, index=[0, 1]),
        pd.DataFrame({"name": ["Jake"]}, index=[2]),
    ]
    expected = pd.DataFrame([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=int)
    got = update_matchings_history(matchings_history, matching)
    assert_frame_equal(expected, got, check_dtype=False)


def test_consolidate_min_size_and_n_groups():
    got = update_min_size_using_n_groups(min_size=2, n_groups=2, n_participants=5)
    assert got == 2


def test_consolidate_min_size_and_n_groups_invalid():
    with pytest.raises(ValueError, match="There are not enough participants"):
        update_min_size_using_n_groups(min_size=3, n_groups=2, n_participants=4)


def test_get_number_of_excluded_participants_no_exclusion():
    got = get_number_of_excluded_participants(
        min_size=2,
        max_size=3,
        n_groups=2,
        n_participants=5,
    )
    assert got == (0, False)


def test_get_number_of_excluded_participants_with_exclusion():
    got = get_number_of_excluded_participants(
        min_size=2,
        max_size=2,
        n_groups=2,
        n_participants=5,
    )
    assert got == (1, True)


def test_get_number_of_excluded_participants_equal_max_min():
    got = get_number_of_excluded_participants(
        min_size=2,
        max_size=2,
        n_groups=None,
        n_participants=5,
    )
    assert got == (1, False)
