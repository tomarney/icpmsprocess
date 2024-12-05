from icpmsprocess.mstypes import (
    IsotopeSystem,
    ProcessingSettings,
    ReferenceMaterial,
    Sample,
)


import pandas as pd
from scipy.stats import zscore

import warnings
from typing import List


class InternalCorrector:
    """Handles internal corrections for a sample"""

    def __init__(self, settings: ProcessingSettings):
        self.settings = settings

    def correct(self, sample: Sample) -> Sample:
        blank_raw = sample.timeseries_data.loc[1 : self.settings.blank_cycles]
        signal_raw = sample.timeseries_data.loc[
            self.settings.signal_cycles[0] : self.settings.signal_cycles[1]
        ]

        blank_sample = Sample(
            timeseries_data=blank_raw,
            name=f"{sample.name} (blank)",
            type=sample.type,
            isotope_system=sample.isotope_system,
        )
        signal_sample = Sample(
            timeseries_data=signal_raw,
            name=f"{sample.name} (signal)",
            type=sample.type,
            isotope_system=sample.isotope_system,
        )

        blank = self.remove_outliers(blank_sample, limit_hi=True)
        signal = self.remove_outliers(signal_sample, limit_low=True)

        sample.timeseries_data = (
            signal.timeseries_data.select_dtypes("number")
            - blank.timeseries_data.select_dtypes("number").mean()
        )

        return sample

    def remove_outliers(
        self,
        sample: Sample,
        limit_hi: bool = False,
        limit_low: bool = False,
    ) -> Sample:
        """
        Removes outliers from the sample data based on z-score and specified limits.
        Args:
            sample (Sample): The sample data to process.
            limit_hi (bool, optional): Whether to apply the upper limit for outlier detection. Defaults to False.
            limit_low (bool, optional): Whether to apply the lower limit for outlier detection. Defaults to False.
        Returns:
            pd.DataFrame: A tuple containing a pandas Series with comments and a DataFrame with the cleaned data.
        """
        is_over_hi_limit = pd.Series([False] * len(sample.timeseries_data))
        is_under_low_limit = pd.Series([False] * len(sample.timeseries_data))

        if limit_hi:
            metric = sample.timeseries_data[self.settings.intensity_metric]
            is_over_hi_limit = metric > self.settings.max_blank_intensity
            if is_over_hi_limit.all():
                warnings.warn(
                    f"All cycles in {sample.name} are above the given intensity threshold"
                )
                sample.timeseries_data.iloc[0:0]  # drop all rows
                return sample
        if limit_low:
            metric = sample.timeseries_data[self.settings.intensity_metric]
            is_under_low_limit = metric < self.settings.min_signal_intensity
            if is_under_low_limit.all():
                warnings.warn(
                    f"All cycles in {sample.name} are below the given intensity threshold"
                )
                sample.timeseries_data.iloc[0:0]  # drop all rows
                return sample

        limited_data = sample.timeseries_data.loc[
            ~(is_over_hi_limit | is_under_low_limit), :
        ]

        is_outlier = (
            limited_data.loc[:, sample.isotope_system.get_intensity_columns()]
            .apply(zscore, axis="index")
            .apply(lambda x: x.abs(), axis="index")
            > 3
        )
        has_outliers = is_outlier.any(axis="columns")

        if has_outliers.sum() == len(limited_data):
            warnings.warn(f"Removing outliers left zero cycles in {sample.name}")
            sample.timeseries_data.iloc[0:0]  # drop all rows
            return sample

        sample.timeseries_data = limited_data.copy().loc[
            ~has_outliers, :
        ]  # .loc[[], :] to ensure df

        if (
            len(sample.timeseries_data)
            < len(sample.timeseries_data) * self.settings.low_cycles_warning_frac
        ):
            warnings.warn(
                f"Removing outliers left only {len(sample.timeseries_data)} cycles in {sample.name}"
            )

        return sample


