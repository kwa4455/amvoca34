import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# === Google Sheets Setup ===
creds_json = st.secrets["GOOGLE_CREDENTIALS"]
creds_dict = json.loads(creds_json)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1jCV-IqALZz7wKqjqc5ISrkA_dv35mX1ZowNqwFHf6mk"
MAIN_SHEET = 'Observations'
MERGED_SHEET = 'Merged Records'

spreadsheet = client.open_by_key(SPREADSHEET_ID)

# Ensure Observations worksheet exists
try:
    sheet = spreadsheet.worksheet(MAIN_SHEET)
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=MAIN_SHEET, rows="100", cols="20")
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
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Timestamp
    sheet.append_row(row)

def merge_start_stop(df):
    df = df.sort_values("Submitted At")
    start_df = df[df["Entry Type"] == "START"]
    stop_df = df[df["Entry Type"] == "STOP"]

    merged = pd.merge(
        start_df,
        stop_df,
        on=["Operator ID", "Site", "Monitoring Officer", "Driver"],
        suffixes=("_start", "_stop"),
        how="inner"
    )

    merged["Elapsed Diff (min)"] = merged["Elapsed Time (min)_stop"] - merged["Elapsed Time (min)_start"]
    return merged

def save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=MERGED_SHEET_NAME):
    try:
        merged_sheet = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(merged_sheet)
    except gspread.WorksheetNotFound:
        pass
    merged_sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
    merged_sheet.append_row(merged_df.columns.tolist())
    for _, row in merged_df.iterrows():
        merged_sheet.append_row(row.astype(str).tolist())

# === Streamlit UI ===
st.title("PM2.5 Monitoring Data Entry")

ids = ["",'ID001', 'ID002', 'ID003']
sites = ["",'Site A', 'Site B', 'Site C']
officers = ['Officer 1', 'Officer 2', 'Officer 3']

# Entry Type Selection
entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])

# Conditional Display of ID and Site
if entry_type:
    id_selected = st.selectbox("Select Operator ID", ids)
    site_selected = st.selectbox("Select Site", sites)

officer_selected = st.multiselect("Monitoring Officer(s)", officers)
driver_name = st.text_input("Driver's Name")

# === Start Day Observation ===
if entry_type == "START":
    with st.expander("Start Day Observation", expanded=True):
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

        if st.button("Submit Start Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                start_row = [
                    "START", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    start_date.strftime("%Y-%m-%d"), start_time.strftime("%H:%M:%S"),
                    start_temp, start_rh, start_pressure, start_weather, start_wind,
                    start_elapsed, start_flow, start_obs
                ]
                add_data(start_row)
                st.success("Start day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Stop Day Observation ===
elif entry_type == "STOP":
    with st.expander("Stop Day Observation", expanded=True):
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

        if st.button("Submit Stop Day Data"):
            if all([id_selected, site_selected, officer_selected, driver_name]):
                stop_row = [
                    "STOP", id_selected, site_selected, ", ".join(officer_selected), driver_name,
                    stop_date.strftime("%Y-%m-%d"), stop_time.strftime("%H:%M:%S"),
                    stop_temp, stop_rh, stop_pressure, stop_weather, stop_wind,
                    stop_elapsed, stop_flow, stop_obs
                ]
                add_data(stop_row)
                st.success("Stop day data submitted successfully!")
            else:
                st.error("Please complete all required fields.")

# === Display & Merge Records ===
st.header("Submitted Monitoring Records")
df = read_data()

if df.empty:
    st.info("No data submitted yet.")
else:
    with st.expander("🔍 Filter Records"):
        id_filter = st.selectbox("Filter by Operator ID", ["All"] + sorted(df["Operator ID"].unique().tolist()))
        date_range = st.date_input("Filter by Date Range", [])

        if id_filter != "All":
            df = df[df["Operator ID"] == id_filter]
        if len(date_range) == 2:
            start, end = date_range
            df = df[(df["Submitted At"].dt.date >= start) & (df["Submitted At"].dt.date <= end)]

    st.dataframe(df, use_container_width=True)

    
