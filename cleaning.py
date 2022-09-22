from typing import Tuple
import pandas as pd
from scipy.stats import zscore


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

    numCols = data.select_dtypes(include=['number']).columns
    negVals = data[numCols] < 0
    negRows = negVals.any(axis=1)
    # .copy() to avoid pandas SettingWithCopyWarning
    dataClean = data.copy().loc[~negRows, :]

    comments = pd.Series({
        "negative_signal_cycles": len(data) - len(dataClean)
    })

    return comments, dataClean



def removeOutliers(data: pd.DataFrame, commentName: str = "outlier_signal_cycles") -> Tuple[pd.Series, pd.DataFrame]:
    """
    remove any cycles which contain outliers in any ratio

    Outliers are defined as any value greater than 2 standard deviations away from the mean.

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing mass spectrometry data
    commentName: str
      The column name giving the number of cycles removed. Defaults to "outlier_signal_cycles"

    Returns
    -------
    dataClean: Pandas.DataFrame
      The cleaned data
    comments: Pandas.Series
      a record of the number of rows dropped
    """

    numCols = data.select_dtypes(include=['number']).copy()
    isOutlier: pd.DataFrame = numCols.apply(zscore).apply(abs) > 2

    hasOutliers = isOutlier.any(axis=1)
    # .copy() to avoid pandas SettingWithCopyWarning
    dataClean = data.copy().loc[~hasOutliers, :]

    comments = pd.Series({
        commentName: len(data) - len(dataClean)
    })

    return comments, dataClean
