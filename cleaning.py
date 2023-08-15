from typing import Tuple
import pandas as pd
from scipy.stats import zscore
import warnings
import math
from config import SETTINGS


def removeOutliers(data: pd.DataFrame, sampleName: str, commentName: str = "outlier_cycles", limitHi: bool = False, limitLow: bool = False) -> Tuple[pd.Series, pd.DataFrame]:
    """
    remove any invalid cycles, or ones which contain outliers in any ratio

    Invalid cycles are those with values beyond the limits set in the settings file.
    Outliers are defined as any value greater than 3 standard deviations away from the mean.

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing mass spectrometry data
    sampleName: str
      the identifier of the sample being cleaned
    commentName: str
      The column name giving the number of cycles removed. Defaults to "outlier_cycles"
    limitHi: bool
      Whether to discard cycles above the limit given in the settings file
    limitLow: bool
      Whether to discard cycles below the limit given in the settings file

    Returns
    -------
    dataClean: Pandas.DataFrame
      The cleaned data
    comments: Pandas.Series
      a record of the number of rows dropped
    """
    
    # Use one column as an indication of ablation efficiency and data quality
    metric: pd.Series = data[SETTINGS.low_signal_metric]
    isOverHiLimit:   pd.Series = metric < -math.inf # default to allow everything (always false)
    isUnderLowLimit: pd.Series = metric >  math.inf # default to allow everything (always false)
    if limitHi:
      isOverHiLimit = metric > SETTINGS.blank_upper_limit # true where upper limit is broken
    if limitLow:
      isUnderLowLimit = metric < SETTINGS.low_signal_level # true where lower limit is broken
    
    limitedData: pd.DataFrame = data.loc[~(isOverHiLimit | isUnderLowLimit), :]  # exclude where either limit is broken
    
    # remove outliers
    isOutlier: pd.DataFrame = limitedData[SETTINGS.intensity_cols].apply(zscore).apply(abs) > 3
    hasOutliers: pd.Series = isOutlier.any(axis=1)
    
    # .copy() to avoid pandas SettingWithCopyWarning
    dataClean = limitedData.copy().loc[~hasOutliers, :]

    comments = pd.Series({
        commentName: len(data) - len(dataClean)
    })

    if len(dataClean) < len(data)*SETTINGS.low_cycles_warning_frac:
        warnings.warn(f'Removing outliers and invalid data left only {len(dataClean)} cycles in {sampleName}')

    return comments, dataClean
