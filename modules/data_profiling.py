
import pandas as pd
import numpy as np


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Analyse a dataset and return a structured
    data quality profile.
    """

    total_records = len(df)
    total_columns = len(df.columns)

    # Missing values
    missing = df.isna().sum()

    missing_report = pd.DataFrame({
        "column": missing.index,
        "missing_values": missing.values,
        "missing_percentage": (
            missing.values / total_records * 100
            if total_records > 0
            else 0
        )
    })

    # Duplicate records
    duplicate_count = int(df.duplicated().sum())

    # Data types
    data_types = pd.DataFrame({
        "column": df.columns,
        "data_type": [
            str(dtype) for dtype in df.dtypes
        ]
    })

    # Unique values
    unique_values = pd.DataFrame({
        "column": df.columns,
        "unique_values": [
            df[col].nunique(dropna=True)
            for col in df.columns
        ]
    })

    # Numeric summary
    numeric_summary = df.describe(
        include=[np.number]
    ).T

    # Empty columns
    empty_columns = [
        col for col in df.columns
        if df[col].isna().all()
    ]

    return {
        "total_records": total_records,
        "total_columns": total_columns,
        "duplicate_count": duplicate_count,
        "missing_report": missing_report,
        "data_types": data_types,
        "unique_values": unique_values,
        "numeric_summary": numeric_summary,
        "empty_columns": empty_columns
    }
