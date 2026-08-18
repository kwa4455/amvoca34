import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from io import BytesIO
import zipfile


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Air Quality Automatic Data Generator",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #555;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🌍 Air Quality Automatic Data Generator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Generate hourly air-quality monitoring data using '
    'user-defined locations, dates, coordinates and pollutant ranges.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Generator Settings")


# ============================================================
# LOCATION INFORMATION
# ============================================================

st.sidebar.markdown("### 📍 Location Information")

location_id = st.sidebar.text_input(
    "Location ID",
    value="001"
)

location_name = st.sidebar.text_input(
    "Location Name",
    value="Monitoring Site 1"
)

location_type_option = st.sidebar.selectbox(
    "Location Type",
    [
        "Urban",
        "Industrial",
        "Residential",
        "Commercial",
        "Traffic",
        "Background",
        "Rural",
        "Other"
    ]
)

if location_type_option == "Other":

    location_type = st.sidebar.text_input(
        "Enter Location Type",
        value=""
    )

else:

    location_type = location_type_option


# ============================================================
# SENSOR INFORMATION
# ============================================================

st.sidebar.markdown("### 📡 Sensor Information")

sensor_id = st.sidebar.text_input(
    "Sensor ID",
    value=f"SENSOR_{location_id}"
)


# ============================================================
# COORDINATES
# ============================================================

st.sidebar.markdown("### 🌐 Coordinates")

latitude = st.sidebar.number_input(
    "Latitude",
    min_value=-90.0,
    max_value=90.0,
    value=5.603700,
    step=0.000001,
    format="%.6f"
)

longitude = st.sidebar.number_input(
    "Longitude",
    min_value=-180.0,
    max_value=180.0,
    value=-0.187000,
    step=0.000001,
    format="%.6f"
)


# ============================================================
# DATE RANGE
# ============================================================

st.sidebar.markdown("### 📅 Date Range")

start_date = st.sidebar.date_input(
    "Start Date",
    value=date(2026, 1, 1)
)

end_date = st.sidebar.date_input(
    "End Date",
    value=date(2026, 1, 7)
)


# ============================================================
# TIME ZONE
# ============================================================

st.sidebar.markdown("### 🕐 Time Zone")

timezone_name = st.sidebar.selectbox(
    "Local Time Zone",
    [
        "Africa/Accra",
        "Africa/Lagos",
        "Africa/Nairobi",
        "Africa/Johannesburg",
        "UTC"
    ],
    index=0
)


# ============================================================
# PLACE OPENING HOURS
# ============================================================

st.sidebar.markdown("### 🏢 Place Opening Hours")

place_open_option = st.sidebar.selectbox(
    "Opening Schedule",
    [
        "24/7",
        "Custom Hours"
    ]
)


if place_open_option == "24/7":

    opening_time = time(0, 0)

    closing_time = time(23, 59)

else:

    opening_time = st.sidebar.time_input(
        "Opening Time",
        value=time(6, 0)
    )

    closing_time = st.sidebar.time_input(
        "Closing Time",
        value=time(18, 0)
    )


# ============================================================
# POLLUTANT RANGES
# ============================================================

st.sidebar.markdown("### 🧪 Pollutant Ranges")


# ------------------------------------------------------------
# PM2.5
# ------------------------------------------------------------

st.sidebar.write("**PM2.5**")

pm25_min = st.sidebar.number_input(
    "PM2.5 Minimum",
    min_value=0.0,
    value=5.0,
    step=0.1
)

pm25_max = st.sidebar.number_input(
    "PM2.5 Maximum",
    min_value=0.0,
    value=80.0,
    step=0.1
)


# ------------------------------------------------------------
# PM1
# ------------------------------------------------------------

st.sidebar.write("**PM1**")

pm1_min = st.sidebar.number_input(
    "PM1 Minimum",
    min_value=0.0,
    value=2.0,
    step=0.1
)