class RatioCalculator:
    """Calculates isotope ratios for any isotope system"""

    def reduce(self, sample: Sample) -> Sample:
        """Calculate all ratios and statistics for a sample"""
        timeseries_ratios = self._calculate_ratios(
            sample.timeseries_data, sample.isotope_system
        )
        sample.reduced_data = self._calculate_statistics(timeseries_ratios)
        return sample

    def strip_peaks(self, sample: Sample) -> Sample:
        """Account for isobaric interferences by peak-stripping, as defined in sample.isotope_system"""
        if sample.isotope_system.peak_strip is None:
            raise ValueError("No peak strip settings defined for isotope system")

        peak_strip = sample.isotope_system.peak_strip

        known_denominator_values = sample.timeseries_data[
            peak_strip.known_isotope_ratio.denominator
        ]
        known_numerator_values = (
            known_denominator_values * peak_strip.known_isotope_ratio_value
        )

        target_values = (
            sample.timeseries_data[peak_strip.target_isotope] - known_numerator_values
        )
        sample.timeseries_data[peak_strip.target_isotope] = target_values
        return sample

    def _calculate_ratios(
        self, ts_data: pd.DataFrame, isotope_system: IsotopeSystem
    ) -> pd.DataFrame:
        """Calculate all defined ratios for the isotope system"""
        ratios = {}
        for ratio in isotope_system.ratios:
            ratios[ratio.name] = ts_data[ratio.numerator] / ts_data[ratio.denominator]

        return pd.DataFrame(ratios)

    def _calculate_statistics(self, ratios: pd.DataFrame) -> pd.Series:
        """Calculate mean and standard error for all ratios"""
        stats = {}
        for col in ratios.columns:
            stats[col] = ratios[col].mean()
            stats[f"{col}_err"] = ratios[col].sem(ddof=0)
        return pd.Series(stats)


class MassBiasCorrector:
    """Handles mass bias corrections using sample-standard bracketing"""

    def __init__(self, ref_mat: ReferenceMaterial):
        self.ref_mat = ref_mat

    def correct(self, measurements: List[Sample]) -> List[Sample]:
        standard_row_indexes = [
            i for i, sample in enumerate(measurements) if sample.type == "standard"
        ]

        if len(standard_row_indexes) == 0:
            raise ValueError("No standards found in dataset")

        prev_std: Sample
        results: List[Sample] = []

        for run_order_number, measurement in enumerate(measurements):

            if measurement.type == "standard":
                prev_std = measurement
                continue

            # Get interpolated standard values
            standard_values = self._get_standard_values(
                run_order_number, measurements, standard_row_indexes, prev_std
            )

            # Apply corrections
            results.append(self._apply_correction(measurement, standard_values))

        return results

    def _get_standard_values(
        self,
        run_order_index: int,
        run_data: List[Sample],
        standard_indices: List[int],
        prev_std: Sample,
    ) -> pd.Series:
        """For an analysis in the run, get the next standard, and return the mean of that and the previous standard."""

        if run_order_index >= standard_indices[-1]:
            warnings.warn(
                "Samples or controls present after the last standard: using only the preceeding standard"
            )
            if prev_std.reduced_data is None:
                raise ValueError(
                    "Previous standard reduced data is missing"
                    + f"(measurement '{run_order_index}' in the run)"
                )
            return prev_std.reduced_data

        next_std_idx = min(idx for idx in standard_indices if idx > run_order_index)
        next_std = run_data[next_std_idx]

        stds = pd.concat(
            [prev_std.reduced_data, next_std.reduced_data], axis="columns"
        ).T
        return stds.mean()

    def _apply_correction(
        self, measurement: Sample, standard_data: pd.Series
    ) -> Sample:
        """Apply mass bias correction to sample using standard values"""
        if measurement.reduced_data is None:
            raise ValueError("Measurement data is missing")

        if standard_data is None:
            raise ValueError("Standard data is missing")

        corrected_data: dict[str, float] = {}

        for ratio in measurement.isotope_system.ratios:
            corrected_data[ratio.name] = (
                measurement.reduced_data[ratio.name]
                / standard_data[ratio.name]
                * self.ref_mat.get_value(ratio.name).value
            )
            corrected_data[f"{ratio.name}_err"] = measurement.reduced_data[
                f"{ratio.name}_err"
            ].item()

        measurement.reduced_data = pd.Series(corrected_data)
        return measurement
