# Laser lead processor

Process raw Pb and Hg intensity data from an automated laser ablation ICP-MS run, and output corrected Pb isotope ratios.

Assumes (for now):

- Thermo Scientific Neptune Mass Spectrometer output file format (tab-delimited `.exp` file with header rows)
- all of 202Hg, 204Pb, 206Pb, 207Pb, and 208Pb were measured
- The first part of each time-resolved analysis is a blank, followed by the measurement, followed by a washout period
- a standard-sample bracketing protocol was used

## Acknowledgements

This package is based on the process used at Southampton University's School of Ocean and Earth Science [Geochemistry labs](https://www.southampton.ac.uk/oes/research/themes/geochemistry/instruments_and_labs.page), developed by (among others) Gavin Foster and J Andy Milton.
