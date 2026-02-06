import os
import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

# -------------------------------
# Load dataset
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# If CSV is in same folder as app.py
DATA_PATH = os.path.join(BASE_DIR, "owid-covid-data.csv")

# If CSV is in a 'data/' subfolder, use this instead:
# DATA_PATH = os.path.join(BASE_DIR, "data", "owid-covid-data.csv")

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])
df = df[df["continent"].notna()]

# Latest data per country (for global comparisons)
latest = df.sort_values("date").groupby("location").tail(1)

# -------------------------------
# Sidebar for country selection
# -------------------------------
st.sidebar.title("COVID-19 Dashboard")
country = st.sidebar.selectbox("Select Country:", sorted(df["location"].unique()), index=sorted(df["location"].unique()).index("United States"))

# -------------------------------
# Title
# -------------------------------
st.title("COVID-19 Public Health Trends Dashboard")

# -------------------------------
# Country-specific charts
# -------------------------------
st.header(f"Country: {country}")

filtered = df[df["location"] == country]

st.plotly_chart(px.line(
    filtered, x="date", y="total_cases",
    title=f"Total Cases Over Time - {country}",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.line(
    filtered, x="date", y="total_deaths",
    title=f"Total Deaths Over Time - {country}",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.line(
    filtered, x="date", y="stringency_index",
    title=f"Stringency Index Over Time - {country}",
    width=1000, height=500
), use_container_width=True)

# -------------------------------
# Global comparisons
# -------------------------------
st.header("Global Comparisons")

st.plotly_chart(px.line(
    df.groupby("date")["total_cases"].sum().reset_index(),
    x="date", y="total_cases",
    title="Global Total COVID-19 Cases Over Time",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.line(
    df.groupby("date")["new_cases"].sum().reset_index(),
    x="date", y="new_cases",
    title="Global Daily New Cases",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.line(
    df.groupby("date")[["total_cases", "total_deaths"]].sum().assign(
        fatality_rate=lambda x: x["total_deaths"] / x["total_cases"]
    ).reset_index(),
    x="date", y="fatality_rate",
    title="Global Case Fatality Rate Over Time",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.bar(
    latest.sort_values("total_cases", ascending=False).head(10),
    x="location", y="total_cases",
    title="Top 10 Countries by Total Cases",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.bar(
    latest.sort_values("total_deaths_per_million", ascending=False).head(10),
    x="location", y="total_deaths_per_million",
    title="Top 10 Countries by Deaths per Million",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.scatter(
    latest, x="total_cases", y="total_deaths",
    hover_name="location",
    title="Total Cases vs Total Deaths",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.choropleth(
    latest,
    locations="location",
    locationmode="country names",
    color="total_cases_per_million",
    title="Total Cases per Million by Country",
    width=1000, height=600
), use_container_width=True)

st.plotly_chart(px.scatter(
    latest,
    x="stringency_index",
    y="new_cases_per_million",
    hover_name="location",
    title="Stringency Index vs New Cases per Million",
    width=1000, height=500
), use_container_width=True)

st.plotly_chart(px.line(
    df.groupby("date")["new_deaths"].sum().reset_index(),
    x="date", y="new_deaths",
    title="Global Daily New Deaths",
    width=1000, height=500
), use_container_width=True)
