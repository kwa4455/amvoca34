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
        "Entry Type", "ID", "Site", "Monitoring Officer", "Driver",
        "Date", "Time", "Temperature (°C)", "RH (%)", "Pressure (hPa)",
        "Weather", "Wind", "Elapsed Time (min)", "Flow Rate (L/min)", "Observation",
        "Submitted At"
    ])

# === Functions ===
def load_data_from_sheet(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["Submitted At"] = pd.to_datetime(df["Submitted At"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def add_data(row):
    row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Timestamp
    sheet.append_row(row)

def merge_start_stop(df):
    # Separate START and STOP records
    start_df = df[df["Entry Type"] == "START"].copy()
    stop_df = df[df["Entry Type"] == "STOP"].copy()

    # Ensure common key for merging (e.g., ID and Site)
    merge_keys = ["ID", "Site"]

    # Rename columns to distinguish between START and STOP
    start_df = start_df.rename(columns=lambda x: f"{x}_Start" if x not in merge_keys else x)
    stop_df = stop_df.rename(columns=lambda x: f"{x}_Stop" if x not in merge_keys else x)

    # Merge START and STOP records on ID and Site
    merged_df = pd.merge(start_df, stop_df, on=merge_keys, how="inner")

    # Calculate elapsed time difference if columns exist
    if "Elapsed Time (min)_Start" in merged_df.columns and "Elapsed Time (min)_Stop" in merged_df.columns:
        merged_df["Elapsed Time Diff (min)"] = (
            merged_df["Elapsed Time (min)_Stop"] - merged_df["Elapsed Time (min)_Start"]
        )

    return merged_df

def save_merged_data_to_sheet(df, spreadsheet, sheet_name):
    if sheet_name in [ws.title for ws in spreadsheet.worksheets()]:
        sheet = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(sheet)
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="50")
    sheet.update([df.columns.tolist()] + df.values.tolist())




# === Streamlit UI ===
st.set_page_config(page_title="EPA Ghana | PM₂.₅ Monitoring", layout="wide")

# --- Custom CSS + Google Fonts ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }

        .stButton>button {
            background-color: #006400;
            color: white;
            font-weight: bold;
        }

        .stButton>button:hover {
            background-color: #004d00;
        }

        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar with Developer Info and Logo ---
with st.sidebar:
    
    st.markdown("---")
    st.markdown("### 📞 For any Information, Please Contact")
    st.markdown("### 👤 The Developer")
    st.markdown("**Clement Mensah Ackaah**  \nEnvironmental Data Analyst")
    st.markdown("[📧 Email 1](mailto:clement.ackaah@epa.gov.gh) | [📧 Email 2](mailto:clementackaah70@gmail.com)")
    st.markdown("[🌐 Website](https://epa.gov)")

    st.markdown("---")
    

# --- Page Title ---
st.title("🇬🇭 EPA Ghana | PM₂.₅ Monitoring Data Entry")

ids = ["",'1', '2', '3','4','5','6','7','8','9','10']
sites = ["",'Kaneshie First Light', 'Tetteh Quarshie', 'Achimota', 'La','Mallam Market','Graphic Road','Weija','Tantra Hill', 'Amasaman']
officers = ['Obed', 'Clement', 'Peter','Ben','Mawuli']

# Entry Type Selection
entry_type = st.selectbox("Select Entry Type", ["", "START", "STOP"])

if entry_type:
    id_selected = st.selectbox("Select Site ID", ids)
    site_selected = st.selectbox("Select Site", sites)
    officer_selected = st.multiselect("Monitoring Officer(s)", officers)
    driver_name = st.text_input("Driver's Name")

# === Start Day Observation ===
if entry_type == "START":
    with st.expander("Start Day Monitoring", expanded=True):
        start_date = st.date_input("Start Date", value=datetime.today())
        start_obs = st.text_area("First Day Observation")

        st.markdown("#### Initial Atmospheric Conditions")
        start_temp = st.number_input("Temperature (°C)", step=0.1)
        start_rh = st.number_input("Relative Humidity (%)", step=0.1)
        start_pressure = st.number_input("Pressure (hPa)", step=0.1)
        start_weather = st.text_input("Weather")
        start_wind = st.text_input("Wind Speed and Direction")

        st.markdown("#### Initial Sampler Information")
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
    with st.expander("Stop Day Monitoring", expanded=True):
        stop_date = st.date_input("Stop Date", value=datetime.today())
        stop_obs = st.text_area("Final Day Observation")

        st.markdown("#### Final Atmospheric Conditions")
        stop_temp = st.number_input("Final Temperature (°C)", step=0.1)
        stop_rh = st.number_input("Final Relative Humidity (%)", step=0.1)
        stop_pressure = st.number_input("Final Pressure (hPa)", step=0.1)
        stop_weather = st.text_input("Final Weather")
        stop_wind = st.text_input("Final Wind Speed and Direction")

        st.markdown("#### Final Sampler Information")
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
        id_filter = st.selectbox("Filter by Site", ["All"] + sorted(df["Site"].unique().tolist()))
        date_range = st.date_input("Filter by Date Range", [])

        if id_filter != "All":
            df = df[df["Site"] == id_filter]
        if len(date_range) == 2:
            start, end = date_range
            df = df[(df["Submitted At"].dt.date >= start) & (df["Submitted At"].dt.date <= end)]

    st.dataframe(df, use_container_width=True)
    
    df = load_data_from_sheet(sheet)

    
    merged_df = merge_start_stop(df)
    if not merged_df.empty:
        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=MERGED_SHEET)
        st.success("Merged records saved to Google Sheets.")
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.warning("No matching START and STOP records found to merge.")

with st.sidebar:
    sentiment_mapping = ["one", "two", "three", "four", "five"]
    selected = st.feedback("stars")
    if selected is not None:
        st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")


with st.expander("✏️ Edit Submitted Records"):
   

    if not df.empty:
        df["Row Number"] = df.index + 2  # Adjust for header row in Google Sheets

        # Create a unique identifier
        df["Record ID"] = df.apply(
            lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
            axis=1
        )

        selected_record = st.selectbox("Select a record to edit:", df["Record ID"].tolist())

        if selected_record:
            selected_index = df[df["Record ID"] == selected_record].index[0]
            record_data = df.loc[selected_index]
            row_number = record_data["Row Number"]

            with st.form("edit_form"):
                entry_type = st.selectbox("Entry Type", ["START", "STOP"], index=["START", "STOP"].index(record_data["Entry Type"]))
                site_id = st.text_input("ID", value=record_data["ID"])
                site = st.text_input("Site", value=record_data["Site"])
                monitoring_officer = st.text_input("Monitoring Officer", value=record_data["Monitoring Officer"])
                driver = st.text_input("Driver", value=record_data["Driver"])
                date = st.date_input("Date", value=pd.to_datetime(record_data["Date"]))
                time = st.time_input("Time", value=pd.to_datetime(record_data["Time"]).time())
                temperature = st.number_input("Temperature (°C)", value=float(record_data["Temperature (°C)"]), step=0.1)
                rh = st.number_input("Relative Humidity (%)", value=float(record_data["RH (%)"]), step=0.1)
                pressure = st.number_input("Pressure (hPa)", value=float(record_data["Pressure (hPa)"]), step=0.1)
                weather = st.text_input("Weather", value=record_data["Weather"])
                wind = st.text_input("Wind", value=record_data["Wind"])
                elapsed_time = st.number_input("Elapsed Time (min)", value=float(record_data["Elapsed Time (min)"]), step=1.0)
                flow_rate = st.number_input("Flow Rate (L/min)", value=float(record_data["Flow Rate (L/min)"]), step=0.1)
                observation_value = record_data["Observation"] if "Observation" in record_data else ""
                observation = st.text_area("Observation", value=observation_value)
                submitted = st.form_submit_button("Update Record")

                if submitted:
                    updated_data = [
                        entry_type, site_id, site, monitoring_officer, driver,
                        date.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"),
                        temperature, rh, pressure, weather, wind,
                        elapsed_time, flow_rate, observation
                    ]

                    for col_index, value in enumerate(updated_data, start=1):
                        sheet.update_cell(row_number, col_index, value)

                    
                    df = load_data_from_sheet(sheet)
                    df["Row Number"] = df.index + 2
                    df["Record ID"] = df.apply(
                        lambda x: f"{x['Entry Type']} | {x['ID']} | {x['Site']} | {x['Submitted At'].strftime('%Y-%m-%d %H:%M')}",
                        axis=1
                    )
                    merged_df = merge_start_stop(df)
                    if not merged_df.empty:
                        save_merged_data_to_sheet(merged_df, spreadsheet, sheet_name=MERGED_SHEET)
                        st.success("Merged records saved to Google Sheets.")
                        st.dataframe(merged_df, use_container_width=True)
                    else:
                        st.warning("No matching START and STOP records found to merge.")
                    

st.markdown("""
    <hr style="margin-top: 40px; margin-bottom:10px">
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        © 2025 EPA Ghana· Developed by Clement Mensah Ackaah· Built with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)

