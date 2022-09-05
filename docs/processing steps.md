# Processing steps

This is a high-level overview of what the code is doing. There are essentially two steps: Internal and mass-bias corrections.

## 1. Internal corrections

To correct for interference. Create a summary table, with rows for each observation, then for each data file:

1. save type to summary table (sample/reference standard/control)
2. import tab-delimited `.exp` file
    - ignore first 22 rows
    - account for column names starting with numbers?
    - ignore last 12 rows (comment = `***` ?)
    - index = Cycle
3. split data into blank, signal, and washout
    - blank: first n cycles (rows) (plus margin at start and end?)
    - signal: detect burn-through/laser turning off? by rate of change?
    - washout: last n cycles - just discarded
4. calculate average blank
    - mean of blank cycles for each isotope
5. subtract blank from each signal cycle of each isotope
6. Peak strip to correct for isobaric interference of 204Hg on 204Pb
    - work out 204Hg intensity by multiplying by the 204/202 ratio (known)
    - then subtract that voltage from the measured 204 intensity to leave just 204Pb
    - `Pb204intV - Hg204/202ratio * Hg202intV`
7. calculate ratios (206/204, 207/204, 208/204, 207/206, 208/206) for all signal cycles in each ratio
8. calculate summary statistics for each ratio and save to summary table
    - n: number of signal cycles
    - mean
    - 1sd: standard deviation
    - 2sd ppm: `Std dev / avg * 2 * 1000000`
      - sd/mean is the coefficient of variation or relative standard deviation, a standardised measure of dispersion
      - multiplied by 2 for 2sd
      - multiplied by 1 million for ppm
    - 1se: standard error: std dev / sqrt(n)
    - 2se ppm: `SE / avg * 2 * 1000000`
      - same logic as 2sd ppm

## 2. Mass bias correction

Correct drift in the instrument measurements by using the standards that bracket the samples.

Create two tables, one for controls and one for samples. For each ratio of interest:

1. Average first 3 reference standard analyses, check they're consistent
    - relative standard deviation is not greater than x?
    - output the average value, the result of the check, and the number behind it
2. Compare NIST612 to known value - for each of the three 612 analyses:
    1. take internally corrected (peak-stripped) ratio, and divide by the average of the nearest reference standard measurement values before and after it
    2. multiply by the known value of the ratio for NIST610 (from literature/certificate)
    3. calculate summary stats of these three values
         - mean value
         - 1sd ppm (`SE / avg * 2 * 1000000`)
         - [all the rest in step 8 above?]
3. for each block of unknowns (samples + controls),
      1. find the two standards before and after in the run queue
      2. do the same calculation as 2.2 above.
      3. Save the result
         - if the measurement is on a standard, add it to the controls table.
         - if a sample, add to sample table
4. Save the two tables to disk as CSV files, and write to the console their locations and a summary (time taken, observations processed, etc)