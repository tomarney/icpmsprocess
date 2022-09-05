import pandas as pd

def internal(data: pd.DataFrame, config: dict) -> pd.DataFrame:
  """
  Apply internal corrections to a single sample.
  Corrections applies blank correction and accounts for isobaric interference of 204Hg on 204Pb, using 202Hg

  Parameters
  ----------
  data: Pandas.DataFrame
    The DataFrame containing the raw mass spectrometry data
  """
  # extract settings from config
  blankCycles=(1,config["blank_cycles"])
  signalCycles=(config["signal_cycles"]["start"],config["signal_cycles"]["end"])

  # split data into blank, signal, and washout
  blank = data.loc[blankCycles[0] : blankCycles[1]]
  signal = data.loc[signalCycles[0] : signalCycles[1]] # detect burn-through?

  # subtract average blank
  signal = signal - blank.mean(axis=0)
  
  # correct for Hg204 interference
  Hg204 = signal.loc[:,"202Hg"] * config["Hg204_202_ratio"]
  signal["204Pb"] = signal["204Pb"] - Hg204

  return signal