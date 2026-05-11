import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(page_title="COVID Dashboard", layout="wide")

# Title
st.title("COVID-19 Country Dashboard")

st.write(
    "This web app displays COVID-19 confirmed case information "
    "for selected countries using Johns Hopkins CSSE data."
)

# GitHub raw CSV links
CONFIRMED_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
DEATHS_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
# Load data
@st.cache_data
def load_data(url):
    return pd.read_csv(url)
confirmed_df = load_data(CONFIRMED_URL)
deaths_df = load_data(DEATHS_URL)
# Prepare data
def prepare_data(df, countries, value_name):
    # Filter countries
    df = df[df["Country/Region"].isin(countries)]
    # Remove unnecessary columns
    df = df.drop(columns=["Province/State", "Lat", "Long"])
    # Combine provinces and states
    df = df.groupby("Country/Region").sum().reset_index()
    # Convert wide format to long format
    long_df = df.melt(id_vars="Country/Region", var_name="Date", value_name=f"Cumulative {value_name}")
    # Convert date column
    long_df["Date"] = pd.to_datetime(long_df["Date"])
    # Sort values
    long_df = long_df.sort_values(["Country/Region", "Date"])
    # Calculate daily values
    long_df[f"Daily {value_name}"] = (long_df.groupby("Country/Region")[f"Cumulative {value_name}"].diff().fillna(0))
    return long_df
#Make Sidebar
st.sidebar.header("Options")
countries = sorted(confirmed_df["Country/Region"].unique())
selected_countries = st.sidebar.multiselect("Select countries:", countries, default=["US"])
metric = st.sidebar.selectbox("Choose data type:",["Confirmed Cases", "Deaths"])
display_type = st.sidebar.radio("Display:", ["Daily", "Cumulative"])

# Main app
if len(selected_countries) > 0:
    if metric == "Confirmed Cases":
        data = prepare_data(confirmed_df, selected_countries, "Confirmed Cases")
    else:
        data = prepare_data(deaths_df, selected_countries, "Deaths")

    y_column = f"{display_type} {metric}"

    # Plot
    fig = px.line(data, x="Date", y=y_column, color="Country/Region", title=f"{display_type} {metric} Over Time")

    st.plotly_chart(fig, use_container_width=True)

    # Latest values table
    latest = (data.sort_values("Date").groupby("Country/Region").tail(1))

    st.subheader("Latest Data")

    st.dataframe(latest[["Country/Region", "Date", y_column]], use_container_width=True)

else:
    st.warning("Please select at least one country.")