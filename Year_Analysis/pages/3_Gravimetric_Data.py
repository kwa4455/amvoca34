import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from io import BytesIO

# --- Page Configuration ---
st.set_page_config(page_title="Gravimetric Data Analysis", page_icon="⚖️", layout="wide")



# --- Title and Logo ---
st.title("📊 Gravimetric Data Analysis")


# --- Helper Functions ---

@st.cache_data(ttl=600)

def cleaned(df):
    df = df.rename(columns=lambda x: x.strip().lower())
    required_columns = ['date', 'site', 'pm25', 'pm10']
    df = df[[col for col in required_columns if col in df.columns]]
    df = df.dropna(axis=1, how='all').dropna()
   

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['quarter'] = df['date'].dt.to_period('Q').astype(str)
    df['day'] = df['date'].dt.date
    df['dayofweek'] = df['date'].dt.day_name()
    df['weekday_type'] = df['date'].dt.weekday.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    df['season'] = df['date'].dt.month.apply(lambda x: 'Harmattan' if x in [12, 1, 2] else 'Non-Harmattan')

    return df

def parse_dates(df):
    for col in df.columns:
        if 'date' in col.lower():  # Focus only on columns with "date" in the name
            try:
                # Parse the date column to datetime
                df[col] = pd.to_datetime(df[col], format='%d-%b-%y', errors='coerce')
                # Drop rows where the parsed date is NaT
                df = df.dropna(subset=[col])
            except Exception as e:
                print(f"Error parsing column {col}: {e}")
                continue
    return df

def standardize_columns(df):
    pm25_cols = ['pm25', 'PM2.5', 'pm_2_5', 'pm25_avg', 'pm2.5']
    pm10_cols = ['pm10', 'PM10', 'pm_10']
    site_cols = ['site', 'station', 'location']

    for col in df.columns:
        col_lower = col.strip().lower()
        if col_lower in [c.lower() for c in pm25_cols]:
            df.rename(columns={col: 'pm25'}, inplace=True)
        if col_lower in [c.lower() for c in pm10_cols]:
            df.rename(columns={col: 'pm10'}, inplace=True)
        if col_lower in [c.lower() for c in site_cols]:
            df.rename(columns={col: 'site'}, inplace=True)
    return df

