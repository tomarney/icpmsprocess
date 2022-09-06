from typing import List
import pandas as pd
import config as c


def internal(data: pd.DataFrame) -> pd.DataFrame:
    """
    Apply internal corrections to a single sample.
    Corrections applies blank correction and accounts for isobaric interference of 204Hg on 204Pb, using 202Hg

    Parameters
    ----------
    data: Pandas.DataFrame
      The DataFrame containing the raw mass spectrometry data
    """
    # extract settings from config
    blankCycles = (1, c.SETTINGS["blank_cycles"])
    signalCycles = (c.SETTINGS["signal_cycles"]
                    ["start"], c.SETTINGS["signal_cycles"]["end"])

    # split data into blank, signal, and washout
    blank = data.loc[blankCycles[0]: blankCycles[1]]
    signal = data.loc[signalCycles[0]: signalCycles[1]]  # detect burn-through?

    # subtract average blank
    signal = signal - blank.mean(axis=0)

    # correct for Hg204 interference
    Hg204 = signal.loc[:, "202Hg"] * c.CONST["Hg_4_2"]
    signal["204Pb"] = signal["204Pb"] - Hg204

    return signal


def massBias(data: pd.DataFrame) -> pd.DataFrame:

    # make sure DataFrame has a monotonically increasing int index
    d = data.reset_index()

    # get the indices of all observations on reference standards
    stdIxs = d.loc[d.type.eq("standard")].index

    prevStd = pd.Series()
    res: List[dict] = []

    # iterate over each row as a named Tuple
    for row in d.itertuples():
        if row.type == "standard":
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
          stds = pd.concat([prevStd, nextStd], axis=1).T
          # find their average values
          s = stds.drop(["sample_name", "type"], axis=1).mean(axis=0)

        # get accepted values for reference standard
        v = c.CONST['NIST610']

        # correct for mass bias
        # sampleValue / AverageStandardValue * knownStandardValue
        res.append(
            {
                "sample_name": row.sample_name,
                "type":        row.type,
                "Pb6_4":       row.Pb6_4 / s.Pb6_4 * v["Pb_6_4"],
                "Pb6_4_err":   row.Pb6_4_err,
                "Pb7_4":       row.Pb7_4 / s.Pb7_4 * v["Pb_7_4"],
                "Pb7_4_err":   row.Pb7_4_err,
                "Pb8_4":       row.Pb8_4 / s.Pb8_4 * v["Pb_8_4"],
                "Pb8_4_err":   row.Pb8_4_err,
                "Pb7_6":       row.Pb7_6 / s.Pb7_6 * v["Pb_7_6"],
                "Pb7_6_err":   row.Pb7_6_err,
                "Pb8_6":       row.Pb8_6 / s.Pb8_6 * v["Pb_8_6"],
                "Pb8_6_err":   row.Pb8_6_err
            }
        )
    # END for

    return pd.DataFrame(res)
