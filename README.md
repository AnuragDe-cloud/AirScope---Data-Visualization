# AirScope — Air Pollution Analytics in Indian Cities

This project contains:
- `AirScope_Analysis.ipynb`: notebook for data preparation and graphical analysis.
- `app.py`: interactive Streamlit dashboard.
- `data/city_day.csv`: add the dataset here after downloading it.

## 1. Get the dataset
Download the **Air Quality Data in India** dataset by Rohan Rao from Kaggle:
https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india

Extract the archive and copy `city_day.csv` into the `data/` directory. The notebook and dashboard expect columns such as `City`, `Date`, `AQI`, `AQI_Bucket`, `PM2.5`, and `PM10`; available columns may vary by version.

This is historical data (commonly 2015–2020), not live air quality. The project uses only cities that are present in the downloaded file. It reports when a preferred city is missing.

## 2. Install dependencies
From this project folder, run:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

## 3. Run the notebook
```bash
jupyter notebook
```
Open `AirScope_Analysis.ipynb` and run cells from top to bottom.

## 4. Run the dashboard
```bash
streamlit run app.py
```
Streamlit will print a local URL to open in your browser.

## Suggested project structure
```
AirScope_Project/
├── AirScope_Analysis.ipynb
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── city_day.csv
```

## Data interpretation cautions
- AQI and pollutant concentrations are different measures.
- Missing measurements are not automatically imputed in the analysis.
- Compare cities with awareness of different station coverage and missingness.
- Correlation is not causation.
- The historical dataset must not be presented as current/live AQI.