pm1_max = st.sidebar.number_input(
    "PM1 Maximum",
    min_value=0.0,
    value=50.0,
    step=0.1
)


# ------------------------------------------------------------
# PM10
# ------------------------------------------------------------

st.sidebar.write("**PM10**")

pm10_min = st.sidebar.number_input(
    "PM10 Minimum",
    min_value=0.0,
    value=10.0,
    step=0.1
)

pm10_max = st.sidebar.number_input(
    "PM10 Maximum",
    min_value=0.0,
    value=150.0,
    step=0.1
)


# ============================================================
# TEMPERATURE
# ============================================================

st.sidebar.markdown("### 🌡️ Temperature")

temperature_min = st.sidebar.number_input(
    "Temperature Minimum (°C)",
    value=20.0,
    step=0.1
)

temperature_max = st.sidebar.number_input(
    "Temperature Maximum (°C)",
    value=35.0,
    step=0.1
)


# ============================================================
# HUMIDITY
# ============================================================

st.sidebar.markdown("### 💧 Humidity")

humidity_min = st.sidebar.number_input(
    "Humidity Minimum (%)",
    min_value=0.0,
    max_value=100.0,
    value=40.0,
    step=0.1
)

humidity_max = st.sidebar.number_input(
    "Humidity Maximum (%)",
    min_value=0.0,
    max_value=100.0,
    value=90.0,
    step=0.1
)


# ============================================================
# RANDOM SEED
# ============================================================

st.sidebar.markdown("### 🎲 Randomization")

random_seed = st.sidebar.number_input(
    "Random Seed",
    min_value=1,
    value=12345,
    step=1
)


# ============================================================
# GENERATE FUNCTION
# ============================================================

def generate_data():

    rng = np.random.default_rng(
        int(random_seed)
    )

    # --------------------------------------------------------
    # TIMEZONE
    # --------------------------------------------------------

    tz = ZoneInfo(
        timezone_name
    )

    # --------------------------------------------------------
    # START AND END DATETIME
    # --------------------------------------------------------

    start_datetime = datetime.combine(
        start_date,
        time(0, 0)
    )

    end_datetime = datetime.combine(
        end_date,
        time(23, 0)
    )

    # --------------------------------------------------------
    # HOURLY TIMESTAMPS
    # --------------------------------------------------------

    timestamps = pd.date_range(
        start=start_datetime,
        end=end_datetime,
        freq="h"
    )

    records = []


    # ========================================================
    # GENERATE EACH HOUR
    # ========================================================

    for ts in timestamps:

        current_date = ts.date()

        current_hour = ts.hour

        current_time = time(
            current_hour,
            0
        )


        # ----------------------------------------------------
        # DETERMINE WHETHER PLACE IS OPEN
        # ----------------------------------------------------

        if place_open_option == "24/7":

            place_open = "Yes"

        else:

            if opening_time <= closing_time:

                is_open = (
                    current_time >= opening_time
                    and
                    current_time <= closing_time
                )

            else:

                # Opening period crosses midnight

                is_open = (
                    current_time >= opening_time
                    or
                    current_time <= closing_time
                )

            place_open = (
                "Yes"
                if is_open
                else "No"
            )


        # ----------------------------------------------------
        # LOCAL DATETIME
        # ----------------------------------------------------

        local_dt = datetime(
            current_date.year,
            current_date.month,
            current_date.day,
            current_hour,
            0,
            0,
            tzinfo=tz
        )


        # ----------------------------------------------------
        # UTC DATETIME
        # ----------------------------------------------------

        utc_dt = local_dt.astimezone(
            ZoneInfo("UTC")
        )


        # ====================================================
        # GENERATE PM DATA
        # ====================================================

        # Generate PM1 first

        pm1 = rng.uniform(
            pm1_min,
            pm1_max
        )


        # Generate PM2.5 ensuring:
        #
        # PM2.5 >= PM1
        #

        pm25_lower = max(
            pm25_min,
            pm1
        )

        pm25_upper = pm25_max


        if pm25_lower <= pm25_upper:

            pm25 = rng.uniform(
                pm25_lower,
                pm25_upper
            )

        else:

            pm25 = pm25_upper


        # ----------------------------------------------------
        # Generate PM10 ensuring:
        #
        # PM10 >= PM2.5
        # ----------------------------------------------------

        pm10_lower = max(
            pm10_min,
            pm25
        )

        pm10_upper = pm10_max


        if pm10_lower <= pm10_upper:

            pm10 = rng.uniform(
                pm10_lower,
                pm10_upper
            )

        else:

            pm10 = pm10_upper


        # ====================================================
        # METEOROLOGICAL DATA
        # ====================================================

        temperature = rng.uniform(
            temperature_min,
            temperature_max
        )

        humidity = rng.uniform(
            humidity_min,
            humidity_max
        )


        # ====================================================
        # CREATE RECORD
        # ====================================================

        record = {

            "Location ID":
                location_id,

            "Location Name":
                location_name,

            "Location Type":
                location_type,

            "Sensor ID":
                sensor_id,

            "Place Open":
                place_open,

            "Local Date/Time":
                local_dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "UTC Date/Time":
                utc_dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "PM2.5":
                round(pm25, 2),

            "Temperature (C)":
                round(temperature, 2),

            "Humidity (%)":
                round(humidity, 2),

            "PM1":
                round(pm1, 2),

            "PM10":
                round(pm10, 2),

            "latitude":
                round(latitude, 6),

            "longitude":
                round(longitude, 6)
        }


        records.append(
            record
        )


    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        records
    )


    # ========================================================
    # FORCE COLUMN ORDER
    # ========================================================

    columns = [

        "Location ID",
        "Location Name",
        "Location Type",
        "Sensor ID",
        "Place Open",
        "Local Date/Time",
        "UTC Date/Time",
        "PM2.5",
        "Temperature (C)",
        "Humidity (%)",
        "PM1",
        "PM10",
        "latitude",
        "longitude"

    ]

    df = df[
        columns
    ]


    return df


