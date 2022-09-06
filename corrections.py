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
  blankCycles=(1,c.SETTINGS["blank_cycles"])
  signalCycles=(c.SETTINGS["signal_cycles"]["start"],c.SETTINGS["signal_cycles"]["end"])

  # split data into blank, signal, and washout
  blank = data.loc[blankCycles[0] : blankCycles[1]]
  signal = data.loc[signalCycles[0] : signalCycles[1]] # detect burn-through?

  # subtract average blank
  signal = signal - blank.mean(axis=0)
  
  # correct for Hg204 interference
  Hg204 = signal.loc[:,"202Hg"] * c.CONST["Hg_4_2"]
  signal["204Pb"] = signal["204Pb"] - Hg204

  return signal