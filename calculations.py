import pandas as pd

def reducePb(data: pd.DataFrame, sampleInfo: pd.Series) -> dict:
  """
  Data reduction for a single sample

  Calculate ratios and associated errors from multiple time-resolved analyses of a single sample.

  Parameters
  ----------
  data: Pandas.DataFrame
    The DataFrame containing internally corrected mass spectrometry data
  sampleInfo: Pandas.Series
    A series containing the name and type (standard/control/sample) of the observation
  
  Returns
  -------
  a Pandas.Series summary of the input data
  """
  
  # calculate ratios
  Pb6_4 = data["206Pb"]/data["204Pb"]
  Pb7_4 = data["207Pb"]/data["204Pb"]
  Pb8_4 = data["208Pb"]/data["204Pb"]
  Pb7_6 = data["207Pb"]/data["206Pb"]
  Pb8_6 = data["208Pb"]/data["206Pb"]

  # save ratios and standard errors
  ratios = dict({
    "sample_name": sampleInfo.sample_name.item(),
    "type": sampleInfo.type.item(),
    "Pb6_4": Pb6_4.mean(),
    "Pb6_4_err": Pb6_4.sem(ddof=0),
    "Pb7_4": Pb7_4.mean(),
    "Pb7_4_err": Pb7_4.sem(ddof=0),
    "Pb8_4": Pb8_4.mean(),
    "Pb8_4_err": Pb8_4.sem(ddof=0),
    "Pb7_6": Pb7_6.mean(),
    "Pb7_6_err": Pb7_6.sem(ddof=0),
    "Pb8_6": Pb8_6.mean(),
    "Pb8_6_err": Pb8_6.sem(ddof=0),
    "Pb8_int": data["208Pb"].mean()
  })

  return ratios