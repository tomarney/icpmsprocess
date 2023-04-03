# %%
# setup
import os
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import glob
import corrections as corr
import calculations as calc
from config import SETTINGS


# %%
# Process each data file

# find all .exp files in the data directory
listOfDataFiles = glob.glob(glob.escape(SETTINGS.data_dir) + "/*" + SETTINGS.file_ext)

# load sample map (links file names to sample names and types)
sampleMap = pd.read_csv(SETTINGS.sample_map)

# create an empty list. We'll append each sample result in the loop
summaryList = []
commentList = []

# process each data file in turn
for fp in listOfDataFiles:
    # get name and type of this observation
    sampleInfo = sampleMap[sampleMap.file_name.str.contains(
        os.path.basename(fp).replace(SETTINGS.file_ext,''))]

    # read the data file. Ignore the first n row and any comments, set the index
    d = pd.read_table(fp,
                      header=SETTINGS.header_row,
                      comment=SETTINGS.comment_char,
                      index_col=SETTINGS.index_col
                      )

    # return only intensity columns and drop rows with no data
    d = d.loc[:, SETTINGS.intensity_cols].dropna(how="all")

    # apply internal corrections
    commInt, r = corr.internal(d)
    # reduce data to ratios with errors
    commReduc, r = calc.reducePb(r, sampleInfo)

    comm = pd.Series({
      'sample_name': sampleInfo.sample_name.item(),
      'type': sampleInfo.type.item(),
      'blank_nrows': SETTINGS.blank_cycles - commInt.outlier_blank_cycles,
      'signal_nrows': SETTINGS.signal_cycles[1] - SETTINGS.signal_cycles[0] - commInt.negative_signal_cycles - commReduc.outlier_signal_cycles
    })

    summaryList.append(r)
    commentList.append(pd.concat([comm,commInt,commReduc]))
# END for

# %%
# add all reduced data to one dataframe and save as CSV
resultInternalCorr = pd.DataFrame(summaryList)
resultInternalCorr.to_csv(f'{SETTINGS.output_dir}results_internally-corrected.csv', index=False)

comments = pd.DataFrame(commentList)
comments.to_csv(f'{SETTINGS.output_dir}comments.csv', index=False)


# %%
# plot all observations of reference standards to check for drift

refPlot = resultInternalCorr[resultInternalCorr.type.eq(
    'standard')].plot(subplots=True, figsize=(8, 16))
refPlot[0].get_figure().savefig('output/NIST610-internal-corrected.png')

# %%
# mass bias correction

resultMBC = corr.massBias(resultInternalCorr)
resultMBC.to_csv(f'{SETTINGS.output_dir}results_mass-bias-corrected.csv', index=False)

# %%
# plot all observations of NIST control to check for drift after mass-bias correction

ctrlPlot = resultMBC.loc[resultMBC.sample_name.str.contains(
    'NIST_612'),~resultMBC.columns.str.contains('_err')].plot(subplots=True, figsize=(8, 16))
ctrlPlot[0].get_figure().savefig('output/NIST612-mass-bias-corrected.png')
