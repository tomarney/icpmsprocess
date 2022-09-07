from typing import Tuple
import pandas as pd


def removeNegativeCycles(data: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    """
    remove any cycles where the signal is smaller than the blank

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing mass spectrometry data

    Returns
    -------
    dataClean: Pandas.DataFrame
      The cleaned data
    comments: Pandas.Series
      a record of the number of rows dropped
    """

    negVals = data < 0
    negRows = negVals.any(axis=1)
    # .copy() to avoid pandas SettingWithCopyWarning
    dataClean = data.copy().loc[~negRows, :]

    comments = pd.Series({
        "dropped_cycles_negative": len(data) - len(dataClean)
    })

    return comments, dataClean
