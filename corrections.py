from typing import List, Tuple
import warnings
import pandas as pd
import cleaning
from config import SETTINGS, CONST


def internal(data: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Apply internal corrections to a single sample.

    Applies blank correction and accounts for isobaric interference of 204Hg on 204Pb, using 202Hg. Removes outliers from the blank, and removes cycles where the blank is greater than the signal

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing the raw mass spectrometry data

    Returns
    -------
    signal: Pandas.DataFrame
      The internally corrected data
    comments: Pandas.Series
      a record of the number of rows dropped
    """
    # extract settings from config
    blankCycles = (1, SETTINGS.blank_cycles)
    signalCycles = (SETTINGS.signal_cycles[0], SETTINGS.signal_cycles[1])

    # split data into blank, signal, and washout
    blankRaw = data.loc[blankCycles[0]: blankCycles[1]]
    signalRaw = data.loc[signalCycles[0]: signalCycles[1]]  # detect burn-through?

    blankComms, blank = cleaning.removeOutliers(
        blankRaw, commentName="outlier_blank_cycles")

    # subtract average blank
    signal = signalRaw - blank.mean(axis=0)

    # remove any cycles where the signal is smaller than the blank
    sigComms, signalClean = cleaning.removeNegativeCycles(signal)

    # correct for Hg204 interference
    Hg204 = signalClean.loc[:, "202Hg"] * CONST.Hg_4_2
    signalClean.loc[:, "204Pb"] = signalClean.loc[:, "204Pb"] - Hg204

    # combine comments
    comments = pd.concat([blankComms, sigComms])

    return (comments, signalClean)


def massBias(data: pd.DataFrame) -> pd.DataFrame:
    """
    Apply internal corrections to a single sample.
    Corrections applies blank correction and accounts for isobaric interference of 204Hg on 204Pb, using 202Hg

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing the raw mass spectrometry data
    """

    # make sure DataFrame has a monotonically increasing int index
    d = data.reset_index()

    # get the indices of all observations on reference standards
    stdIxs = d.loc[d.type.eq("standard")].index

    prevStd = pd.Series()
    res: List[dict] = []

    # iterate over each row as a named Tuple
    for row in d.itertuples():

        if row.Index > stdIxs[-1]:
            warnings.warn("Ignoring samples or controls after the last standard")
            break
        
        if row.type == "standard":
            # TODO: check if standard values are anomalous, and don't update prevStd if so
            prevStd = pd.Series(row._asdict())  # convert back to a Series
            continue

        # not a standard: treat controls & samples identically.

        if row.Index == len(d)-1:
            # last row and not a standard: don't try and find next standard
            # just use previous standard
            s = prevStd

        else:
            # find the next standard in the run queue
            nextStdIdx = int(stdIxs[stdIxs > row.Index].min())
            nextStd = d.iloc[nextStdIdx]

            # join the two standards
            stds = pd.concat([prevStd, nextStd], axis=1).T.convert_dtypes()
            # find their average values
            s = stds.select_dtypes(include=['number']).mean(axis=0)

        # get accepted values for reference standard
        v = CONST.NIST610

        # correct for mass bias
        # sampleValue / AverageStandardValue * knownStandardValue
        res.append(
            {
                "sample_name": row.sample_name,
                "type":        row.type,
                "Pb6_4":       row.Pb6_4 / s.Pb6_4 * v.Pb_6_4,
                "Pb6_4_err":   row.Pb6_4_err,
                "Pb7_4":       row.Pb7_4 / s.Pb7_4 * v.Pb_7_4,
                "Pb7_4_err":   row.Pb7_4_err,
                "Pb8_4":       row.Pb8_4 / s.Pb8_4 * v.Pb_8_4,
                "Pb8_4_err":   row.Pb8_4_err,
                "Pb7_6":       row.Pb7_6 / s.Pb7_6 * v.Pb_7_6,
                "Pb7_6_err":   row.Pb7_6_err,
                "Pb8_6":       row.Pb8_6 / s.Pb8_6 * v.Pb_8_6,
                "Pb8_6_err":   row.Pb8_6_err,
                "Pb6_7":       row.Pb6_7 / s.Pb6_7 * v.Pb_6_4 / v.Pb_7_4,
                "Pb6_7_err":   row.Pb6_7_err,
                "Pb8_7":       row.Pb8_7 / s.Pb8_7 * v.Pb_8_4 / v.Pb_7_4,
                "Pb8_7_err":   row.Pb8_7_err,
                "Pb4_mean":    row.Pb4_mean, # pass through (no correction)
                "Pb4_mean_err":row.Pbint_err,
                "Pbint":       row.Pbint, # pass through (no correction)
                "Pbint_err":   row.Pbint_err
            }
        )
    # END for

    return pd.DataFrame(res)
