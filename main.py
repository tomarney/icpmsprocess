# %%
# setup
import glob
import os

import pandas as pd

import calculations as calc
import corrections as corr
from config import SETTINGS

# %%
# Process each data file

# find all .exp files in the data directory
listOfDataFiles = glob.glob(glob.escape(SETTINGS.data_dir) + "/*" + SETTINGS.file_ext)

if len(listOfDataFiles) == 0:
    raise RuntimeError("No data files found. Are the directory and file extension settings correct?")

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
    commInt, r = corr.internal(d, sampleInfo)
    # reduce data to ratios with errors
    r = calc.reducePb(r, sampleInfo)

    comm = pd.Series({
      'sample_name': sampleInfo.sample_name.item(),
      'type': sampleInfo.type.item(),
      'blank_nrows': SETTINGS.blank_cycles - commInt.outlier_blank_cycles,
      'signal_nrows': SETTINGS.signal_cycles[1] - SETTINGS.signal_cycles[0] - commInt.outlier_signal_cycles
    })

    summaryList.append(r)
    commentList.append(pd.concat([comm,commInt]))
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
refPlot[0].get_figure().savefig(f'{SETTINGS.output_dir}NIST610-internal-corrected.png')

# %%
# mass bias correction

resultMBC = corr.massBias(resultInternalCorr)
resultMBC.to_csv(f'{SETTINGS.output_dir}results_mass-bias-corrected.csv', index=False)

# %%
# plot all observations of NIST control to check for drift after mass-bias correction

ctrlPlot = resultMBC.loc[resultMBC.sample_name.str.contains(
    'NIST612'),~resultMBC.columns.str.contains('_err')].plot(subplots=True, figsize=(8, 16))
ctrlPlot[0].get_figure().savefig(f'{SETTINGS.output_dir}NIST612-mass-bias-corrected.png')
