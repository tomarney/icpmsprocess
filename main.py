# %%
# setup
import os
from typing import List
import pandas as pd
import glob
import corrections as corr
import calculations as calc
import config as c

# TODO: make a dataclass
sampleMapPath: str = c.SETTINGS["sample_map"]
dataDir: str = c.SETTINGS["data_dir"]
fileExt: str = c.SETTINGS["file_ext"]
headerRow: int = c.SETTINGS["header_row"]
commentChar: str = c.SETTINGS["comment_char"]
indexCol: str = c.SETTINGS["index_col"]
intCols: List[str] = c.SETTINGS["intensity_cols"]


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
    r = corr.internal(d)
    # reduce data to ratios with errors
    r = calc.reducePb(r, sampleInfo)

    summaryDictList.append(r)

# %%
# add all reduced data to one dataframe and save as CSV
result = pd.DataFrame(summaryDictList).set_index("sample")
result.to_csv("output/results_internally-corrected.csv")
