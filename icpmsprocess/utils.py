import pandas as pd
import glob
import os
from typing import List

from icpmsprocess.mstypes import IsotopeSystem, Sample


def load_samples(
    data_dir: str,
    sample_map_path: str,
    isotope_system: IsotopeSystem,
    file_ext: str = ".exp",
    header_row: int = 22,
    comment_char: str = "*",
    index_col: str = "Cycle",
) -> List[Sample]:
    """
    Load all samples from a directory matching them to sample map entries.

    Deafult values are for Neptune `.exp` files.

    Parameters:
    - data_dir (str): The directory containing the sample data files.
    - sample_map_path (str): The path to the CSV file containing the sample map.
    - isotope_system (IsotopeSystem): The isotope system to be used for the samples.
    - file_ext (str, optional): The file extension of the data files. Defaults to ".exp".
    - header_row (int, optional): The row number to use as the header. Defaults to 22.
    - comment_char (str, optional): The character used to denote comments in the data files. Defaults to "*".
    - index_col (str, optional): The column to use as the index. Defaults to "Cycle".
    Returns:
    - List[Sample]: A list of Sample objects loaded from the data files.
    """
    data_files = _find_data_files(data_dir, file_ext)
    sample_map = pd.read_csv(sample_map_path)

    samples = []
    for fp in data_files:
        sample_info = _get_sample_info(fp, sample_map, file_ext)
        raw_data = _load_data_file(fp, header_row, comment_char, index_col)
        samples.append(
            Sample(
                name=sample_info.sample_name,
                type=sample_info.type,
                isotope_system=isotope_system,
                timeseries_data=raw_data,
            )
        )

    return samples


def _find_data_files(data_dir: str, file_ext: str) -> List[str]:
    """Find all data files with given extension in directory"""
    data_files = glob.glob(glob.escape(data_dir) + "/*" + file_ext)
    if len(data_files) == 0:
        raise RuntimeError(
            "No data files found. Are the directory and file extension settings correct?"
        )
    return data_files


def _get_sample_info(
    filepath: str, sample_map: pd.DataFrame, file_ext: str
) -> pd.Series:
    """Get sample metadata from sample map"""
    sample_info = sample_map[
        sample_map.file_name.str.contains(
            os.path.basename(filepath).replace(file_ext, "")
        )
    ]
    if sample_info.empty:
        raise ValueError(f"No matching sample info found for file: {filepath}")
    return sample_info.iloc[0]


def _load_data_file(
    filepath: str,
    header_row: int,
    comment_char: str,
    index_col: str,
    separator: str = "\t",
) -> pd.DataFrame:
    """Load and preprocess a single data file"""

    # Read raw data
    data = pd.read_table(
        filepath,
        header=header_row,
        comment=comment_char,
        index_col=index_col,
        sep=separator,
    )
    return data
