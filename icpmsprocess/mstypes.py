from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd


@dataclass
class ProcessingSettings:
    """Settings for data processing"""

    intensity_metric: str
    min_signal_intensity: float
    max_blank_intensity: float
    low_cycles_warning_frac: float
    blank_cycles: int
    signal_cycles: Tuple[int, int]


@dataclass
class IsotopeRatio:
    """
    Defines a ratio between two isotopes.

    Attributes:
        numerator: The numerator isotope (e.g., "206Pb").
        denominator: The denominator isotope (e.g., "204Pb").
        name: The generated name of the ratio based on the numerator and denominator.
    """

    numerator: str
    denominator: str

    @property
    def name(self) -> str:
        """Generate the name of the ratio based on the numerator and denominator."""
        return f"{self.numerator}_{self.denominator}"


@dataclass
class PeakStripSettings:
    """Settings to use for correction of isobaric interference"""

    target_isotope: str
    known_isotope_ratio: IsotopeRatio
    known_isotope_ratio_value: float


@dataclass
class IsotopeSystem:
    """
    Defines an isotope system and its ratios.

    Attributes:
        name: The name of the isotope system (e.g., "Pb-Pb").
        ratios: A list of IsotopeRatio objects.
    """

    name: str
    ratios: List[IsotopeRatio]
    peak_strip: PeakStripSettings | None = None

    def get_ratio_columns(self) -> List[str]:
        """Get column names for all ratios"""
        return [f"{self.name}{r.name}" for r in self.ratios]

    def get_intensity_columns(self) -> List[str]:
        """Generate intensity columns from the list of IsotopeRatios."""
        isotopes = set()
        for ratio in self.ratios:
            isotopes.add(ratio.numerator)
            isotopes.add(ratio.denominator)
        return list(isotopes)


@dataclass
class Sample:
    """
    Mass spectrometry sample data

    Attributes:
        name (str): The sample name.
        type (str): The type of the sample ("standard", "control", "sample").
        isotope_system (IsotopeSystem): The intended isotope system associated with the measurements of this sample.
        timeseries_data (pd.DataFrame): The full data of the sample. Rows are cycles, columns are measured mass intensities.
        reduced_data (pd.Series | None): The reduced data of the sample; None until calculated. Content is determined by the isotope_system.
    """

    name: str
    type: str
    isotope_system: IsotopeSystem
    timeseries_data: pd.DataFrame
    reduced_data: pd.Series | None = None


@dataclass
class ReferenceValue:
    """Represents a standard value with its uncertainty, units, and source."""

    value: float
    source: str
    units: str = ""
    uncertainty: float | None = None


@dataclass
class ReferenceMaterial:
    """Reference material for standardization"""

    name: str
    values: dict[str, ReferenceValue]

    def get_value(self, key: str) -> ReferenceValue:
        """Get the reference value for a given property of the reference material."""
        if key not in self.values:
            raise KeyError(f"An entry for '{key}' not found in '{self.name}'.")
        return self.values[key]
