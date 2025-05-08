import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# === Google Sheets Setup ===
creds_json = st.secrets["GOOGLE_CREDENTIALS"]
try:
    creds_dict = json.loads(creds_json)
except json.JSONDecodeError:
    st.error("Invalid JSON in GOOGLE_CREDENTIALS secret.")
    st.stop()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1jCV-IqALZz7wKqjqc5ISrkA_dv35mX1ZowNqwFHf6mk"
SHEET_NAME = 'Observations'

# Open spreadsheet
spreadsheet = client.open_by_key(SPREADSHEET_ID)
try:
    sheet = spreadsheet.worksheet(SHEET_NAME)
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows="100", cols="20")
    sheet.append_row([
        "Entry Type", "Operator ID", "Site", "Monitoring Officer", "Driver",
        "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (hPa)",
        "Weather", "Wind", "Elapsed Time (min)", "Flow Rate (L/min)", "Notes",
        "Submitted At"
    ])

# === Functions ===
def read_data():
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        df["Submitted At"] = pd.to_datetime(df["Submitted At"])
    return df

def add_data(row):
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Add timestamp
    sheet.append_row(row)

def merge_start_stop(df):
    df_start = df[df["Entry Type"] == "START"].copy()
    df_stop = df[df["Entry Type"] == "STOP"].copy()

    merge_cols = ["Operator ID", "Site", "Monitoring Officer", "Driver"]
    merged = pd.merge(
        df_start,
        df_stop,
        on=merge_cols,
        suffixes=("_Start", "_Stop")
    )
    # Compute elapsed time difference (if both present and numeric)
    merged["Elapsed Time Diff (min)"] = merged["Elapsed Time (min)_Stop"] - merged["Elapsed Time (min)_Start"]
    return merged

# === Streamlit UI ===
st.title("PM2.5 Monitoring Data Entry")

ids = ['ID001', 'ID002', 'ID003']
sites = ['Site A', 'Site B', 'Site C']
officers = ['Officer 1', 'Officer 2', 'Officer 3']

# Sidebar - Operator Info
with st.sidebar:
    st.header("Operator Details")
    id_selected = st.selectbox("Select ID", ids)
    site_selected = st.selectbox("Select Site", sites)
    officer_selected = st.multiselect("Monitoring Officer(s)", officers)
    driver_name = st.text_input("Driver's Name")

# === Start Day ===
with st.expander("📅 Start Day Observation", expanded=False):
    with st.form("start_form"):
        start_date = st.date_input("Start Date", value=datetime.today())
        start_obs = st.text_area("First Day Observation Notes")

        st.markdown("#### Atmospheric Conditions")
        start_temp = st.number_input("Temperature (°C)", step=0.1)
        start_rh = st.number_input("Relative Humidity (%)", step=0.1)
        start_pressure = st.number_input("Pressure (hPa)", step=0.1)
        start_weather = st.text_input("Weather")
        start_wind = st.text_input("Wind Speed and Direction")

        st.markdown("#### Sampler Information")
        start_elapsed = st.number_input("Initial Elapsed Time (min)", step=1)
        start_flow = st.number_input("Initial Flow Rate (L/min)", step=0.1)
        start_time = st.time_input("Start Time", value=datetime.now().time())

        submit_start = st.form_submit_button("Submit Start Day Data")
        if submit_start:
            if all([id_selected, site_selected, officer_selected, driver_name]):
                for officer in officer_selected:
                    start_row = [
                        "START", id_selected, site_selected, officer, driver_name,
                        start_date.strftime("%Y-%m-%d"), start_time.strftime("%H:%M:%S"),
                        start_temp, start_rh, start_pressure, start_weather, start_wind,
                        start_elapsed, start_flow, start_obs
                    ]
                    add_data(start_row)
                st.success("Start day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Stop Day ===
with st.expander("📅 Stop Day Observation", expanded=False):
    with st.form("stop_form"):
        stop_date = st.date_input("Stop Date", value=datetime.today())
        stop_obs = st.text_area("Final Day Observation Notes")

        st.markdown("#### Final Atmospheric Conditions")
        stop_temp = st.number_input("Final Temperature (°C)", step=0.1)
        stop_rh = st.number_input("Final Relative Humidity (%)", step=0.1)
        stop_pressure = st.number_input("Final Pressure (hPa)", step=0.1)
        stop_weather = st.text_input("Final Weather")
        stop_wind = st.text_input("Final Wind Speed and Direction")

        st.markdown("#### Sampler Information")
        stop_elapsed = st.number_input("Final Elapsed Time (min)", step=1)
        stop_flow = st.number_input("Final Flow Rate (L/min)", step=0.1)
        stop_time = st.time_input("Stop Time", value=datetime.now().time())

        submit_stop = st.form_submit_button("Submit Stop Day Data")
        if submit_stop:
            if all([id_selected, site_selected, officer_selected, driver_name]):
                for officer in officer_selected:
                    stop_row = [
                        "STOP", id_selected, site_selected, officer, driver_name,
                        stop_date.strftime("%Y-%m-%d"), stop_time.strftime("%H:%M:%S"),
                        stop_temp, stop_rh, stop_pressure, stop_weather, stop_wind,
                        stop_elapsed, stop_flow, stop_obs
                    ]
                    add_data(stop_row)
                st.success("Stop day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Display Merged Start/Stop Data ===
st.header("📋 Merged Monitoring Records (Start & Stop)")
df = read_data()
if df.empty:
    st.info("No data submitted yet.")
else:
    try:
        merged_df = merge_start_stop(df)
        st.dataframe(merged_df, use_container_width=True)
    except Exception as e:
        st.error("Error merging data. Please ensure matching START/STOP entries exist.")
