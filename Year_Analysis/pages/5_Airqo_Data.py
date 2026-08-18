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
    page_title="Ghana Air Quality Automatic Data Generator",
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

    .season-box {
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
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
    '🌍 Ghana Air Quality Automatic Data Generator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Generate hourly synthetic air-quality monitoring data '
    'using Ghana-specific seasonal patterns.'
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
# SENSOR
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
# GHANA REGION
# ============================================================

st.sidebar.markdown("### 🇬🇭 Ghana Seasonal Region")

region = st.sidebar.selectbox(
    "Select Region",
    [
        "Southern Ghana",
        "Northern Ghana"
    ]
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
# TIMEZONE
# ============================================================

st.sidebar.markdown("### 🕐 Time Zone")

timezone_name = st.sidebar.selectbox(
    "Local Time Zone",
    [
        "Africa/Accra",
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
# SEASON MODE
# ============================================================

st.sidebar.markdown("### 🌦️ Season Selection")

season_mode = st.sidebar.selectbox(
    "How should the season be determined?",
    [
        "Automatic based on month",
        "Harmattan",
        "Wet Season",
        "Dry Season",
        "Custom Season"
    ]
)


# ============================================================
# SEASONAL INFORMATION
# ============================================================

with st.expander(
    "ℹ️ Ghana seasonal classification",
    expanded=False
):

    st.write(
        """
        **Southern Ghana**

        - Harmattan: December–February
        - Major Wet Season: March–July
        - Little Dry Season: August
        - Minor Wet Season: September–November

        **Northern Ghana**

        - Harmattan/Dry Season: December–March
        - Wet Season: April–October
        """
    )


# ============================================================
# DEFAULT SEASONAL RANGES
# ============================================================

# These are simulation defaults.
#
# They are NOT official Ghana air-quality standards.
# Users can change all values.


DEFAULT_SEASONS = {

    "Harmattan": {

        "pm1_min": 5.0,
        "pm1_max": 80.0,

        "pm25_min": 10.0,
        "pm25_max": 120.0,

        "pm10_min": 20.0,
        "pm10_max": 250.0,

        "temp_min": 22.0,
        "temp_max": 35.0,

        "humidity_min": 25.0,
        "humidity_max": 70.0
    },

    "Wet Season": {

        "pm1_min": 1.0,
        "pm1_max": 40.0,

        "pm25_min": 3.0,
        "pm25_max": 60.0,

        "pm10_min": 5.0,
        "pm10_max": 120.0,

        "temp_min": 23.0,
        "temp_max": 32.0,

        "humidity_min": 60.0,
        "humidity_max": 98.0
    },

    "Dry Season": {

        "pm1_min": 3.0,
        "pm1_max": 60.0,

        "pm25_min": 5.0,
        "pm25_max": 90.0,

        "pm10_min": 10.0,
        "pm10_max": 180.0,

        "temp_min": 24.0,
        "temp_max": 36.0,

        "humidity_min": 35.0,
        "humidity_max": 80.0
    }

}


# ============================================================
# CUSTOM SEASON
# ============================================================

custom_season_name = "Custom"

if season_mode == "Custom Season":

    st.sidebar.markdown("### ✏️ Custom Season")

    custom_season_name = st.sidebar.text_input(
        "Season Name",
        value="Custom Season"
    )


# ============================================================
# SEASONAL RANGE INPUT
# ============================================================

st.sidebar.markdown("### 🧪 Pollutant Ranges")

st.sidebar.caption(
    "Ranges are used to generate synthetic hourly observations."
)


# ============================================================
# DEFAULT VALUES FOR RANGE CONTROLS
# ============================================================

if season_mode == "Harmattan":

    default = DEFAULT_SEASONS["Harmattan"]

elif season_mode == "Wet Season":

    default = DEFAULT_SEASONS["Wet Season"]

elif season_mode == "Dry Season":

    default = DEFAULT_SEASONS["Dry Season"]

else:

    default = DEFAULT_SEASONS["Wet Season"]


# ============================================================
# PM1
# ============================================================

st.sidebar.write("**PM1**")

pm1_min = st.sidebar.number_input(
    "PM1 Minimum",
    min_value=0.0,
    value=float(default["pm1_min"]),
    step=0.1
)

pm1_max = st.sidebar.number_input(
    "PM1 Maximum",
    min_value=0.0,
    value=float(default["pm1_max"]),
    step=0.1
)


# ============================================================
# PM2.5
# ============================================================

st.sidebar.write("**PM2.5**")

pm25_min = st.sidebar.number_input(
    "PM2.5 Minimum",
    min_value=0.0,
    value=float(default["pm25_min"]),
    step=0.1
)

pm25_max = st.sidebar.number_input(
    "PM2.5 Maximum",
    min_value=0.0,
    value=float(default["pm25_max"]),
    step=0.1
)


# ============================================================
# PM10
# ============================================================

st.sidebar.write("**PM10**")

pm10_min = st.sidebar.number_input(
    "PM10 Minimum",
    min_value=0.0,
    value=float(default["pm10_min"]),
    step=0.1
)

pm10_max = st.sidebar.number_input(
    "PM10 Maximum",
    min_value=0.0,
    value=float(default["pm10_max"]),
    step=0.1
)


# ============================================================
# TEMPERATURE
# ============================================================

st.sidebar.markdown("### 🌡️ Temperature")

temperature_min = st.sidebar.number_input(
    "Temperature Minimum (°C)",
    value=float(default["temp_min"]),
    step=0.1
)

temperature_max = st.sidebar.number_input(
    "Temperature Maximum (°C)",
    value=float(default["temp_max"]),
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
    value=float(default["humidity_min"]),
    step=0.1
)

humidity_max = st.sidebar.number_input(
    "Humidity Maximum (%)",
    min_value=0.0,
    max_value=100.0,
    value=float(default["humidity_max"]),
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
# SEASON FUNCTION
# ============================================================

def determine_season(
    current_month,
    selected_mode,
    selected_region
):

    # --------------------------------------------------------
    # USER FORCED SEASON
    # --------------------------------------------------------

    if selected_mode == "Harmattan":

        return "Harmattan"

    if selected_mode == "Wet Season":

        return "Wet Season"

    if selected_mode == "Dry Season":

        return "Dry Season"

    if selected_mode == "Custom Season":

        return custom_season_name


    # --------------------------------------------------------
    # AUTOMATIC SOUTHERN GHANA
    # --------------------------------------------------------

    if selected_region == "Southern Ghana":

        if current_month in [12, 1, 2]:

            return "Harmattan"

        elif current_month in [3, 4, 5, 6, 7]:

            return "Wet Season"

        elif current_month == 8:

            return "Dry Season"

        elif current_month in [9, 10, 11]:

            return "Wet Season"


    # --------------------------------------------------------
    # AUTOMATIC NORTHERN GHANA
    # --------------------------------------------------------

    if selected_region == "Northern Ghana":

        if current_month in [12, 1, 2, 3]:

            return "Harmattan"

        elif current_month in [4, 5, 6, 7, 8, 9, 10]:

            return "Wet Season"

        elif current_month == 11:

            return "Dry Season"


    return "Dry Season"


# ============================================================
# GENERATE DATA FUNCTION
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
    # DATE RANGE
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
    # LOOP THROUGH EVERY HOUR
    # ========================================================

    for ts in timestamps:

        current_date = ts.date()

        current_hour = ts.hour


        # ----------------------------------------------------
        # DETERMINE SEASON
        # ----------------------------------------------------

        season = determine_season(
            current_date.month,
            season_mode,
            region
        )


        # ----------------------------------------------------
        # PLACE OPEN
        # ----------------------------------------------------

        current_time = time(
            current_hour,
            0
        )


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
        # LOCAL TIME
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
        # UTC TIME
        # ----------------------------------------------------

        utc_dt = local_dt.astimezone(
            ZoneInfo("UTC")
        )


        # ====================================================
        # PARTICULATE MATTER
        # ====================================================

        # PM1
        pm1 = rng.uniform(
            pm1_min,
            pm1_max
        )


        # ----------------------------------------------------
        # PM2.5
        # ----------------------------------------------------

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
        # PM10
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
        # METEOROLOGICAL VARIABLES
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
                round(longitude, 6),

            "Season":
                season

        }


        records.append(
            record
        )


    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        records
    )


    # ========================================================
    # COLUMN ORDER
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
        "longitude",
        "Season"

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


if pm1_max < pm1_min:

    errors.append(
        "PM1 maximum must be greater than or equal to PM1 minimum."
    )


if pm25_max < pm25_min:

    errors.append(
        "PM2.5 maximum must be greater than or equal to PM2.5 minimum."
    )


if pm10_max < pm10_min:

    errors.append(
        "PM10 maximum must be greater than or equal to PM10 minimum."
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
# CHECK PM RANGE COMPATIBILITY
# ============================================================

if pm1_max > pm25_max:

    errors.append(
        "PM1 maximum cannot be greater than PM2.5 maximum "
        "when enforcing PM1 ≤ PM2.5 ≤ PM10."
    )


if pm25_max > pm10_max:

    errors.append(
        "PM2.5 maximum cannot be greater than PM10 maximum "
        "when enforcing PM1 ≤ PM2.5 ≤ PM10."
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

        st.error(error)

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
# DISPLAY DATA
# ============================================================

if "generated_data" in st.session_state:

    df = st.session_state[
        "generated_data"
    ]


    # ========================================================
    # SUMMARY METRICS
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
    # SEASON SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🌦️ Season Summary'
        '</div>',
        unsafe_allow_html=True
    )


    season_summary = (
        df["Season"]
        .value_counts()
        .rename_axis("Season")
        .reset_index(
            name="Hourly Records"
        )
    )


    season_summary["Percentage"] = (
        season_summary["Hourly Records"]
        /
        len(df)
        *
        100
    ).round(2)


    st.dataframe(
        season_summary,
        use_container_width=True,
        hide_index=True
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
        '📈 Overall Summary Statistics'
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
    # SEASONAL SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🌦️ Pollutant Summary by Season'
        '</div>',
        unsafe_allow_html=True
    )


    seasonal_summary = (
        df.groupby("Season")[
            [
                "PM1",
                "PM2.5",
                "PM10",
                "Temperature (C)",
                "Humidity (%)"
            ]
        ]
        .agg(
            [
                "count",
                "mean",
                "median",
                "min",
                "max"
            ]
        )
        .round(2)
    )


    st.dataframe(
        seasonal_summary,
        use_container_width=True
    )


    # ========================================================
    # DOWNLOAD FILES
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '💾 Download Data'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CSV FILE
    # --------------------------------------------------------

    csv_data = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    csv_filename = (
        f"air_quality_"
        f"{location_id}_"
        f"{start_date}_"
        f"{end_date}.csv"
    )


    # --------------------------------------------------------
    # ZIP FILE
    # --------------------------------------------------------

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


    zip_filename = (
        f"air_quality_"
        f"{location_id}_"
        f"{start_date}_"
        f"{end_date}.zip"
    )


    # --------------------------------------------------------
    # DOWNLOAD BUTTONS
    # --------------------------------------------------------

    download_col1, download_col2 = st.columns(2)


    with download_col1:

        st.download_button(

            label="📦 Download CSV ZIP File",

            data=zip_buffer.getvalue(),

            file_name=zip_filename,

            mime="application/zip",

            use_container_width=True

        )


    with download_col2:

        st.download_button(

            label="📄 Download CSV",

            data=csv_data,

            file_name=csv_filename,

            mime="text/csv",

            use_container_width=True

        )


    st.info(
        f"The ZIP file contains: **{csv_filename}**"
    )


    # ========================================================
    # DATA QUALITY CHECK
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔍 Data Quality Check'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # PM RELATIONSHIP
    # --------------------------------------------------------

    pm_relationship = (

        (df["PM1"] <= df["PM2.5"]) &
        (df["PM2.5"] <= df["PM10"])

    )


    valid_relationship = int(
        pm_relationship.sum()
    )


    total_records = len(df)


    percentage = (
        valid_relationship /
        total_records *
        100
    )


    qc1, qc2, qc3 = st.columns(3)


    with qc1:

        st.metric(
            "Valid PM Records",
            f"{valid_relationship:,}"
        )


    with qc2:

        st.metric(
            "Total Records",
            f"{total_records:,}"
        )


    with qc3:

        st.metric(
            "Valid PM (%)",
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


    # ========================================================
    # DATE/TIME CHECK
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🕐 Date and Time Check'
        '</div>',
        unsafe_allow_html=True
    )


    local_times = pd.to_datetime(
        df["Local Date/Time"]
    )

    utc_times = pd.to_datetime(
        df["UTC Date/Time"]
    )


    expected_records = (
        int(
            (
                pd.Timestamp(end_date)
                -
                pd.Timestamp(start_date)
            ).total_seconds()
            /
            3600
        )
        + 24
    )


    time_col1, time_col2, time_col3 = st.columns(3)


    with time_col1:

        st.metric(
            "Expected Hourly Records",
            f"{expected_records:,}"
        )


    with time_col2:

        st.metric(
            "Generated Records",
            f"{len(df):,}"
        )


    with time_col3:

        st.metric(
            "Frequency",
            "Hourly"
        )


    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    with st.expander(
        "📋 Dataset Configuration"
    ):

        config = pd.DataFrame({

            "Parameter": [

                "Location ID",
                "Location Name",
                "Location Type",
                "Sensor ID",
                "Region",
                "Season Mode",
                "Start Date",
                "End Date",
                "Latitude",
                "Longitude",
                "Time Zone",
                "Opening Schedule",
                "PM1 Range",
                "PM2.5 Range",
                "PM10 Range",
                "Temperature Range",
                "Humidity Range"

            ],

            "Value": [

                location_id,
                location_name,
                location_type,
                sensor_id,
                region,
                season_mode,
                str(start_date),
                str(end_date),
                f"{latitude:.6f}",
                f"{longitude:.6f}",
                timezone_name,
                place_open_option,
                f"{pm1_min} – {pm1_max}",
                f"{pm25_min} – {pm25_max}",
                f"{pm10_min} – {pm10_max}",
                f"{temperature_min} – {temperature_max} °C",
                f"{humidity_min} – {humidity_max} %"

            ]

        })


        st.dataframe(
            config,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Ghana Air Quality Automatic Data Generator | "
    "Hourly synthetic monitoring data"
)