# ============================================================
# VALIDATION
# ============================================================

errors = []


if not str(location_id).strip():

    errors.append(
        "Location ID cannot be empty."
    )


if not str(location_name).strip():

    errors.append(
        "Location Name cannot be empty."
    )


if not str(location_type).strip():

    errors.append(
        "Location Type cannot be empty."
    )


if not str(sensor_id).strip():

    errors.append(
        "Sensor ID cannot be empty."
    )


if end_date < start_date:

    errors.append(
        "End Date must be greater than or equal to Start Date."
    )


if pm25_max < pm25_min:

    errors.append(
        "PM2.5 maximum must be greater than or equal to minimum."
    )


if pm1_max < pm1_min:

    errors.append(
        "PM1 maximum must be greater than or equal to minimum."
    )


if pm10_max < pm10_min:

    errors.append(
        "PM10 maximum must be greater than or equal to minimum."
    )


if temperature_max < temperature_min:

    errors.append(
        "Temperature maximum must be greater than or equal to minimum."
    )


if humidity_max < humidity_min:

    errors.append(
        "Humidity maximum must be greater than or equal to minimum."
    )


# ============================================================
# GENERATE DATA
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🚀 Generate Dataset'
    '</div>',
    unsafe_allow_html=True
)


if errors:

    for error in errors:

        st.error(
            error
        )

else:

    generate_button = st.button(
        "🚀 Generate Hourly Data",
        type="primary",
        use_container_width=True
    )


    if generate_button:

        with st.spinner(
            "Generating hourly air-quality data..."
        ):

            df = generate_data()

            st.session_state[
                "generated_data"
            ] = df


        st.success(
            f"Successfully generated "
            f"{len(df):,} hourly records."
        )


# ============================================================
# DISPLAY GENERATED DATA
# ============================================================

