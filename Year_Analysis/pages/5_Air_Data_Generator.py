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
    page_title="Ghana Air Quality Data Generator",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# CSS
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
    '🌍 Ghana Air Quality Automatic Data Generator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Generate hourly synthetic air-quality data and download '
    'hourly, daily or monthly datasets.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# GHANA REGIONS AND CITIES
# ============================================================

ghana_regions = {

    "Greater Accra": [
        "Accra",
        "Tema",
        "Kasoa",
        "Madina",
        "Adenta",
        "Teshie",
        "Nungua",
        "Dansoman",
        "Kaneshie",
        "Lapaz",
        "Achimota"
    ],

    "Ashanti": [
        "Kumasi",
        "Obuasi",
        "Ejisu",
        "Konongo",
        "Mampong"
    ],

    "Western": [
        "Takoradi",
        "Sekondi",
        "Tarkwa",
        "Axim",
        "Prestea"
    ],

    "Western North": [
        "Sefwi Wiawso",
        "Bibiani",
        "Enchi"
    ],

    "Central": [
        "Cape Coast",
        "Kasoa",
        "Winneba",
        "Elmina",
        "Mankessim"
    ],

    "Eastern": [
        "Koforidua",
        "Nkawkaw",
        "Suhum",
        "Nsawam",
        "Akropong"
    ],

    "Volta": [
        "Ho",
        "Hohoe",
        "Keta",
        "Aflao",
        "Kpando"
    ],

    "Oti": [
        "Dambai",
        "Jasikan",
        "Nkwanta"
    ],

    "Northern": [
        "Tamale",
        "Yendi",
        "Savelugu",
        "Bimbilla"
    ],

    "Savannah": [
        "Damongo",
        "Bole",
        "Salaga"
    ],

    "North East": [
        "Nalerigu",
        "Walewale",
        "Gambaga"
    ],

    "Upper East": [
        "Bolgatanga",
        "Navrongo",
        "Bawku"
    ],

    "Upper West": [
        "Wa",
        "Lawra",
        "Tumu"
    ],

    "Bono": [
        "Sunyani",
        "Berekum",
        "Dormaa Ahenkro"
    ],

    "Bono East": [
        "Techiman",
        "Kintampo",
        "Atebubu"
    ],

    "Ahafo": [
        "Goaso",
        "Bechem",
        "Duayaw Nkwanta"
    ],

    "Brong Ahafo": [
        "Sunyani",
        "Techiman",
        "Berekum"
    ]
}


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Generator Settings")


# ============================================================
# LOCATION INFORMATION
# ============================================================

st.sidebar.markdown("### 📍 Location Information")

region = st.sidebar.selectbox(
    "Region",
    list(ghana_regions.keys())
)


city = st.sidebar.selectbox(
    "City",
    ghana_regions[region]
)


location_id = st.sidebar.text_input(
    "Location ID",
    value="001"
)


location_name = st.sidebar.text_input(
    "Location Name",
    value=city
)


location_type = st.sidebar.selectbox(
    "Location Type",
    [
        "Urban",
        "Industrial",
        "Residential",
        "Commercial",
        "Traffic",
        "Background",
        "Rural",
        "Market",
        "Other"
    ]
)


if location_type == "Other":

    location_type = st.sidebar.text_input(
        "Enter Location Type"
    )


# ============================================================
# PROVIDER INFORMATION
# ============================================================

st.sidebar.markdown("### 🏢 Provider Information")

provider_name = st.sidebar.text_input(
    "Provider Name",
    value="EPA Ghana"
)


# ============================================================
# SENSOR INFORMATION
# ============================================================

st.sidebar.markdown("### 📡 Sensor Information")

sensor_type = st.sidebar.selectbox(
    "Sensor Type",
    [
        "Low-Cost Sensor",
        "Reference Grade Monitor",
        "Gravimetric Sampler",
        "Optical Particle Counter",
        "Air Quality Monitor",
        "Other"
    ]
)


if sensor_type == "Other":

    sensor_type = st.sidebar.text_input(
        "Enter Sensor Type"
    )


