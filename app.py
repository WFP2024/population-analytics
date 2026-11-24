
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.data_profiling import profile_dataset
from modules.displacement import calculate_displacement
from modules.data_validation import validate_dataset
from modules.data_cleaning import clean_dataset


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="DTM Analytics Workbench",
    page_icon="🌍",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "validation_results" not in st.session_state:
    st.session_state.validation_results = None

if "cleaned_dataset" not in st.session_state:
    st.session_state.cleaned_dataset = None

if "cleaning_log" not in st.session_state:
    st.session_state.cleaning_log = None


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.title("🌍 DTM Analytics Workbench")

    st.caption(
        "Humanitarian Data Quality & Displacement Analytics"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Data Import",
            "Data Quality",
            "Displacement Analytics",
            "Data Validation",
            "Data Cleaning"
        ]
    )


# ==================================================
# OVERVIEW
# ==================================================

if page == "Overview":

    st.title("🌍 DTM Analytics Workbench")

    st.subheader(
        "Humanitarian Data Quality & Displacement Analytics"
    )

    st.write(
        "A demonstration workspace for importing, validating "
        "and analysing humanitarian displacement data."
    )

    st.divider()

    if st.session_state.dataset is not None:

        df = st.session_state.dataset

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Records", len(df))

        col2.metric("Total Columns", len(df.columns))

        col3.metric(
            "Countries",
            df["country"].nunique()
            if "country" in df.columns else "N/A"
        )

        st.success("Dataset successfully loaded.")

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

    else:

        st.info(
            "Upload a displacement dataset using the Data Import page."
        )


# ==================================================
# DATA IMPORT
# ==================================================

elif page == "Data Import":

    st.title("📂 Data Import")

    st.write(
        "Upload humanitarian displacement data in CSV or Excel format."
    )

    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        try:

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.dataset = df

            # Reset results when a new dataset is uploaded
            st.session_state.validation_results = None
            st.session_state.cleaned_dataset = None
            st.session_state.cleaning_log = None

            st.success("Dataset uploaded successfully!")

            st.subheader("Dataset Preview")

            st.dataframe(
                df.head(20),
                use_container_width=True
            )

            col1, col2 = st.columns(2)

            col1.metric("Records", len(df))
            col2.metric("Columns", len(df.columns))

        except Exception as e:

            st.error(f"Unable to read dataset: {e}")

    if st.session_state.dataset is not None:

        st.info(
            f"Current dataset: "
            f"{len(st.session_state.dataset)} records loaded."
        )


# ==================================================
# DATA QUALITY
# ==================================================

elif page == "Data Quality":

    st.title("🔍 Data Quality Assessment")

    if st.session_state.dataset is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.dataset

        try:

            report = profile_dataset(df)

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Records", report["total_records"])

            col2.metric("Columns", report["total_columns"])

            col3.metric("Missing Cells", report["missing_cells"])

            col4.metric(
                "Completeness",
                f"{report['completeness']:.1f}%"
            )

            st.divider()

            st.subheader("Missing Values by Column")

            missing_df = report["missing_report"]

            if isinstance(missing_df, pd.DataFrame):
                st.dataframe(
                    missing_df,
                    use_container_width=True
                )
            else:
                st.write(missing_df)

            st.subheader("Data Types")

            st.write(report["data_types"])

            st.subheader("Numeric Summary")

            st.dataframe(
                report["numeric_summary"],
                use_container_width=True
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Duplicate Records",
                report["duplicate_count"]
            )

            col2.metric(
                "Empty Columns",
                len(report["empty_columns"])
            )

            if report["empty_columns"]:
                st.warning(
                    f"Empty columns: {report['empty_columns']}"
                )

        except Exception as e:

            st.error(
                f"Data quality assessment failed: {e}"
            )


# ==================================================
# DISPLACEMENT ANALYTICS
# ==================================================

