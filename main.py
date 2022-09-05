# %%
# setup
from distutils.command.config import config
import os
from typing import List
import pandas as pd
import yaml
import glob
import corrections as corr
import calculations as calc

# load config file
with open('settings.yml') as y:
    c = yaml.safe_load(y)

# TODO: make a dataclass
sampleMapPath: str = c["sample_map"]
dataDir: str = c["data_dir"]
fileExt: str = c["file_ext"]
headerRow: int = c["header_row"]
commentChar: str = c["comment_char"]
indexCol: str = c["index_col"]
intCols: List[str] = c["intensity_cols"]


# %%
# find all .exp files in the data directory
listOfDataFiles = glob.glob(glob.escape(dataDir) + "/*" + fileExt)
# load sample map (links file names to sample names and types)
sampleMap = pd.read_csv(sampleMapPath)

# create an empty list. We'll append each sample result in the loop
summaryDictList = []


# process each data file in turn
for fp in listOfDataFiles:
    # get name and type of this observation
    sampleInfo = sampleMap[sampleMap.file_name.str.contains(
        os.path.basename(fp))]

    # read the data file. Ignore the first n row and any comments, set the index
    d = pd.read_table(fp,
                      header=headerRow,
                      comment=commentChar,
                      index_col=indexCol
                      )

    # return only intensity columns and drop rows with no data
    d = d.loc[:, intCols].dropna(how="all")

    # apply internal corrections
    r = corr.internal(d, c)
    # reduce data to ratios with errors
    r = calc.reducePb(r, sampleInfo)

    summaryDictList.append(r)

result = pd.DataFrame(summaryDictList)
