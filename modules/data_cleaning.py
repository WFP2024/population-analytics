
import pandas as pd


def clean_dataset(df):

    cleaned_df = df.copy()

    cleaning_log = []

    # 1. Remove exact duplicate records
    duplicates = cleaned_df.duplicated().sum()

    if duplicates > 0:
        cleaned_df = cleaned_df.drop_duplicates()

        cleaning_log.append({
            "action": "Remove duplicate records",
            "records_affected": int(duplicates),
            "status": "Completed"
        })

    # 2. Standardise country names
    if "country" in cleaned_df.columns:

        cleaned_df["country"] = (
            cleaned_df["country"]
            .astype("string")
            .str.strip()
        )

    # 3. Standardise ISO3 codes
    if "iso3" in cleaned_df.columns:

        cleaned_df["iso3"] = (
            cleaned_df["iso3"]
            .astype("string")
            .str.strip()
            .str.upper()
        )

    # 4. Convert assessment dates
    if "assessment_date" in cleaned_df.columns:

        cleaned_df["assessment_date"] = pd.to_datetime(
            cleaned_df["assessment_date"],
            errors="coerce"
        )

    # 5. Convert population columns to numeric
    numeric_columns = [
        "idps_stock",
        "returnees_stock",
        "new_displacements_flow",
        "returns_flow",
        "male_idps",
        "female_idps"
    ]

    for column in numeric_columns:

        if column in cleaned_df.columns:

            original_invalid = (
                cleaned_df[column].notna()
                & pd.to_numeric(
                    cleaned_df[column],
                    errors="coerce"
                ).isna()
            ).sum()

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

            if original_invalid > 0:
                cleaning_log.append({
                    "action": f"Convert {column} to numeric",
                    "records_affected": int(original_invalid),
                    "status": "Completed"
                })

    return cleaned_df, pd.DataFrame(cleaning_log)