elif page == "Displacement Analytics":

    st.title("📊 Displacement Analytics")

    st.write(
        "Analyse internally displaced populations, returnees "
        "and displacement movements."
    )

    if st.session_state.dataset is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.dataset

        try:

            results = calculate_displacement(df)

            stock = results["stock"]
            flows = results["flows"]

            if stock.empty:

                st.warning(
                    "No valid assessment dates found in the dataset."
                )

            else:

                countries = sorted(
                    stock["country"].dropna().unique()
                )

                if not countries:

                    st.warning("No valid countries found.")

                else:

                    selected_country = st.selectbox(
                        "Select Country",
                        countries
                    )

                    country_stock = stock[
                        stock["country"] == selected_country
                    ].sort_values("assessment_date")

                    country_flows = flows[
                        flows["country"] == selected_country
                    ].sort_values("assessment_date")

                    st.divider()

                    latest = country_stock.iloc[-1]

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Recorded IDP Stock",
                        f"{latest['idps_stock']:,.0f}"
                        if pd.notna(latest["idps_stock"])
                        else "N/A"
                    )

                    col2.metric(
                        "Recorded Returnee Stock",
                        f"{latest['returnees_stock']:,.0f}"
                        if pd.notna(latest["returnees_stock"])
                        else "N/A"
                    )

                    latest_change = latest["idp_percentage_change"]

                    col3.metric(
                        "IDP Stock Change",
                        f"{latest_change:+.1f}%"
                        if pd.notna(latest_change)
                        else "N/A",
                        help=(
                            "Change compared with the previous assessment, "
                            "not new displacement."
                        )
                    )

                    st.divider()

                    st.subheader("Population Stock Trends")

                    stock_long = country_stock.melt(
                        id_vars=["assessment_date"],
                        value_vars=[
                            "idps_stock",
                            "returnees_stock"
                        ],
                        var_name="Population Group",
                        value_name="Population"
                    )

                    stock_long["Population Group"] = (
                        stock_long["Population Group"].map({
                            "idps_stock": "IDP Stock",
                            "returnees_stock": "Returnee Stock"
                        })
                    )

                    fig_stock = px.line(
                        stock_long,
                        x="assessment_date",
                        y="Population",
                        color="Population Group",
                        markers=True,
                        title=f"Population Trends - {selected_country}"
                    )

                    fig_stock.update_layout(
                        xaxis_title="Assessment Date",
                        yaxis_title="Population",
                        legend_title="Population Group"
                    )

                    st.plotly_chart(
                        fig_stock,
                        use_container_width=True
                    )

                    st.subheader(
                        "Displacement and Return Movements"
                    )

                    flow_long = country_flows.melt(
                        id_vars=["assessment_date"],
                        value_vars=[
                            "new_displacements_flow",
                            "returns_flow"
                        ],
                        var_name="Movement Type",
                        value_name="People"
                    )

                    flow_long["Movement Type"] = (
                        flow_long["Movement Type"].map({
                            "new_displacements_flow": "New Displacements",
                            "returns_flow": "Returns"
                        })
                    )

                    fig_flows = px.bar(
                        flow_long,
                        x="assessment_date",
                        y="People",
                        color="Movement Type",
                        barmode="group",
                        title=f"Movement Flows - {selected_country}"
                    )

                    fig_flows.update_layout(
                        xaxis_title="Reporting Date",
                        yaxis_title="Number of People"
                    )

                    st.plotly_chart(
                        fig_flows,
                        use_container_width=True
                    )

                    st.subheader("Country Assessment Data")

                    st.dataframe(
                        country_stock,
                        use_container_width=True
                    )

                    st.subheader("Movement Data")

                    st.dataframe(
                        country_flows,
                        use_container_width=True
                    )

                    st.download_button(
                        "Download Population Stock CSV",
                        data=country_stock.to_csv(index=False),
                        file_name=(
                            f"{selected_country}_population_stock.csv"
                        ),
                        mime="text/csv"
                    )

        except Exception as e:

            st.error(
                f"Displacement analytics could not be generated: {e}"
            )


# ==================================================
# DATA VALIDATION
# ==================================================

elif page == "Data Validation":

    st.title("🛡️ Data Validation")

    st.write(
        "Automatically identify data quality issues before "
        "humanitarian displacement analysis."
    )

    if st.session_state.dataset is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.dataset

        st.subheader("Dataset Validation")

        st.write(
            "Run automated checks against required fields, "
            "population figures, dates and country codes."
        )

        if st.button("Run Data Validation", type="primary"):

            try:

                issues = validate_dataset(df)

                st.session_state.validation_results = issues

            except Exception as e:

                st.error(f"Validation failed: {e}")

        if st.session_state.validation_results is not None:

            issues = st.session_state.validation_results

            st.divider()

            if issues.empty:

                st.success(
                    "No validation issues detected. "
                    "The dataset passed the current checks."
                )

            else:

                critical_count = (
                    issues["severity"] == "Critical"
                ).sum()

                warning_count = (
                    issues["severity"] == "Warning"
                ).sum()

                col1, col2, col3 = st.columns(3)

                col1.metric("Total Issues", len(issues))
                col2.metric("Critical Issues", int(critical_count))
                col3.metric("Warnings", int(warning_count))

                st.divider()

                st.subheader("Detected Issues")

                st.dataframe(
                    issues,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Recommended Actions")

                for _, issue in issues.iterrows():

                    st.markdown(
                        f"**{issue['severity']} — {issue['issue']}**"
                    )

                    st.write(f"Column: {issue['column']}")

                    st.write(
                        f"Records affected: "
                        f"{issue['records_affected']}"
                    )

                    st.info(issue["recommendation"])

                st.download_button(
                    "Download Validation Report",
                    data=issues.to_csv(index=False),
                    file_name="dtm_validation_report.csv",
                    mime="text/csv"
                )


# ==================================================
# DATA CLEANING
# ==================================================

elif page == "Data Cleaning":

    st.title("🧹 Data Cleaning")

    st.write(
        "Clean and standardise displacement datasets "
        "before analysis."
    )

    df = st.session_state.dataset

    if df is None:

        st.info("Please upload a dataset first.")

    else:

        st.subheader("Original Dataset")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        st.write(
            "The cleaning process removes exact duplicates, "
            "standardises country codes and converts dates "
            "and population fields."
        )

        if st.button("Run Data Cleaning", type="primary"):

            try:

                cleaned_df, cleaning_log = clean_dataset(df)

                st.session_state.cleaned_dataset = cleaned_df
                st.session_state.cleaning_log = cleaning_log

                st.success("Data cleaning completed successfully.")

            except Exception as e:

                st.error(f"Data cleaning failed: {e}")

        if st.session_state.cleaned_dataset is not None:

            cleaned_df = st.session_state.cleaned_dataset
            cleaning_log = st.session_state.cleaning_log

            st.divider()

            st.subheader("Cleaning Results")

            col1, col2, col3 = st.columns(3)

            col1.metric("Original Records", len(df))

            col2.metric("Cleaned Records", len(cleaned_df))

            col3.metric(
                "Records Removed",
                len(df) - len(cleaned_df)
            )

            st.subheader("Cleaning Activity")

            if cleaning_log is not None and not cleaning_log.empty:

                st.dataframe(
                    cleaning_log,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success("No cleaning actions were necessary.")

            st.subheader("Cleaned Dataset")

            st.dataframe(
                cleaned_df.head(20),
                use_container_width=True
            )

            csv = cleaned_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Cleaned Dataset",
                data=csv,
                file_name="cleaned_displacement_data.csv",
                mime="text/csv"
            )
