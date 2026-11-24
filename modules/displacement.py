
import pandas as pd


def calculate_displacement(df):

    required_columns = [
        "country",
        "assessment_date",
        "idps_stock",
        "returnees_stock",
        "new_displacements_flow",
        "returns_flow"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df.copy()

    data["assessment_date"] = pd.to_datetime(
        data["assessment_date"],
        errors="coerce"
    )

    numeric_columns = [
        "idps_stock",
        "returnees_stock",
        "new_displacements_flow",
        "returns_flow"
    ]

    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Exclude rows with invalid assessment dates
    data = data.dropna(subset=["assessment_date"])

    # Aggregate population stocks
    stock = (
        data.groupby(["country", "assessment_date"], as_index=False)
        [["idps_stock", "returnees_stock"]]
        .sum(min_count=1)
    )

    # Aggregate displacement and return movements
    flows = (
        data.groupby(["country", "assessment_date"], as_index=False)
        [["new_displacements_flow", "returns_flow"]]
        .sum(min_count=1)
    )

    # Calculate changes in recorded IDP stock
    stock = stock.sort_values(["country", "assessment_date"])

    stock["idp_change"] = (
        stock.groupby("country")["idps_stock"].diff()
    )

    stock["idp_percentage_change"] = (
        stock.groupby("country")["idps_stock"]
        .pct_change(fill_method=None) * 100
    )

    return {
        "stock": stock,
        "flows": flows
    }
