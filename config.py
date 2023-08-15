from dataclasses import dataclass
from dataclass_wizard import YAMLWizard
from typing import List, Tuple


@dataclass
class Settings(YAMLWizard):
  blank_cycles: int
  signal_cycles: Tuple[int,int]
  sample_map: str
  data_dir: str
  output_dir: str
  file_ext: str
  header_row: int
  comment_char: str
  index_col: str | int
  intensity_cols: List[str]
  low_signal_metric: str
  low_signal_level: float
  low_cycles_warning_frac: float
  blank_upper_limit: float

@dataclass
class PbIsotopeList:
  Pb_6_4: float
  Pb_7_4: float
  Pb_7_6: float
  Pb_8_4: float
  Pb_8_6: float

@dataclass
class Constants(YAMLWizard):
  Hg_4_2: float
  NIST610: PbIsotopeList
  NIST612: PbIsotopeList

try:
  SETTINGS = Settings.from_yaml_file('settings.yml')
except:
  raise Exception("Could not load settings file. Please make sure it exists and has the correct structure.")

try:
  CONST = Constants.from_yaml_file('constants.yml')
except:
  raise Exception("Could not load constants file. Please make sure it exists and has the correct structure.")