import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# -------------------------------
# Load dataset
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "owid-covid-data.csv")

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])
df = df[df["continent"].notna()]

# Latest data per country (for global comparisons)
latest = df.sort_values("date").groupby("location").tail(1)

# -------------------------------
# Create Dash App
# -------------------------------
app = Dash(_name_)
server = app.server

# -------------------------------
# App Layout
# -------------------------------
app.layout = html.Div([
    html.H1("COVID-19 Public Health Trends Dashboard", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Label("Select Country:", style={"fontWeight": "bold", "fontSize": "18px"}),
    dcc.Dropdown(
        options=[{"label": c, "value": c} for c in sorted(df["location"].unique())],
        value="United States",
        id="country_dropdown",
        style={"marginBottom": "30px"}
    ),

    # Country-specific charts
    html.Div([
        dcc.Graph(id="cases_trend", style={"width": "100%", "height": "500px"}),
        dcc.Graph(id="deaths_trend", style={"width": "100%", "height": "500px"}),
        dcc.Graph(id="stringency_trend", style={"width": "100%", "height": "500px"}),
    ], style={"marginBottom": "50px"}),

    html.H2("Global Comparisons", style={"textAlign": "center", "marginBottom": "30px"}),

    # Global charts
    html.Div([
        dcc.Graph(
            figure=px.line(
                df.groupby("date")["total_cases"].sum().reset_index(),
                x="date",
                y="total_cases",
                title="Global Total COVID-19 Cases Over Time",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.line(
                df.groupby("date")["new_cases"].sum().reset_index(),
                x="date",
                y="new_cases",
                title="Global Daily New Cases",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.line(
                df.groupby("date")[["total_cases", "total_deaths"]].sum().assign(
                    fatality_rate=lambda x: x["total_deaths"]/x["total_cases"]
                ).reset_index(),
                x="date",
                y="fatality_rate",
                title="Global Case Fatality Rate Over Time",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.bar(
                latest.sort_values("total_cases", ascending=False).head(10),
                x="location",
                y="total_cases",
                title="Top 10 Countries by Total Cases",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.bar(
                latest.sort_values("total_deaths_per_million", ascending=False).head(10),
                x="location",
                y="total_deaths_per_million",
                title="Top 10 Countries by Deaths per Million",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.scatter(
                latest,
                x="total_cases",
                y="total_deaths",
                hover_name="location",
                title="Total Cases vs Total Deaths",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.choropleth(
                latest,
                locations="location",
                locationmode="country names",
                color="total_cases_per_million",
                title="Total Cases per Million by Country",
                width=1000, height=600
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.scatter(
                latest,
                x="stringency_index",
                y="new_cases_per_million",
                hover_name="location",
                title="Stringency Index vs New Cases per Million",
                width=1000, height=500
            ),
            style={"marginBottom": "30px"}
        ),
        dcc.Graph(
            figure=px.line(
                df.groupby("date")["new_deaths"].sum().reset_index(),
                x="date",
                y="new_deaths",
                title="Global Daily New Deaths",
                width=1000, height=500
            ),
            style={"marginBottom": "50px"}
        ),
    ])
])

# -------------------------------
# Callback for selected country charts
# -------------------------------
@app.callback(
    Output("cases_trend", "figure"),
    Output("deaths_trend", "figure"),
    Output("stringency_trend", "figure"),
    Input("country_dropdown", "value")
)
def update_country_charts(country):
    filtered = df[df["location"] == country]

    fig1 = px.line(
        filtered, x="date", y="total_cases",
        title=f"Total Cases Over Time - {country}",
        width=1000, height=500
    )
    fig2 = px.line(
        filtered, x="date", y="total_deaths",
        title=f"Total Deaths Over Time - {country}",
        width=1000, height=500
    )
    fig3 = px.line(
        filtered, x="date", y="stringency_index",
        title=f"Stringency Index Over Time - {country}",
        width=1000, height=500
    )
    return fig1, fig2, fig3

# -------------------------------
# Run App
# -------------------------------
if _name_ == "_main_":
    app.run(debug=True)