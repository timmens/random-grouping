import numpy as np
from randomgroups.algorithm import (
    _create_chunks,
    _create_candidate_matching,
    _compute_history_score,
    update_matchings_history,
)
import pandas as pd
from collections import namedtuple
from pandas.testing import assert_frame_equal


def test_compute_history_score_no_matchings():
    matchings_history = pd.DataFrame(np.zeros((2, 2), dtype=np.int64))
    got = _compute_history_score(matchings_history, penalty_func=np.exp)
    assert np.allclose(got, 1.0)


def test_compute_history_score_one_matching():
    matchings_history = pd.DataFrame(np.ones((2, 2), dtype=np.int64))
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
    matchings_history = pd.DataFrame(np.zeros((3, 3), dtype=np.int64))
    matching = [
        pd.DataFrame({"name": ["Alice", "Bob"]}, index=[0, 1]),
        pd.DataFrame({"name": ["Jake"]}, index=[2]),
    ]
    expected = pd.DataFrame([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.int64)
    got = update_matchings_history(matchings_history, matching)
    assert_frame_equal(expected, got)
