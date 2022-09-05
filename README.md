# Laser lead processor

Process raw Pb and Hg intensity data from an automated laser ablation ICP-MS run, and output corrected Pb isotope ratios.

**Note:** I wrote this tool to help me process a large number of samples based on, but instead of, the in-house Excel spreadsheet-based workflow. As such, it is (for now) a very specific solution for my narrow needs, and therefore assumes:

- Thermo Scientific Neptune Mass Spectrometer output file format (tab-delimited `.exp` file with header rows)
- all of 202Hg, 204Pb, 206Pb, 207Pb, and 208Pb were measured
- The first part of each time-resolved analysis is a blank, followed by the measurement, followed by a washout period, **and that this is the same for all observations** (timings and all)
- a standard-sample bracketing protocol was used, including controls (standards as unknowns).

If you want to adapt it for your needs, feel free to fork and modify it - or even better, modify it in a way that makes it more generalisable and submit a pull request to this repo!

If you notice a mistake (either a scientific mis-step or a programming bug), please file an issue. I'll be grateful for the heads-up.

## Package structure

The package has the following structure:

```txt
.
├── settings.yml
├── constants.yml
├── sampleMap.csv
└── data/
    ├── S-001.exp
    ├── S-002.exp
    └── etc.
```

- a directory containing only the MS output `.exp` files
- a CSV file mapping filenames to sample names; for example:

    | file_name | sample_name | type     |
    | --------- | ----------- | -------- |
    | S-001.exp | NIST610     | standard |
    | S-002.exp | NIST612     | control  |
    | S-003.exp | my-sample-1 | sample   |

- a configuration file in the base directory called `settings.yml`; for example:

    ```yaml
    sampleMap: inputs/sampleMap.csv
    dataDir: data/
    blankCycles: 60
    signalCycles:
      start: 70
      end: 180
    ```

- a second YAML file `constants.yml` containing the known reference material preferred values and natural constants

## Acknowledgements

This package is based on the process used at Southampton University's School of Ocean and Earth Science [Geochemistry labs](https://www.southampton.ac.uk/oes/research/themes/geochemistry/instruments_and_labs.page), developed by (among others) Gavin Foster and J Andy Milton.

This work was supported by the Natural Environmental Research Council [grant number NE/S007210/1]
