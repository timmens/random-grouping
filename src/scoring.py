import numpy as np
import pandas as pd


def score(grouping_matrix, penalty_func):
    """Score grouping matrix.

    Args:
        grouping_matrix (pd.DataFrame):
        penalty_func (callable):
    
    Returns:
        score (float):

    """
    values = grouping_matrix.values
    tril = np.tril(values).flatten()
    
    unique_values = np.unique(tril)
    counts = np.bincount(tril)

    score = np.sum(counts * penalty_func(unique_values))
    return score
