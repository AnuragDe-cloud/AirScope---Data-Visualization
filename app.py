from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AirScope | Air Pollution Analytics", page_icon="🌍", layout="wide")
st.title("🌍 AirScope")
st.caption("Explore historical air-quality observations across Indian cities.")
DATA_PATH = Path("data/city_day.csv")

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = [c.strip() for c in data.columns]
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["City"] = data["City"].astype("string").str.strip()
    for c in data.columns:
        if c not in ["City", "Date", "AQI_Bucket"]:
            data[c] = pd.to_numeric(data[c], errors="coerce")
    return data.dropna(subset=["Date", "City"])

if not DATA_PATH.exists():
    st.error("Dataset not found. Download city_day.csv and place it in the data/ folder. See README.md.")
    st.stop()

df = load_data(str(DATA_PATH))
st.sidebar.header("Filters")
city_options = sorted(df["City"].dropna().unique().tolist())
default_cities = [c for c in ["Pune", "Mumbai", "Delhi", "Bengaluru"] if c in city_options]
selected_cities = st.sidebar.multiselect("Cities", city_options, default=default_cities or city_options[:4])
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if len(date_range) != 2:
    st.info("Choose both a start and end date.")
    st.stop()
start_date, end_date = date_range
filtered = df[df["City"].isin(selected_cities) & df["Date"].dt.date.between(start_date, end_date)].copy()
if filtered.empty:
    st.warning("No rows match these filters.")
    st.stop()

st.info(f"Dataset period: {min_date} to {max_date}. This is historical data, not live air quality.")
k1, k2, k3, k4 = st.columns(4)
if "AQI" in filtered:
    k1.metric("Mean AQI", f"{filtered['AQI'].mean():.1f}" if filtered["AQI"].notna().any() else "N/A")
    k2.metric("Highest recorded AQI", f"{filtered['AQI'].max():.0f}" if filtered["AQI"].notna().any() else "N/A")
else:
    k1.metric("Mean AQI", "Unavailable")
    k2.metric("Highest recorded AQI", "Unavailable")
k3.metric("Cities selected", str(filtered["City"].nunique()))
k4.metric("Daily records", f"{len(filtered):,}")

left, right = st.columns(2)
if "AQI" in filtered:
    city_mean = filtered.groupby("City", as_index=False)["AQI"].mean().dropna().sort_values("AQI", ascending=False)
    left.plotly_chart(px.bar(city_mean, x="City", y="AQI", title="Mean AQI by City", labels={"AQI":"Mean AQI"}), use_container_width=True)
    monthly = filtered.assign(Month=filtered["Date"].dt.to_period("M").dt.to_timestamp()).groupby(["Month","City"], as_index=False)["AQI"].mean()
    right.plotly_chart(px.line(monthly, x="Month", y="AQI", color="City", markers=True, title="Monthly Mean AQI"), use_container_width=True)

if "AQI" in filtered:
    heat = filtered.assign(Month=filtered["Date"].dt.month).pivot_table(index="City", columns="Month", values="AQI", aggfunc="mean")
    st.plotly_chart(px.imshow(heat, aspect="auto", color_continuous_scale="YlOrRd", labels={"x":"Month","y":"City","color":"Mean AQI"}, title="AQI Heatmap: City vs Month"), use_container_width=True)

pollutants = [c for c in ["PM2.5","PM10","NO2","NO","NOx","NH3","CO","SO2","O3"] if c in filtered.columns]
if pollutants:
    pollutant = st.selectbox("Choose a pollutant", pollutants)
    pollutant_data = filtered.dropna(subset=[pollutant])
    c1, c2 = st.columns(2)
    trend = pollutant_data.assign(Month=pollutant_data["Date"].dt.to_period("M").dt.to_timestamp()).groupby(["Month","City"], as_index=False)[pollutant].mean()
    c1.plotly_chart(px.line(trend, x="Month", y=pollutant, color="City", markers=True, title=f"Monthly {pollutant} Trend"), use_container_width=True)
    c2.plotly_chart(px.box(pollutant_data, x="City", y=pollutant, color="City", title=f"{pollutant} Distribution by City"), use_container_width=True)

if {"PM2.5","PM10"}.issubset(filtered.columns):
    st.plotly_chart(px.scatter(filtered.dropna(subset=["PM2.5","PM10"]), x="PM2.5", y="PM10", color="City", hover_data=["Date"], title="PM2.5 vs PM10"), use_container_width=True)

with st.expander("View filtered data"):
    st.dataframe(filtered, use_container_width=True)
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "airscope_filtered_data.csv", "text/csv")
st.caption("Interpretation note: these charts describe the selected dataset and time range. Associations do not prove causation, and historical observations are not current health guidance.")
