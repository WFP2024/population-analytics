
import pandas as pd
import pycountry


def validate_dataset(df):

    issues = []

    required_columns = [
        "country",
        "iso3",
        "admin1",
        "admin2",
        "assessment_date",
        "idps_stock",
        "returnees_stock",
        "new_displacements_flow",
        "returns_flow"
    ]

    # 1. Check required columns
    for column in required_columns:
        if column not in df.columns:
            issues.append({
                "severity": "Critical",
                "issue": "Missing required column",
                "column": column,
                "records_affected": len(df),
                "recommendation": f"Add the required column: {column}."
            })

    # Continue checks only where relevant columns exist

    # 2. Check missing values
    for column in required_columns:
        if column in df.columns:
            missing = df[column].isna().sum()

            if missing > 0:
                issues.append({
                    "severity": "Warning",
                    "issue": "Missing values",
                    "column": column,
                    "records_affected": int(missing),
                    "recommendation": "Review and complete missing values where possible."
                })

    # 3. Check duplicate records
    duplicates = df.duplicated().sum()

    if duplicates > 0:
        issues.append({
            "severity": "Warning",
            "issue": "Duplicate records",
            "column": "All columns",
            "records_affected": int(duplicates),
            "recommendation": "Investigate duplicate records before aggregation."
        })

    # 4. Check invalid assessment dates
    if "assessment_date" in df.columns:
        dates = pd.to_datetime(
            df["assessment_date"],
            errors="coerce"
        )

        invalid_dates = dates.isna() & df["assessment_date"].notna()

        if invalid_dates.sum() > 0:
            issues.append({
                "severity": "Critical",
                "issue": "Invalid assessment dates",
                "column": "assessment_date",
                "records_affected": int(invalid_dates.sum()),
                "recommendation": "Correct dates or remove invalid records after review."
            })

    # 5. Check negative and non-numeric population values
    numeric_columns = [
        "idps_stock",
        "returnees_stock",
        "new_displacements_flow",
        "returns_flow"
    ]

    for column in numeric_columns:
        if column in df.columns:

            values = pd.to_numeric(df[column], errors="coerce")

            invalid = df[column].notna() & values.isna()

            if invalid.sum() > 0:
                issues.append({
                    "severity": "Warning",
                    "issue": "Non-numeric population values",
                    "column": column,
                    "records_affected": int(invalid.sum()),
                    "recommendation": "Review and correct non-numeric values."
                })

            negative = values < 0

            if negative.sum() > 0:
                issues.append({
                    "severity": "Critical",
                    "issue": "Negative population value",
                    "column": column,
                    "records_affected": int(negative.sum()),
                    "recommendation": "Investigate negative values and correct them at source."
                })

    # 6. Validate ISO3 codes against country names
    if "iso3" in df.columns and "country" in df.columns:

        aliases = {
            "dr congo": "COD",
            "drc": "COD",
            "democratic republic of the congo": "COD",
            "south sudan": "SSD",
            "kenya": "KEN"
        }

        for index, row in df.iterrows():

            if pd.isna(row["iso3"]) or pd.isna(row["country"]):
                continue

            iso3 = str(row["iso3"]).strip().upper()
            country_name = str(row["country"]).strip()

            if not iso3 or not country_name:
                continue

            country = pycountry.countries.get(alpha_3=iso3)

            if country is None:
                issues.append({
                    "severity": "Critical",
                    "issue": "Invalid ISO3 country code",
                    "column": "iso3",
                    "records_affected": 1,
                    "recommendation": f"Check ISO3 code '{iso3}' in record {index}."
                })
                continue

            expected_iso3 = aliases.get(country_name.lower())

            if expected_iso3 is None:
                valid_names = {
                    country.name.lower()
                }

                if hasattr(country, "official_name"):
                    valid_names.add(country.official_name.lower())

                if hasattr(country, "common_name"):
                    valid_names.add(country.common_name.lower())

                if country_name.lower() not in valid_names:
                    issues.append({
                        "severity": "Critical",
                        "issue": "Country and ISO3 mismatch",
                        "column": "country / iso3",
                        "records_affected": 1,
                        "recommendation": (
                            f"Country '{country_name}' does not match "
                            f"ISO3 code '{iso3}' ({country.name}). "
                            "Review the source record."
                        )
                    })

            elif expected_iso3 != iso3:
                issues.append({
                    "severity": "Critical",
                    "issue": "Country and ISO3 mismatch",
                    "column": "country / iso3",
                    "records_affected": 1,
                    "recommendation": (
                        f"Country '{country_name}' should use ISO3 "
                        f"'{expected_iso3}', not '{iso3}'."
                    )
                })

    return pd.DataFrame(
        issues,
        columns=[
            "severity",
            "issue",
            "column",
            "records_affected",
            "recommendation"
        ]
    )