if "generated_data" in st.session_state:

    df = st.session_state[
        "generated_data"
    ]


    # ========================================================
    # SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📊 Dataset Summary'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            "Records",
            f"{len(df):,}"
        )


    with col2:

        st.metric(
            "Location",
            location_name
        )


    with col3:

        st.metric(
            "Sensor",
            sensor_id
        )


    with col4:

        st.metric(
            "Latitude",
            f"{latitude:.6f}"
        )


    with col5:

        st.metric(
            "Longitude",
            f"{longitude:.6f}"
        )


    # ========================================================
    # DATA PREVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '👁️ Generated Data'
        '</div>',
        unsafe_allow_html=True
    )


    st.dataframe(
        df,
        use_container_width=True,
        height=550
    )


    # ========================================================
    # POLLUTANT SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📈 Pollutant Summary'
        '</div>',
        unsafe_allow_html=True
    )


    summary_columns = [

        "PM2.5",
        "PM1",
        "PM10",
        "Temperature (C)",
        "Humidity (%)"

    ]


    summary = (
        df[
            summary_columns
        ]
        .describe()
        .T
        .round(2)
    )


    st.dataframe(
        summary,
        use_container_width=True
    )


    # ========================================================
    # FILE NAMES
    # ========================================================

    csv_filename = (

        f"air_quality_"
        f"{location_id}_"
        f"{start_date}_"
        f"{end_date}.csv"

    )


    zip_filename = (

        f"air_quality_"
        f"{location_id}_"
        f"{start_date}_"
        f"{end_date}.zip"

    )


    # ========================================================
    # CREATE CSV
    # ========================================================

    csv_data = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    # ========================================================
    # CREATE ZIP
    # ========================================================

    zip_buffer = BytesIO()


    with zipfile.ZipFile(

        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED

    ) as zip_file:

        zip_file.writestr(
            csv_filename,
            csv_data
        )


    zip_buffer.seek(0)


    # ========================================================
    # DOWNLOAD SECTION
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '💾 Download Data'
        '</div>',
        unsafe_allow_html=True
    )


    col_download1, col_download2 = st.columns(2)


    # ========================================================
    # ZIP DOWNLOAD
    # ========================================================

    with col_download1:

        st.download_button(

            label="📦 Download CSV ZIP File",

            data=zip_buffer.getvalue(),

            file_name=zip_filename,

            mime="application/zip",

            use_container_width=True

        )


    # ========================================================
    # DIRECT CSV DOWNLOAD
    # ========================================================

    with col_download2:

        st.download_button(

            label="📄 Download CSV",

            data=csv_data,

            file_name=csv_filename,

            mime="text/csv",

            use_container_width=True

        )


    # ========================================================
    # FILE INFORMATION
    # ========================================================

    st.info(
        f"ZIP file contains: **{csv_filename}**"
    )


    # ========================================================
    # CHECK PM RELATIONSHIP
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔍 Data Quality Check'
        '</div>',
        unsafe_allow_html=True
    )


    pm_relationship = (

        (df["PM1"] <= df["PM2.5"]) &
        (df["PM2.5"] <= df["PM10"])

    )


    valid_relationship = (
        pm_relationship.sum()
    )

    total_records = len(df)


    col_qc1, col_qc2, col_qc3 = st.columns(3)


    with col_qc1:

        st.metric(
            "Valid PM Relationships",
            f"{valid_relationship:,}"
        )


    with col_qc2:

        st.metric(
            "Total Records",
            f"{total_records:,}"
        )


    with col_qc3:

        percentage = (

            valid_relationship /
            total_records *
            100

        )

        st.metric(
            "Valid (%)",
            f"{percentage:.1f}%"
        )


    if valid_relationship == total_records:

        st.success(
            "✓ All records satisfy "
            "PM1 ≤ PM2.5 ≤ PM10."
        )

    else:

        st.warning(
            "Some records do not satisfy "
            "PM1 ≤ PM2.5 ≤ PM10."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Air Quality Automatic Data Generator | "
    "Hourly synthetic monitoring data"
)
