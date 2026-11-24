# DTM Analytics Workbench

A lightweight humanitarian data quality and displacement analytics application designed to support the preparation, validation, exploration and presentation of displacement data.

## Overview

The DTM Analytics Workbench demonstrates a practical workflow for transforming raw humanitarian datasets into structured, reliable and accessible information.

It combines Python-based data processing capabilities with a React-based interactive dashboard to explore displacement trends, assess data quality and visualise location-level indicators.

## Key Features

### Interactive Dashboard
- Overview of internally displaced persons (IDP) and returnee figures.
- Summary indicators for displacement and assessed locations.
- Country-level filtering.

### Displacement Mapping
- Interactive map displaying assessed locations.
- Location-level IDP and returnee information.
- Geographic visualisation using latitude and longitude.

### Analytics
- Displacement indicators by location.
- Visual comparison of IDP and returnee figures.
- Tabular presentation of assessment data.

### Data Quality
- Dataset completeness checks.
- Missing-value identification.
- Duplicate record checks.
- Basic data profiling and validation.

### Python Data Processing
The Python modules provide separate capabilities for:
- Data profiling.
- Data validation.
- Data cleaning.
- Displacement data analysis.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Development server | Vite |
| Mapping | Leaflet, React Leaflet |
| Charts | Recharts |
| CSV processing | PapaParse |
| Data analysis | Python, Pandas, NumPy |
| Data application | Streamlit |
| Data formats | CSV, Excel |

## Project Structure

```text
dtm-analytics-workbench/
│
├── app.py
├── generate_sample_data.py
├── requirements.txt
│
├── modules/
│   ├── data_profiling.py
│   ├── data_validation.py
│   ├── data_cleaning.py
│   └── displacement.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│
└── frontend/
    ├── public/
    │   └── sample_displacement_data.csv
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    └── package.json
```

## Running the Application

### React Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal.

### Python Application

From the project root, install the Python dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit application:

```bash
python -m streamlit run app.py
```

## Sample Data

The included displacement dataset is synthetic and intended for application testing and demonstration.

It contains illustrative assessment records from Kenya, the Democratic Republic of the Congo and South Sudan.

The geographic coordinates are approximate town-level reference points and should not be interpreted as verified displacement-site coordinates.

No actual IOM operational dataset is included.

## Technical Scope

The React frontend currently reads the sample CSV file directly. The Python processing modules operate separately and have not yet been integrated through an API.

