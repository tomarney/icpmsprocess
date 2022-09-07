# %%
# setup
import os
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
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
commentDictList = []

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
    commInt, r = corr.internal(d)
    # reduce data to ratios with errors
    r = calc.reducePb(r, sampleInfo)

    commInt['sample_name'] = sampleInfo.sample_name.item()
    commInt['type'] = sampleInfo.type.item()

    summaryDictList.append(r)
    commentDictList.append(commInt)
# END for

# %%
# add all reduced data to one dataframe and save as CSV
resultInternalCorr = pd.DataFrame(summaryDictList).set_index("sample_name")
resultInternalCorr.to_csv("output/results_internally-corrected.csv")

comments = pd.DataFrame(commentDictList).set_index("sample_name")
comments.to_csv("output/comments.csv")


# %%
# plot all observations of reference standards to check for drift

refPlot = resultInternalCorr[resultInternalCorr.type.eq(
    'standard')].plot(subplots=True, figsize=(8, 16))
refPlot[0].get_figure().savefig('output/NIST610-internal-corrected.png')

# %%
# mass bias correction

resultMBC = corr.massBias(resultInternalCorr)
resultMBC.to_csv("output/results_mass-bias-corrected.csv")

# %%
# plot all observations of NIST control to check for drift after mass-bias correction

ctrlPlot = resultMBC[resultMBC.sample_name.str.contains(
    'NIST_612')].plot(subplots=True, figsize=(8, 16))
ctrlPlot[0].get_figure().savefig('output/NIST612-mass-bias-corrected.png')