sensor_id = st.sidebar.text_input(
    "Sensor ID",
    value=f"{region[:3].upper()}_{city[:3].upper()}_001"
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

st.sidebar.markdown("### 🌦️ Season")

season_mode = st.sidebar.selectbox(
    "Season Mode",
    [
        "Automatic based on month",
        "Harmattan",
        "Wet Season",
        "Dry Season",
        "Custom Season"
    ]
)


if season_mode == "Custom Season":

    custom_season_name = st.sidebar.text_input(
        "Custom Season Name",
        value="Custom Season"
    )

else:

    custom_season_name = "Custom Season"


# ============================================================
# GHANA SEASONAL DEFAULTS
# ============================================================

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
# SELECT DEFAULT SEASONAL VALUES
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
# POLLUTANT RANGES
# ============================================================

st.sidebar.markdown("### 🧪 Pollutant Ranges")

st.sidebar.caption(
    "These ranges are for synthetic-data generation."
)


# ------------------------------------------------------------
# PM1
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# PM2.5
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# PM10
# ------------------------------------------------------------

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
# METEOROLOGY
# ============================================================

st.sidebar.markdown(
    "### 🌡️ Meteorological Variables"
)


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
# SEASON DETERMINATION
# ============================================================

def determine_season(month):

    # --------------------------------------------------------
    # MANUAL SEASON
    # --------------------------------------------------------

    if season_mode == "Harmattan":

        return "Harmattan"

    if season_mode == "Wet Season":

        return "Wet Season"

    if season_mode == "Dry Season":

        return "Dry Season"

    if season_mode == "Custom Season":

        return custom_season_name


    # --------------------------------------------------------
    # SOUTHERN GHANA
    # --------------------------------------------------------

    southern_regions = [

        "Greater Accra",
        "Ashanti",
        "Western",
        "Western North",
        "Central",
        "Eastern",
        "Volta",
        "Oti",
        "Bono",
        "Bono East",
        "Ahafo",
        "Brong Ahafo"

    ]


    if region in southern_regions:

        # Harmattan
        if month in [12, 1, 2]:

            return "Harmattan"

        # Major wet season
        elif month in [3, 4, 5, 6, 7]:

            return "Wet Season"

        # Little dry season
        elif month == 8:

            return "Dry Season"

        # Minor wet season
        elif month in [9, 10, 11]:

            return "Wet Season"


    # --------------------------------------------------------
    # NORTHERN GHANA
    # --------------------------------------------------------

    else:

        # Harmattan / dry
        if month in [12, 1, 2, 3]:

            return "Harmattan"

        # Wet season
        elif month in [
            4, 5, 6, 7,
            8, 9, 10
        ]:

            return "Wet Season"

        # Transition
        elif month == 11:

            return "Dry Season"


    return "Dry Season"


# ============================================================
# GENERATE HOURLY DATA
# ============================================================

def generate_data():

    rng = np.random.default_rng(
        int(random_seed)
    )


    tz = ZoneInfo(
        timezone_name
    )


    start_datetime = datetime.combine(
        start_date,
        time(0, 0)
    )


    end_datetime = datetime.combine(
        end_date,
        time(23, 0)
    )


    timestamps = pd.date_range(
        start=start_datetime,
        end=end_datetime,
        freq="h"
    )


    records = []


    # ========================================================
    # LOOP THROUGH HOURLY TIMESTAMPS
    # ========================================================

    for ts in timestamps:

        current_date = ts.date()

        current_hour = ts.hour


        # ----------------------------------------------------
        # SEASON
        # ----------------------------------------------------

        season = determine_season(
            current_date.month
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
        # PM1
        # ====================================================

        pm1 = rng.uniform(
            pm1_min,
            pm1_max
        )


        # ====================================================
        # PM2.5
        # ====================================================

        pm25_lower = max(
            pm25_min,
            pm1
        )


        if pm25_lower <= pm25_max:

            pm25 = rng.uniform(
                pm25_lower,
                pm25_max
            )

        else:

            pm25 = pm25_max


        # ====================================================
        # PM10
        # ====================================================

        pm10_lower = max(
            pm10_min,
            pm25
        )


        if pm10_lower <= pm10_max:

            pm10 = rng.uniform(
                pm10_lower,
                pm10_max
            )

        else:

            pm10 = pm10_max


        # ====================================================
        # TEMPERATURE
        # ====================================================

        temperature = rng.uniform(
            temperature_min,
            temperature_max
        )


        # ====================================================
        # HUMIDITY
        # ====================================================

        humidity = rng.uniform(
            humidity_min,
            humidity_max
        )


        # ====================================================
        # RECORD
        # ====================================================

        records.append({

            "Location ID":
                location_id,

            "Location Name":
                location_name,

            "Region":
                region,

            "City":
                city,

            "Location Type":
                location_type,

            "Provider Name":
                provider_name,

            "Sensor ID":
                sensor_id,

            "Sensor Type":
                sensor_type,

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

        })


    return pd.DataFrame(
        records
    )


# ============================================================
# DAILY AVERAGES
# ============================================================

def calculate_daily_average(df):

    data = df.copy()


    data["Local Date/Time"] = pd.to_datetime(
        data["Local Date/Time"]
    )


    data["Date"] = (
        data["Local Date/Time"]
        .dt.date
    )


    pollutant_columns = [

        "PM1",
        "PM2.5",
        "PM10",
        "Temperature (C)",
        "Humidity (%)"

    ]


    group_columns = [

        "Location ID",
        "Location Name",
        "Region",
        "City",
        "Location Type",
        "Provider Name",
        "Sensor ID",
        "Sensor Type",
        "Date",
        "Season",
        "latitude",
        "longitude"

    ]


    averages = (

        data.groupby(
            group_columns,
            as_index=False
        )[pollutant_columns]

        .mean()

    )


    averages = averages.round({
        "PM1": 2,
        "PM2.5": 2,
        "PM10": 2,
        "Temperature (C)": 2,
        "Humidity (%)": 2
    })


    averages["Date"] = (
        averages["Date"]
        .astype(str)
    )


    return averages


# ============================================================
# MONTHLY AVERAGES
# ============================================================

def calculate_monthly_average(df):

    data = df.copy()


    data["Local Date/Time"] = pd.to_datetime(
        data["Local Date/Time"]
    )


    data["Year"] = (
        data["Local Date/Time"]
        .dt.year
    )


    data["Month"] = (
        data["Local Date/Time"]
        .dt.month
    )


    data["Month Name"] = (
        data["Local Date/Time"]
        .dt.strftime("%B")
    )


    pollutant_columns = [

        "PM1",
        "PM2.5",
        "PM10",
        "Temperature (C)",
        "Humidity (%)"

    ]


    group_columns = [

        "Location ID",
        "Location Name",
        "Region",
        "City",
        "Location Type",
        "Provider Name",
        "Sensor ID",
        "Sensor Type",
        "Year",
        "Month",
        "Month Name",
        "Season",
        "latitude",
        "longitude"

    ]


    averages = (

        data.groupby(
            group_columns,
            as_index=False
        )[pollutant_columns]

        .mean()

    )


    averages = averages.round({
        "PM1": 2,
        "PM2.5": 2,
        "PM10": 2,
        "Temperature (C)": 2,
        "Humidity (%)": 2
    })


    return averages


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


if not str(provider_name).strip():

    errors.append(
        "Provider Name cannot be empty."
    )


if not str(sensor_id).strip():

    errors.append(
        "Sensor ID cannot be empty."
    )


if not str(sensor_type).strip():

    errors.append(
        "Sensor Type cannot be empty."
    )


if end_date < start_date:

    errors.append(
        "End Date must be greater than "
        "or equal to Start Date."
    )


if pm1_max < pm1_min:

    errors.append(
        "PM1 maximum must be greater than "
        "or equal to minimum."
    )


if pm25_max < pm25_min:

    errors.append(
        "PM2.5 maximum must be greater than "
        "or equal to minimum."
    )


if pm10_max < pm10_min:

    errors.append(
        "PM10 maximum must be greater than "
        "or equal to minimum."
    )


if pm1_max > pm25_max:

    errors.append(
        "PM1 maximum should not exceed "
        "PM2.5 maximum."
    )


if pm25_max > pm10_max:

    errors.append(
        "PM2.5 maximum should not exceed "
        "PM10 maximum."
    )


if temperature_max < temperature_min:

    errors.append(
        "Temperature maximum must be greater "
        "than minimum."
    )


if humidity_max < humidity_min:

    errors.append(
        "Humidity maximum must be greater "
        "than minimum."
    )


# ============================================================
# GENERATE BUTTON
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

    if st.button(
        "🚀 Generate Hourly Data",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Generating hourly air-quality data..."
        ):

            hourly_df = generate_data()

            daily_df = calculate_daily_average(
                hourly_df
            )

            monthly_df = calculate_monthly_average(
                hourly_df
            )


            st.session_state[
                "hourly_data"
            ] = hourly_df


            st.session_state[
                "daily_data"
            ] = daily_df


            st.session_state[
                "monthly_data"
            ] = monthly_df


        st.success(
            f"Successfully generated "
            f"{len(hourly_df):,} hourly records."
        )


# ============================================================
# RESULTS
# ============================================================

if "hourly_data" in st.session_state:

    hourly_df = st.session_state[
        "hourly_data"
    ]

    daily_df = st.session_state[
        "daily_data"
    ]

    monthly_df = st.session_state[
        "monthly_data"
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


    c1, c2, c3, c4, c5, c6 = st.columns(6)


    with c1:

        st.metric(
            "Hourly Records",
            f"{len(hourly_df):,}"
        )


    with c2:

        st.metric(
            "Daily Records",
            f"{len(daily_df):,}"
        )


    with c3:

        st.metric(
            "Monthly Records",
            f"{len(monthly_df):,}"
        )


    with c4:

        st.metric(
            "Region",
            region
        )


    with c5:

        st.metric(
            "City",
            city
        )


    with c6:

        st.metric(
            "Provider",
            provider_name
        )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🕐 Hourly Data",
            "📅 Daily Average",
            "📆 Monthly Average",
            "📊 Summary"
        ]
    )


    # ========================================================
    # HOURLY TAB
    # ========================================================

    with tab1:

        st.subheader(
            "Hourly Generated Data"
        )


        st.dataframe(
            hourly_df,
            use_container_width=True,
            height=550
        )


    # ========================================================
    # DAILY TAB
    # ========================================================

    with tab2:

        st.subheader(
            "Daily Average Data"
        )


        st.dataframe(
            daily_df,
            use_container_width=True,
            height=550
        )


    # ========================================================
    # MONTHLY TAB
    # ========================================================

    with tab3:

        st.subheader(
            "Monthly Average Data"
        )


        st.dataframe(
            monthly_df,
            use_container_width=True,
            height=550
        )


    # ========================================================
    # SUMMARY TAB
    # ========================================================

    with tab4:

        st.subheader(
            "Pollutant Summary Statistics"
        )


        summary = (

            hourly_df[
                [
                    "PM1",
                    "PM2.5",
                    "PM10",
                    "Temperature (C)",
                    "Humidity (%)"
                ]
            ]

            .describe()

            .T

            .round(2)

        )


        st.dataframe(
            summary,
            use_container_width=True
        )


        # ----------------------------------------------------
        # SEASON SUMMARY
        # ----------------------------------------------------

        st.subheader(
            "Season Summary"
        )


        season_summary = (

            hourly_df[
                "Season"
            ]

            .value_counts()

            .rename_axis(
                "Season"
            )

            .reset_index(
                name="Records"
            )

        )


        season_summary[
            "Percentage"
        ] = (

            season_summary[
                "Records"
            ]

            /

            len(hourly_df)

            *

            100

        ).round(2)


        st.dataframe(
            season_summary,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# DOWNLOAD SECTION
# ============================================================

if "hourly_data" in st.session_state:

    st.markdown(
        '<div class="section-title">'
        '💾 Download Data'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # SELECT DOWNLOAD DATA
    # ========================================================

    download_type = st.selectbox(
        "Select data to download",
        [
            "Hourly",
            "Daily Average",
            "Monthly Average"
        ]
    )


    if download_type == "Hourly":

        download_df = (
            st.session_state[
                "hourly_data"
            ]
        )

        file_label = "hourly"


    elif download_type == "Daily Average":

        download_df = (
            st.session_state[
                "daily_data"
            ]
        )

        file_label = "daily_average"


    else:

        download_df = (
            st.session_state[
                "monthly_data"
            ]
        )

        file_label = "monthly_average"


    # ========================================================
    # CSV
    # ========================================================

    csv_data = download_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    safe_city = (
        city
        .replace(" ", "_")
        .replace("/", "_")
    )


    safe_provider = (
        provider_name
        .replace(" ", "_")
        .replace("/", "_")
    )


    base_filename = (

        f"{location_id}_"
        f"{safe_city}_"
        f"{safe_provider}_"
        f"{file_label}_"
        f"{start_date}_"
        f"{end_date}"

    )


    csv_filename = (
        f"{base_filename}.csv"
    )


    zip_filename = (
        f"{base_filename}.zip"
    )


    # ========================================================
    # ZIP
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
    # DOWNLOAD BUTTONS
    # ========================================================

    d1, d2 = st.columns(2)


    with d1:

        st.download_button(

            label="📄 Download CSV",

            data=csv_data,

            file_name=csv_filename,

            mime="text/csv",

            use_container_width=True

        )


    with d2:

        st.download_button(

            label="📦 Download ZIP",

            data=zip_buffer.getvalue(),

            file_name=zip_filename,

            mime="application/zip",

            use_container_width=True

        )


# ============================================================
# DOWNLOAD ALL DATASETS
# ============================================================

if "hourly_data" in st.session_state:

    st.markdown(
        '<div class="section-title">'
        '📦 Download All Datasets'
        '</div>',
        unsafe_allow_html=True
    )


    all_zip_buffer = BytesIO()


    with zipfile.ZipFile(
        all_zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:


        # ----------------------------------------------------
        # HOURLY
        # ----------------------------------------------------

        zip_file.writestr(
            "hourly_data.csv",

            st.session_state[
                "hourly_data"
            ].to_csv(
                index=False
            )
        )


        # ----------------------------------------------------
        # DAILY
        # ----------------------------------------------------

        zip_file.writestr(
            "daily_average.csv",

            st.session_state[
                "daily_data"
            ].to_csv(
                index=False
            )
        )


        # ----------------------------------------------------
        # MONTHLY
        # ----------------------------------------------------

        zip_file.writestr(
            "monthly_average.csv",

            st.session_state[
                "monthly_data"
            ].to_csv(
                index=False
            )
        )


    all_zip_buffer.seek(0)


    st.download_button(

        label=(
            "📦 Download Hourly + Daily + "
            "Monthly ZIP"
        ),

        data=all_zip_buffer.getvalue(),

        file_name=(
            f"{location_id}_"
            f"{city.replace(' ', '_')}_"
            f"air_quality_all_data.zip"
        ),

        mime="application/zip",

        use_container_width=True

    )


# ============================================================
# DATA QUALITY CHECK
# ============================================================

if "hourly_data" in st.session_state:

    st.markdown(
        '<div class="section-title">'
        '🔍 Data Quality Check'
        '</div>',
        unsafe_allow_html=True
    )


    hourly_df = st.session_state[
        "hourly_data"
    ]


    # --------------------------------------------------------
    # PM RELATIONSHIP
    # --------------------------------------------------------

    pm_valid = (

        (hourly_df["PM1"] <= hourly_df["PM2.5"])

        &

        (hourly_df["PM2.5"] <= hourly_df["PM10"])

    )


    valid_count = int(
        pm_valid.sum()
    )


    total_count = len(
        hourly_df
    )


    valid_percentage = (

        valid_count

        /

        total_count

        *

        100

    )


    q1, q2, q3 = st.columns(3)


    with q1:

        st.metric(
            "Valid PM Records",
            f"{valid_count:,}"
        )


    with q2:

        st.metric(
            "Total Records",
            f"{total_count:,}"
        )


    with q3:

        st.metric(
            "Valid PM (%)",
            f"{valid_percentage:.1f}%"
        )


    if valid_count == total_count:

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
# CONFIGURATION SUMMARY
# ============================================================

if "hourly_data" in st.session_state:

    with st.expander(
        "📋 Generator Configuration"
    ):


        configuration = pd.DataFrame({

            "Parameter": [

                "Location ID",
                "Location Name",
                "Region",
                "City",
                "Location Type",
                "Provider Name",
                "Sensor ID",
                "Sensor Type",
                "Latitude",
                "Longitude",
                "Start Date",
                "End Date",
                "Season Mode",
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
                region,
                city,
                location_type,
                provider_name,
                sensor_id,
                sensor_type,
                f"{latitude:.6f}",
                f"{longitude:.6f}",
                str(start_date),
                str(end_date),
                season_mode,
                timezone_name,
                place_open_option,
                f"{pm1_min} - {pm1_max}",
                f"{pm25_min} - {pm25_max}",
                f"{pm10_min} - {pm10_max}",
                f"{temperature_min} - {temperature_max} °C",
                f"{humidity_min} - {humidity_max} %"

            ]

        })


        st.dataframe(
            configuration,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Ghana Air Quality Automatic Data Generator | "
    "Hourly, Daily and Monthly Synthetic Data"
)
