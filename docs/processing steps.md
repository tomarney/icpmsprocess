# Processing steps

This is a high-level overview of what the code is doing. There are essentially two steps: Internal and mass-bias corrections.

## 1. Internal corrections

To correct for interference. Create a summary table, with rows for each observation, then for each data file:

1. Import mass spectrometer data file.
2. Match the sample name and type (sample/reference standard/control) to the data file, using the sample map.
3. Split the time-resolved data into a blank and the signal, as defined in the settings object.
4. Calculate the average blank (mean of blank cycles for each mass)
5. Subtract the blank from each signal cycle of each mass.
6. If enabled (`ProcessingSettings.peak_strip` is not `None`), correct for isobaric interferences using the provided settings (`PeakStripSettings`)
    - work out the intensity of the interfering isotope by multiplying by the known ratio of this and another measured mass.
    - then subtract that voltage from the measured target mass intensity to leave just the target isotope intensity.
7. calculate ratios (defined in the `IsotopeSystem`) for all signal cycles in each ratio
8. calculate the mean and the standard error of the mean for each ratio

## 2. Mass bias correction

Correct drift in the instrument measurements by using the standards that bracket the samples.

Loop over the run. For each unknown analysed and for each ratio within it: 
 1. Find the nearest reference material measurements before and after it and take the averages of all the internally corrected ratios measured on them.
 2. Take the unknown's internally corrected ratio and divide by the average reference material's value
 3. multiply by the known value of that ratio
