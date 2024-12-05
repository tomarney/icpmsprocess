import copy
from typing import List
import pandas as pd

from icpmsprocess.mstypes import (
    ProcessingSettings,
    Sample,
    ReferenceMaterial,
)
from icpmsprocess.processors import (
    InternalCorrector,
    MassBiasCorrector,
    RatioCalculator,
)


class DataProcessor:
    """Main processing orchestrator"""

    def __init__(
        self,
        settings: ProcessingSettings,
        correction_reference_material: ReferenceMaterial,
    ):
        self.settings = settings
        self.internal_corrector = InternalCorrector(settings)
        self.ratio_calculator = RatioCalculator()
        self.mass_bias_corrector = MassBiasCorrector(correction_reference_material)

    def process(self, samples: List[Sample]) -> pd.DataFrame:
        processed_data = []
        for sample in copy.deepcopy(samples):
            sample = self.internal_corrector.correct(sample)
            if sample.isotope_system.peak_strip is not None:
                sample = self.ratio_calculator.strip_peaks(sample)
            sample = self.ratio_calculator.reduce(sample)
            processed_data.append(sample)

        corrected_data = self.mass_bias_corrector.correct(processed_data)

        # Convert the list of samples to a DataFrame
        metadata = {
            "name": [sample.name for sample in corrected_data],
            "type": [sample.type for sample in corrected_data],
        }

        # Unpack reduced_data series into the DataFrame
        reduced_data_df = pd.DataFrame(
            [sample.reduced_data for sample in corrected_data]
        )
        result_df = pd.DataFrame(metadata).join(reduced_data_df)

        return result_df