def compute_aggregates(df, label, pollutant):
    aggregates = {}
    aggregates[f'{label} - Daily Avg ({pollutant})'] = df.groupby(['day', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Monthly Avg ({pollutant})'] = df.groupby(['month', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Quarterly Avg ({pollutant})'] = df.groupby(['quarter', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Yearly Avg ({pollutant})'] = df.groupby(['year', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Day of Week Avg ({pollutant})'] = df.groupby(['dayofweek', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Weekday Type Avg ({pollutant})'] = df.groupby(['weekday_type', 'site'])[pollutant].mean().reset_index().round(1)
    aggregates[f'{label} - Season Avg ({pollutant})'] = df.groupby(['year','season', 'site'])[pollutant].mean().reset_index().round(1)
    return aggregates

def calculate_exceedances(df):
    daily_avg = df.groupby(['site', 'day', 'year', 'month'], as_index=False).agg({
        'pm25': 'mean',
        'pm10': 'mean'
    })
    pm25_exceed = daily_avg[daily_avg['pm25'] > 35].groupby(['year', 'site']).size().reset_index(name='PM25_Exceedance_Count')
    pm10_exceed = daily_avg[daily_avg['pm10'] > 70].groupby(['year', 'site']).size().reset_index(name='PM10_Exceedance_Count')
    total_days = daily_avg.groupby(['year', 'site']).size().reset_index(name='Total_Records')

    exceedance = total_days.merge(pm25_exceed, on=['year', 'site'], how='left') \
                           .merge(pm10_exceed, on=['year', 'site'], how='left')
    exceedance.fillna(0, inplace=True)
    exceedance['PM25_Exceedance_Percent'] = round((exceedance['PM25_Exceedance_Count'] / exceedance['Total_Records']) * 100, 1)
    exceedance['PM10_Exceedance_Percent'] = round((exceedance['PM10_Exceedance_Count'] / exceedance['Total_Records']) * 100, 1)

    return exceedance

def calculate_min_max(df):
    daily_avg = df.groupby(['site', 'day', 'year'], as_index=False).agg({
        'pm25': 'mean',
        'pm10': 'mean'
    })
    df_min_max = daily_avg.groupby(['year', 'site'], as_index=False).agg(
        daily_avg_pm10_max=('pm10', lambda x: round(x.max(), 1)),
        daily_avg_pm10_min=('pm10', lambda x: round(x.min(), 1)),
        daily_avg_pm25_max=('pm25', lambda x: round(x.max(), 1)),
        daily_avg_pm25_min=('pm25', lambda x: round(x.min(), 1))
    )
    return df_min_max

def calculate_aqi_and_category(df):
    daily_avg = df.groupby(['site', 'day', 'year', 'month'], as_index=False).agg({
        'pm25': 'mean'
    })
    breakpoints = [
        (0.0, 9.0, 0, 50),
        (9.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200),
        (125.5, 225.4, 201, 300),
        (225.5, 325.4, 301, 500),
        (325.5, 99999.9, 501, 999)
    ]

    def calculate_aqi(pm):
        for low, high, aqi_low, aqi_high in breakpoints:
            if low <= pm <= high:
                return round(((pm - low) * (aqi_high - aqi_low) / (high - low)) + aqi_low)
        return np.nan

    daily_avg['AQI'] = daily_avg['pm25'].apply(calculate_aqi)
    conditions = [
        (daily_avg['AQI'] > 300),
        (daily_avg['AQI'] > 200),
        (daily_avg['AQI'] > 150),
        (daily_avg['AQI'] > 100),
        (daily_avg['AQI'] > 50),
        (daily_avg['AQI'] >= 0)
    ]
    remarks = ['Hazardous', 'Very Unhealthy', 'Unhealthy', 'Unhealthy for Sensitive Groups', 'Moderate', 'Good']
    daily_avg['AQI_Remark'] = np.select(conditions, remarks, default='Unknown')

    remarks_counts = daily_avg.groupby(['site', 'year', 'AQI_Remark']).size().reset_index(name='Count')
    remarks_counts['Total_Count_Per_Site_Year'] = remarks_counts.groupby(['site', 'year'])['Count'].transform('sum')
    remarks_counts['Percent'] = round((remarks_counts['Count'] / remarks_counts['Total_Count_Per_Site_Year']) * 100, 1)

    return daily_avg, remarks_counts

def to_csv_download(df):
    return BytesIO(df.to_csv(index=False).encode('utf-8'))

def plot_chart(df, x, y, color, chart_type="line", title="", bar_mode="group"):
    streamlit_theme = st.get_option("theme.base")
    theme = streamlit_theme if streamlit_theme else "Light"

    background = '#1c1c1c' if theme == 'dark' else 'white'
    font_color = 'white' if theme == 'dark' else 'black'
    grid_color = '#444' if theme == 'dark' else '#ccc'

    # Define consistent color mapping
    predefined_colors = {
        "pm25": "#1f77b4",   # blue
        "pm10": "#ff7f0e",   # orange
        # Add more pollutants here if needed
    }

    if color and df[color].nunique() > 1:
        selector_param = alt.param(
            name="selector",
            bind=alt.binding_select(options=sorted(df[color].unique()), name=f"Filter {color}: "),
            value=df[color].iloc[0]
        )
        filter_condition = alt.datum[color] == selector_param
    else:
        selector_param = None
        filter_condition = True

    # Axis encoding
    x_encoding = alt.X(f"{x}:N", title=x, axis=alt.Axis(labelAngle=-45)) if chart_type == "bar" else alt.X(x, title=x)

    # Apply consistent color mapping
    if color:
        unique_vals = df[color].unique().tolist()
        color_scale = alt.Scale(domain=list(predefined_colors.keys()), range=list(predefined_colors.values()))
        color_encoding = alt.Color(color, scale=color_scale, legend=alt.Legend(title=color))
    else:
        color_encoding = alt.value("steelblue")

    base = alt.Chart(df).encode(
        x=x_encoding,
        y=alt.Y(y, title=y),
        color=color_encoding,
        tooltip=[x, y, color] if color else [x, y]
    ).properties(
        title=alt.TitleParams(text=title, color=font_color),
        width=700,
        height=400
    ).configure(
        background=background,
        view={"stroke": None},
        axis={
            "labelColor": font_color,
            "titleColor": font_color,
            "gridColor": grid_color,
            "domainColor": grid_color
        },
        legend={
            "labelColor": font_color,
            "titleColor": font_color
        }
    )

    chart = base.mark_line(point=True) if chart_type == "line" else base.mark_bar()

    if selector_param:
        chart = chart.add_params(selector_param).transform_filter(filter_condition)

    return chart.interactive()

# --- Main App ---

uploaded_files = st.file_uploader("Upload up to 4 datasets", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    all_outputs = {}
    site_options = set()
    year_options = set()
    dfs = {}

    for file in uploaded_files:
        label = file.name.split('.')[0]
        ext = file.name.split('.')[-1]
        df = pd.read_excel(file) if ext == 'xlsx' else pd.read_csv(file)

        df = parse_dates(df)
        df = standardize_columns(df)
        df = cleaned(df)

        if 'date' not in df.columns or 'pm25' not in df.columns or 'pm10' not in df.columns or 'site' not in df.columns:
            st.warning(f"⚠️ Could not process {label}: missing columns.")
            continue

        dfs[label] = df
        site_options.update(df['site'].unique())
        year_options.update(df['year'].unique())

    with st.sidebar:
        selected_years = st.multiselect("📅 Filter by Year", sorted(year_options))
        selected_sites = st.multiselect("🏢 Filter by Site", sorted(site_options))

    tabs = st.tabs(["Aggregated Means", "Exceedances", "AQI Stats", "Min/Max Values"])

    with tabs[0]:  # Aggregated Means
        st.header("📊 Aggregated Means")
        for label, df in dfs.items():
            st.subheader(f"Dataset: {label}")
            site_in_tab = st.multiselect(f"Select Site(s) for {label}", sorted(df['site'].unique()), key=f"site_agg_{label}")
            filtered_df = df.copy()
            if selected_years:
                filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
            if site_in_tab:
                filtered_df = filtered_df[filtered_df['site'].isin(site_in_tab)]
            selected_pollutants = ['pm25', 'pm10']
            valid_pollutants = [p for p in selected_pollutants if p in filtered_df.columns]
            if not valid_pollutants:
                st.warning(f"No valid pollutants found in {label}")

            selected_display_pollutants = st.multiselect(
                f"Select Pollutants to Display for {label}",
                options=["All"] + valid_pollutants,
                default=["All"],
                key=f"pollutants_{label}"
            )
            if "All" in selected_display_pollutants:
                selected_display_pollutants = valid_pollutants

            aggregate_levels = [
                ('Daily Avg', ['day', 'site']),
                ('Monthly Avg', ['month', 'site']),
                ('Quarterly Avg', ['quarter', 'site']),
                ('Yearly Avg', ['year', 'site']),
                ('Day of Week Avg', ['dayofweek', 'site']),
                ('Weekday Type Avg', ['weekday_type', 'site']),
                ('Season Avg', ['year','season', 'site'])
            ]
            for level_name, group_keys in aggregate_levels:
                agg_label = f"{label} - {level_name}"
                agg_dfs = []
                for pollutant in valid_pollutants:
                    agg_df = filtered_df.groupby(group_keys)[pollutant].mean().reset_index().round(1)
                    agg_dfs.append(agg_df)
                from functools import reduce
                merged_df = reduce(lambda left, right: pd.merge(left, right, on=group_keys, how='outer'), agg_dfs)
                display_cols = group_keys + [p for p in selected_display_pollutants if p in merged_df.columns]
                editable_df = merged_df[display_cols]
                
                st.data_editor(
                    editable_df,
                    use_container_width=True,
                    column_config={col: {"disabled": True} for col in editable_df.columns},
                    num_rows="dynamic",
                    key=f"editor_{label}_{agg_label}"
                )
                st.download_button(
                    label=f"📥 Download {agg_label}",
                    data=to_csv_download(editable_df),
                    file_name=f"{label}_{agg_label.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                st.markdown("---")
                auto_expand = "Yearly Avg" in agg_label
                with st.expander(f"📈 Show Charts for {agg_label}", expanded=auto_expand):
                    default_chart_type = "line" if any(keyword in level_name for keyword in ['Daily', 'Monthly', 'Quarterly', 'Yearly']) else "bar"
                    chart_type_choice = st.selectbox(
                        f"Select Chart Type for {agg_label}",
                        options=["line", "bar"],
                        index=0 if "Yearly" in agg_label else 1,
                        key=f"chart_type_{label}_{agg_label}"
                    )
                    x_axis = next(
                        (col for col in editable_df.columns if col not in ["site"] + valid_pollutants),
                        None
                    )
                    if not x_axis or x_axis not in editable_df.columns:
                        st.warning(f"Could not determine x-axis column for {agg_label}")
                        continue
                    safe_pollutants = [
                        p for p in selected_display_pollutants if p in editable_df.columns
                    ]
                    if not safe_pollutants:
                        st.warning(f"No valid pollutant columns to plot for {agg_label}")
                        continue
                    try:
                        df_melted = editable_df.melt(
                            id_vars=["site", x_axis],
                            value_vars=safe_pollutants,
                            var_name="pollutant",
                            value_name="value"
                        )
                        if "pollutant" not in df_melted.columns:
                            st.error(f"'pollutant' column missing in melted DataFrame for {agg_label}")
                            st.dataframe(df_melted.head())
                            continue
                        color_map = alt.Scale(domain=["pm25", "pm10"], range=["#1f77b4", "#ff7f0e"])
                        chart = plot_chart(
                            df_melted,
                            x=x_axis,
                            y="value",
                            color="pollutant",  # Changed to allow side-by-side comparison of pm10 and pm25
                            chart_type=chart_type_choice,
                            title=f"{agg_label} - {', '.join(valid_pollutants)}"
                        )
                        st.altair_chart(chart, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error plotting chart: {e}")

    with tabs[1]:  # Exceedances
        st.header("🚨 Exceedances")
        for label, df in dfs.items():
            st.subheader(f"Dataset: {label}")
            site_in_tab = st.multiselect(f"Select Site(s) for {label}", sorted(df['site'].unique()), key=f"site_exc_{label}")
            filtered_df = df.copy()
            if selected_years:
                filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
            if site_in_tab:
                filtered_df = filtered_df[filtered_df['site'].isin(site_in_tab)]

            exceedances = calculate_exceedances(filtered_df)
            st.dataframe(exceedances, use_container_width=True)
            st.download_button(f"⬇️ Download Exceedances - {label}", to_csv_download(exceedances), file_name=f"Exceedances_{label}.csv")

    with tabs[2]:  # AQI
        st.header("🌫️ AQI Stats")
        for label, df in dfs.items():
            st.subheader(f"Dataset: {label}")
            site_in_tab = st.multiselect(f"Select Site(s) for {label}", sorted(df['site'].unique()), key=f"site_aqi_{label}")
            filtered_df = df.copy()
            if selected_years:
                filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
            if site_in_tab:
                filtered_df = filtered_df[filtered_df['site'].isin(site_in_tab)]

            daily_avg, remarks_counts = calculate_aqi_and_category(filtered_df)
            st.dataframe(remarks_counts, use_container_width=True)
            st.dataframe(daily_avg, use_container_width=True)
            st.download_button(f"⬇️ Download Daily Avg - {label}", to_csv_download(daily_avg), file_name=f"DailyAvg_{label}.csv")
            st.download_button(f"⬇️ Download AQI - {label}", to_csv_download(remarks_counts), file_name=f"AQI_{label}.csv")

            aqi_colors = {
                'Good': '#00e400',
                'Moderate': '#ffff00',
                'Unhealthy for Sensitive Groups': '#ff7e00',
                'Unhealthy': '#ff0000',
                'Very Unhealthy': '#8f3f97',
                'Hazardous': '#7e0023'
            }
            remarks_counts['Color'] = remarks_counts['AQI_Remark'].map(aqi_colors)
            aqi_chart = alt.Chart(remarks_counts).mark_bar().encode(
                x=alt.X('Percent:Q', title='% Time in AQI Category'),
                y=alt.Y('AQI_Remark:N', sort='-x', title='AQI Category'),
                color=alt.Color('AQI_Remark:N', scale=alt.Scale(domain=list(aqi_colors.keys()), range=list(aqi_colors.values())), legend=None),
                tooltip=['site', 'year', 'AQI_Remark', 'Percent']
            ).properties(width=700, height=400, title="AQI Remark Percentages")
            st.altair_chart(aqi_chart, use_container_width=True)

    with tabs[3]:  # Min/Max
        st.header("🔥 Min/Max Values")
        for label, df in dfs.items():
            st.subheader(f"Dataset: {label}")
            site_in_tab = st.multiselect(f"Select Site(s) for {label}", sorted(df['site'].unique()), key=f"site_minmax_{label}")
            filtered_df = df.copy()
            if selected_years:
                filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
            if site_in_tab:
                filtered_df = filtered_df[filtered_df['site'].isin(site_in_tab)]

            min_max = calculate_min_max(filtered_df)
            st.dataframe(min_max, use_container_width=True)
            st.download_button(f"⬇️ Download MinMax - {label}", to_csv_download(min_max), file_name=f"MinMax_{label}.csv")

else:
    st.info("Upload CSV or Excel files from different air quality sources to begin.")
