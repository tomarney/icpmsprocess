from typing import Tuple
import pandas as pd
import cleaning

def reducePb(data: pd.DataFrame, sampleInfo: pd.Series) -> Tuple[pd.Series, pd.Series]:
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
  ratioCycles = pd.DataFrame({
    "Pb6_4": data["206Pb"]/data["204Pb"],
    "Pb7_4": data["207Pb"]/data["204Pb"],
    "Pb8_4": data["208Pb"]/data["204Pb"],
    "Pb7_6": data["207Pb"]/data["206Pb"],
    "Pb8_6": data["208Pb"]/data["206Pb"],
    "Pb6_7": data["206Pb"]/data["207Pb"],
    "Pb8_7": data["208Pb"]/data["207Pb"],
    "Pbint": data['204Pb']+data['206Pb']+data['207Pb']+data['208Pb']
  })

  comments, r = cleaning.removeOutliers(ratioCycles)

  # save ratios and standard errors
  ratios = pd.Series({
    "sample_name": sampleInfo.sample_name.item(),
    "type": sampleInfo.type.item(),
    "Pb6_4":     r.Pb6_4.mean(),
    "Pb6_4_err": r.Pb6_4.sem(ddof=0),
    "Pb7_4":     r.Pb7_4.mean(),
    "Pb7_4_err": r.Pb7_4.sem(ddof=0),
    "Pb8_4":     r.Pb8_4.mean(),
    "Pb8_4_err": r.Pb8_4.sem(ddof=0),
    "Pb7_6":     r.Pb7_6.mean(),
    "Pb7_6_err": r.Pb7_6.sem(ddof=0),
    "Pb8_6":     r.Pb8_6.mean(),
    "Pb8_6_err": r.Pb8_6.sem(ddof=0),
    "Pb6_7":     r.Pb6_7.mean(),
    "Pb6_7_err": r.Pb6_7.sem(ddof=0),
    "Pb8_7":     r.Pb8_7.mean(),
    "Pb8_7_err": r.Pb8_7.sem(ddof=0),
    "Pbint":     r.Pbint.mean(),
    "Pbint_err": r.Pbint.sem(ddof=0),
  })

  return comments, ratios
