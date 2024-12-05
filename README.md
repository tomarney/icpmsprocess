# ICP-MS process (`icpmsprocess`)

Process raw mass spectrum intensity data from an ICP-MS run, and output corrected isotope ratios.

## Getting started

For now, the package is not yet installable from PyPI. The easiest way to use it is to edit the example notebook:

1. Clone the repository (or download as `.zip`)
2. To be able to run the notebook, you'll need to install the dependencies in the `requirements_docs.txt` file using your favourite method:
   - pipenv: `pipenv install -r requirements.txt`
   - conda or mamba: `mamba create --name icpmsprocess_docs --file requirements_docs.txt`
3. Open [/docs/example-usage.ipynb](/docs/example-usage.ipynb) and select the interpreter you just created
4. Run the notebook as-is. It will generate example (Pb-Pb) data files and then process them.

To process your own data:

1. The example notebook will have created a data directory (/docs/data) containing lots of `.exp` data files and a sample map CSV.
2. Delete the cell which creates the example data and the one which plots the results (unless you're also running Pb-Pb! Or you could edit the plot to make sense for your results).
3. Delete the example data files and the results CSV, but keep the sample map CSV.
4. Add your own data files.
5. Edit the sample map to reflect your analysis run (make sure you use the words "sample", "control" or "standard" in the type column).
6. Edit the settings object to reflect your run.
7. Re-run the notebook. Your processed unknowns (samples and controls) will be saved to `/docs/data/results.csv`

## Disclaimer

> This software has not been peer-reviewed and has only been narrowly tested for some situations. I hope it might be useful to others, but you should check it does what you expect and that the results make sense. You can find an overview of the processing steps [here](/docs/processing%20steps.md).

I wrote this tool for my narrow needs. I've tried to generalise it a bit, but it assumes:

- The data to process is in individual time-resolved files, one for each sample/standard
- Each analysis contains a time interval to be treated as a gas blank and another interval to be treated as the measurement
- The same blank/signal timings have been used for all observations
- The mass spectrometer output file is a tabular format which can be read by `Pandas.read_table()`
- a standard-sample bracketing protocol was used, including controls (reference materials analysed as unknowns).

The blank/signal timings, data file format, and analysis protocol (order of standards, controls, and samples) can all be configured.

## Contributing

If you want to adapt it for your needs, feel free to fork and modify it - or even better, modify it in a way that makes it more generalisable and submit a pull request to this repo!

If you notice a mistake (either a scientific mis-step or a programming bug), please file an issue. I'll be grateful for the heads-up.

## Acknowledgements

This package is based on the process used at Southampton University's School of Ocean and Earth Science [Geochemistry labs](https://www.southampton.ac.uk/oes/research/themes/geochemistry/instruments_and_labs.page), developed by (among others) Gavin Foster and J Andy Milton. I have subsequently adapted and extended it, so any mistakes are mine.

This work was supported by the Natural Environmental Research Council [grant number NE/S007210/1]
