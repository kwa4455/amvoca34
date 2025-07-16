import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.stats import kruskal, ttest_ind
from plotly.subplots import make_subplots

# --- Page Config ---
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("🌍 Air Quality Data Explorer")

# Initialize theme and font size in session state
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "font_size" not in st.session_state:
    st.session_state.font_size = "Medium"

theme_choice = st.sidebar.selectbox(
    "Choose Theme",
    ["Light", "Dark", "Blue", "Green", "Purple"],
    index=["Light", "Dark", "Blue", "Green", "Purple"].index(st.session_state.theme)
)
st.session_state.theme = theme_choice

# Font size selection
font_choice = st.sidebar.radio("Font Size", ["Small", "Medium", "Large"],
                               index=["Small", "Medium", "Large"].index(st.session_state.font_size))
st.session_state.font_size = font_choice

# Reset to default
if st.sidebar.button("🔄 Reset to Defaults"):
    st.session_state.theme = "Light"
    st.session_state.font_size = "Medium"
    st.success("Reset to Light theme and Medium font!")
    st.rerun()

# Theme settings dictionary
themes = {
    "Light": {
        "background": "rgba(255, 255, 255, 0.4)",
        "text": "#004d40",
        "button": "#00796b",
        "hover": "#004d40",
        "input_bg": "rgba(255, 255, 255, 0.6)"
    },
    "Dark": {
        "background":"rgba(22, 27, 34, 0.4)",
        "text": "#e6edf3",
        "button": "#238636",
        "hover": "#2ea043",
        "input_bg": "rgba(33, 38, 45, 0.6)"
    },
    "Blue": {
        "background": "rgba(210, 230, 255, 0.4)",
        "text": "#0a2540",
        "button": "#1e88e5",
        "hover": "#1565c0",
        "input_bg": "rgba(255, 255, 255, 0.6)"
    },
    "Green": {
        "background": "rgba(223, 255, 231, 0.4)", 
        "text": "#1b5e20",
        "button": "#43a047",
        "hover": "#2e7d32",
        "input_bg": "rgba(255, 255, 255, 0.6)"
    },
    "Purple": {
        "background": "rgba(240, 225, 255, 0.4)",
        "text": "#4a148c",
        "button": "#8e24aa",
        "hover": "#6a1b9a",
        "input_bg": "rgba(255, 255, 255, 0.6)"
    }
}

# Font size mapping
font_map = {"Small": "14px", "Medium": "16px", "Large": "18px"}

# Apply theme and inject CSS
theme = themes[st.session_state.theme]
font_size = font_map[st.session_state.font_size]

def generate_css(theme: dict, font_size: str) -> str:
    return f"""
    <style>
    html, body, .stApp, [class^="css"], button, input, label, textarea, select {{
        font-size: {font_size} !important;
        color: {theme["text"]} !important;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }}
    .stApp {{
        background-color: {theme["background"]} !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        background-attachment: fixed;
        box-shadow: inset 0 0 50px rgba(255,255,255,0.1);
        transition: background 0.5s ease, color 0.5s ease;
    }}
    html, body, [class^="css"] {{
        background-color: transparent !important;
    }}
    h1, h2, h3 {{
        font-weight: bold;
    }}
    .stTextInput > div > input,
    .stSelectbox > div > div,
    .stRadio > div,
    textarea {{
        background-color: {theme["input_bg"]} !important;
        color: {theme["text"]} !important;
        border: 1px solid {theme["button"]};
        border-radius: 8px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }}
    div.stButton > button {{
        background-color: {theme["button"]};
        color: white;
        padding: 0.5em 1.5em;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: {theme["hover"]};
    }}

    body, .stApp {{
        font-family: 'Poppins', sans-serif;
        transition: all 0.5s ease;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
        border-right: 2px solid #74c69d;
    }}

    .stButton>button, .stDownloadButton>button {{
        background: {theme["button"]};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7em 1.5em;
        font-weight: bold;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 20px {theme["button"]};
        transition: all 0.3s ease;
    }}

    .stButton>button:hover, .stDownloadButton>button:hover {{
        background: {theme["hover"]};
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4), 0 0 30px {theme["hover"]};
    }}

    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #74c69d;
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #52b788;
    }}

    .glow-text {{
        text-align: center;
        font-size: 3em;
        color: #52b788;
        text-shadow: 0 0 5px #52b788, 0 0 10px #52b788, 0 0 20px #52b788;
        margin-bottom: 20px;
    }}

    .stDataFrame, .stTable {{
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        overflow: hidden;
        font-size: 15px;
    }}

    thead tr th {{
        background: {theme["button"]};
        color: white;
        font-weight: bold;
        text-align: center;
        padding: 0.5em;
    }}

    tbody tr:nth-child(even) {{
        background-color: #eeeeee;
    }}
    tbody tr:nth-child(odd) {{
        background-color: #ffffff;
    }}
    tbody tr:hover {{
        background-color: #b7e4c7;
        transition: background-color 0.3s ease;
    }}

    .element-container iframe {{
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }}

    body.dark-mode .stDataFrame, body.dark-mode .stTable {{
        background: rgba(33, 38, 45, 0.6);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        font-size: 15px;
        overflow: hidden;
    }}

    body.dark-mode thead tr th {{
        background: linear-gradient(135deg, #238636, #2ea043);
        color: #ffffff;
        font-weight: bold;
        text-align: center;
    }}

    body.dark-mode tbody tr:nth-child(even) {{
        background: linear-gradient(90deg, #21262d, #30363d);
        color: #e6edf3;
        transition: all 0.3s ease;
    }}

    body.dark-mode tbody tr:nth-child(odd) {{
        background: linear-gradient(90deg, #161b22, #21262d);
        color: #e6edf3;
        transition: all 0.3s ease;
    }}

    body.dark-mode tbody tr:hover {{
        background: linear-gradient(90deg, #21262d, #30363d);
        box-shadow: 0 0 15px #58a6ff;
        transform: scale(1.01);
    }}

    body.dark-mode .element-container iframe {{
        background: rgba(33, 38, 45, 0.5) !important;
        backdrop-filter: blur(10px);
        border: 2px solid #58a6ff;
        padding: 10px;
        border-radius: 16px;
        box-shadow: 0 0 15px #58a6ff, 0 0 30px #79c0ff;
        animation: pulse-glow-dark 3s infinite ease-in-out;
    }}

    @keyframes pulse-glow {{
      0% {{ box-shadow: 0 0 15px #74c69d, 0 0 30px #52b788; }}
      50% {{ box-shadow: 0 0 25px #40916c, 0 0 45px #2d6a4f; }}
      100% {{ box-shadow: 0 0 15px #74c69d, 0 0 30px #52b788; }}
    }}
    @keyframes pulse-glow-dark {{
      0% {{ box-shadow: 0 0 15px #58a6ff, 0 0 30px #79c0ff; }}
      50% {{ box-shadow: 0 0 25px #3b82f6, 0 0 45px #2563eb; }}
      100% {{ box-shadow: 0 0 15px #58a6ff, 0 0 30px #79c0ff; }}
    }}

    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: {theme["background"]};
        color: {theme["text"]};
        text-align: center;
        padding: 12px 0;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0px -2px 10px rgba(0,0,0,0.1);
        backdrop-filter: blur(8px);
    }}
    </style>
    """

st.markdown(generate_css(theme, font_size), unsafe_allow_html=True)

def cleaned(df):
    # Parse and clean date
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows with invalid dates
    df['date'] = df['date'].dt.tz_localize(None)
    df = df.set_index('date')

    # Add time features
    df['year'] = df.index.year
    df['month'] = pd.Categorical(df.index.strftime('%b'),
                                 categories=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                 ordered=True)
    df['dayofweek'] = pd.Categorical(df.index.day_name(),
                                     categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                 'Friday', 'Saturday', 'Sunday'],
                                     ordered=True)

    return df

def yearly_plot_bar(df, metal_sel):
    import plotly.graph_objects as go
    import pandas as pd

    # Check if the selected metal and its error column are in the DataFrame
    if metal_sel not in df.columns:
        return go.Figure(), pd.DataFrame()  # Return empty plot and data if missing

    error_col = f"{metal_sel}_error"
    has_error = error_col in df.columns

    # Define aggregation logic
    agg_funcs = {
        metal_sel: ['mean', 'std', 'median']
    }
    if has_error:
        agg_funcs[error_col] = ['mean', 'std', 'median']

    # Group and aggregate
    summary_data = (
        df.groupby(['site', 'dayofweek'])
        .agg(agg_funcs)
        .reset_index()
    )

    # Flatten column names
    summary_data.columns = ['_'.join(col).strip('_') for col in summary_data.columns]

    # Add sample count per group
    summary_data['count'] = df.groupby(['site', 'dayofweek']).size().values

    # Round and format
    summary_data = summary_data.round(3)

    # Define colors by day of week
        # Define colors by day of week
    year_colors = {
        "Monday": "#008000",
        "Tuesday": "#b30000",
        "Wednesday": "blue",
        "Thursday": "yellow",
        "Friday": "purple",
        "Saturday": "orange",
        "Sunday": "green"
    }

    # Metal-specific limits
    metal_limits = {
        "pb": 0.5,     # Ghana
        "cr": 12,      # US EPA
        "cd": 5        # EU AQS
    }

    limit_value = metal_limits.get(metal_sel.lower())

    # Build plot
    fig = go.Figure()

    for day in summary_data['dayofweek'].unique():
        subset = summary_data[summary_data['dayofweek'] == day]

        fig.add_trace(go.Bar(
            x=subset['site'],
            y=subset.get(f'{metal_sel}_median', [0]),
            name=day,
            error_y=dict(
                type='data',
                array=subset.get(f'{error_col}_median', [0]) if has_error else None,
                visible=has_error
            ),
            marker_color=year_colors.get(day, 'gray'),
        ))

    # Add standard limit line if available
    if limit_value:
        fig.add_shape(
            type="line",
            x0=-0.5, x1=len(summary_data['site'].unique()) - 0.5,
            y0=limit_value, y1=limit_value,
            line=dict(color="red", dash="solid"),
            xref="x", yref="y"
        )

    # Vertical lines between sites
    for i in range(len(summary_data['site'].unique()) - 1):
        fig.add_vline(x=i + 0.5, line_dash="dash", line_color="black")

    # Set units
    unit = "μg/m³" if metal_sel.lower() == "al" else "ng/m³"

    fig.update_layout(
        barmode='group',
        title=f"{metal_sel.upper()} Pollution by Site (Median Value)",
        xaxis_title="Site",
        yaxis_title=f"{metal_sel.upper()} ({unit})",
        xaxis_tickangle=45,
        legend_title_text='Day of Week',
        template="plotly_white",
        font=dict(size=12, family="Arial"),
        plot_bgcolor='white',
        margin=dict(t=80, b=100),
    )

    return fig, summary_data

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

def correlation_analysis(df, metals, selected_sites, title="Correlation Heatmap"):
    site_corrs = {}

    # Use Plotly's color palette to auto-assign site colors
    unique_sites = sorted(df['site'].unique())
    color_palette = px.colors.qualitative.Set3 + px.colors.qualitative.Plotly
    colors = {site: color_palette[i % len(color_palette)] for i, site in enumerate(unique_sites)}

    for site in unique_sites:
        if site not in selected_sites:
            continue

        site_df = df[df['site'] == site][metals]

        if site_df.empty:
            continue

        corr_matrix = site_df.corr(method='pearson')
        site_corrs[site] = corr_matrix

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation"),
            hovertemplate="x: %{x}<br>y: %{y}<br>Correlation: %{z:.2f}<extra></extra>",
        ))

        fig.update_layout(
            title=f"{title} - {site}",
            xaxis_title="Variables",
            yaxis_title="Variables",
            title_font=dict(size=16),
            xaxis=dict(tickangle=45, tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12)),
            plot_bgcolor='white',
            height=600,
            width=600,
        )

        st.plotly_chart(fig, use_container_width=True)

    return site_corrs




def plot_violin_plot(df, metal, selected_sites):
    # Generate automatic color palette
    unique_sites = sorted(df['site'].unique())
    color_palette = px.colors.qualitative.Set3 + px.colors.qualitative.Plotly
    colors = {site: color_palette[i % len(color_palette)] for i, site in enumerate(unique_sites)}

    # Define units
    unit = "µg/m³" if metal.lower() == "al" else "ng/m³"
    
    fig = go.Figure()

    for site in unique_sites:
        if site not in selected_sites:
            continue

        site_data = df[df['site'] == site]

        fig.add_trace(go.Violin(
            x=site_data['site'],
            y=site_data[metal],
            box_visible=True,
            line_color=colors[site],
            name=site,
            side='positive',
            meanline_visible=True,
            fillcolor=colors[site],
            opacity=0.6,
            points="all",
        ))

        mean_value = site_data[metal].mean()
        sd_value = site_data[metal].std()
        median_value = site_data[metal].median()

        fig.add_annotation(
            x=site,
            y=mean_value + 0.02,
            text=f"Mean: {mean_value:.2f}<br>SD: {sd_value:.2f}<br>Median: {median_value:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            ax=0,
            ay=-40,
            font=dict(size=10, color="black"),
            align="center"
        )

    fig.update_layout(
        title=f"{metal.upper()} ({unit}) by Site",
        xaxis_title="Site",
        yaxis_title=f"{metal.upper()} ({unit})",
        template="plotly_white",
        showlegend=False,
        xaxis_tickangle=45,
        font=dict(size=12, family="Arial", color="black"),
        plot_bgcolor='white',
        margin=dict(t=50, b=100),
    )

    return fig



# Function to calculate Kruskal-Wallis test and return a summary DataFrame
def kruskal_wallis_by_test(df, metals, site_column, n_bootstrap=1000, ci_level=0.95):
    # Initialize an empty list to store results
    results = []

    # Function to calculate the confidence interval of a sample using bootstrapping
    def bootstrap_ci(data, n_bootstrap, ci_level):
        bootstrapped_means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrapped_means.append(np.median(sample))
        lower_bound = np.percentile(bootstrapped_means, (1 - ci_level) / 2 * 100)
        upper_bound = np.percentile(bootstrapped_means, (1 + ci_level) / 2 * 100)
        return lower_bound, upper_bound

    # Iterate over each metal to perform Kruskal-Wallis test
    for metal in metals:
        # Group the data by site for each metal and perform the Kruskal-Wallis test
        groups = [df[df[site_column] == site][metal].dropna() for site in df[site_column].unique()]
        statistic, p_value = stats.kruskal(*groups)

        # Calculate the degrees of freedom (df = number of unique sites - 1)
        df_value = len(df[site_column].unique()) - 1
        
        # Calculate the confidence intervals for the medians of each group
        ci_dict = {}
        for site in df[site_column].unique():
            site_data = df[df[site_column] == site][metal].dropna()
            lower, upper = bootstrap_ci(site_data, n_bootstrap, ci_level)
            ci_dict[site] = {'lower': lower, 'upper': upper}

        # Store the results in the results list
        results.append({
            'Variable': metal.capitalize(),
            'Statistic': statistic,
            'p_value': p_value,
            'df': df_value,
            'Confidence Intervals': ci_dict
        })

    # Convert the results to a DataFrame
    kruskal_df = pd.DataFrame(results)
    
    return kruskal_df

# Function to aggregate data by month or dayofweek
def aggregate_metals(df, time_col):
    metals = ["cd", "cr", "hg", "al", "as", "mn", "pb"]
    agg_funcs = {col: ['mean', 'std', 'median'] for col in metals}
    summary = df.groupby(['site', time_col]).agg(agg_funcs).reset_index()
    
    # Flatten MultiIndex columns
    summary.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in summary.columns]
    return summary

# Time Variation Plotting Function
def timeVariation(df, pollutants=["pb"], statistic="median", colors=None):
    if colors is None:
        colors = px.colors.qualitative.Plotly

    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=["Time Variation by Month", "Time Variation by Day of Week"],
        shared_yaxes=True
    )

    # Aggregate by 'month'
    df_month_agg = aggregate_metals(df, time_col="month")
    
    # Plot for 'month'
    for i, pollutant in enumerate(pollutants):
        col_name = f"{pollutant}_{statistic}"
        if col_name not in df_month_agg.columns:
            raise ValueError(f"'{col_name}' not found in DataFrame.")

        df_clean = df_month_agg.dropna(subset=[col_name])

        fig.add_trace(go.Scatter(
            x=df_clean['month'],
            y=df_clean[col_name],
            mode='lines+markers',
            name=f'{pollutant} by Month',
            line=dict(color=colors[i % len(colors)]),
        ), row=1, col=1)

    # Aggregate by 'dayofweek'
    df_dayofweek_agg = aggregate_metals(df, time_col="dayofweek")
    
    # Plot for 'dayofweek'
    for i, pollutant in enumerate(pollutants):
        col_name = f"{pollutant}_{statistic}"
        if col_name not in df_dayofweek_agg.columns:
            raise ValueError(f"'{col_name}' not found in DataFrame.")

        df_clean = df_dayofweek_agg.dropna(subset=[col_name])

        fig.add_trace(go.Scatter(
            x=df_clean['dayofweek'],
            y=df_clean[col_name],
            mode='lines+markers',
            name=f'{pollutant} by Day of Week',
            line=dict(color=colors[i % len(colors)]),
        ), row=1, col=2)

    # Update layout and titles
    fig.update_layout(
        title=f"Time Variation of Pollutants ({statistic.capitalize()})",
        xaxis_title="Month",
        yaxis_title="Concentration",
        template="plotly",
        showlegend=True,
        height=500
    )

    # X-axis label for dayofweek subplot
    fig.update_xaxes(title_text="Day", row=1, col=2)  # Label x-axis for dayofweek plot

    # Custom Y-axis labels based on pollutant
    for pollutant in pollutants:
        if pollutant == "al":  # For Al, use "µg/m³"
            fig.update_yaxes(title_text="Concentration (µg/m³)", row=1, col=1)
            fig.update_yaxes(title_text="Concentration (µg/m³)", row=1, col=2)
        else:  # For other metals, use "ng/m³"
            fig.update_yaxes(title_text="Concentration (ng/m³)", row=1, col=1)
            fig.update_yaxes(title_text="Concentration (ng/m³)", row=1, col=2)

    # Update x-axis type for categorical variables
    fig.update_xaxes(type='category', row=1, col=1)  # 'month' is categorical
    fig.update_xaxes(type='category', row=1, col=2)  # 'dayofweek' is categorical

    return fig






uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])
if not uploaded_files:
    st.warning("Please upload at least one CSV file.")
    st.stop()
required_columns = [
    'date', 'site', 'id', "cd", "cr", "hg", "al", "as", "mn", "pb",
    "cd_error", "cr_error", "hg_error", "al_error", "as_error", "mn_error", "pb_error"
]
dataframes = []
file_names = []

for uploaded_file in uploaded_files:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        missing = set(required_columns) - set(df.columns)
        if missing:
            st.warning(f"File '{uploaded_file.name}' is missing required columns: {', '.join(sorted(missing))}")
            continue
        df = df[required_columns].copy()
        file_names.append(uploaded_file.name)
        df_cleaned = cleaned(df)
        dataframes.append(df_cleaned)
        file_names.append(uploaded_file.name)
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {e}")
        st.stop()

# Sidebar filters

# Identify metal columns (exclude non-metal ones)
non_metal_columns = {'site', 'year', 'dayofweek', 'month' 'date',"cd_error", "cr_error", "hg_error", "al_error", "as_error", "mn_error", "pb_error"}
all_columns = set().union(*[df.columns for df in dataframes])
metal_columns = ["cd", "cr", "hg", "al", "as", "mn", "pb"]
error_columns = [f"{m}_error" for m in metal_columns]
errors = sorted([col for col in all_columns if col.lower() in error_columns])
non_metal_columns = {'site', 'year', 'dayofweek', 'month', 'date'}
metals = sorted([col for col in all_columns if col.lower() in metal_columns])
sites = sorted(
    set().union(*[df['site'].unique() for df in dataframes if 'site' in df.columns])
)




    
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends", "📊 Box & Bar Plots", "📐 Kruskal & T-Test",
    "🔗 Correlation", "📉 Theil-Sen Trend"
])

# --- Tab 1: Yearly Trends ---
with tab1:
    for df, name in zip(dataframes, file_names):
        st.subheader(f"Yearly Trend: {name}")
        metals = [m for m in metal_columns if m in df.columns]
        if not metals:
            st.warning(f"No metals found in {name}. Skipping.")
            continue

        selected_metals = st.multiselect(
            f"Select metals for {name}", metals, default=metals, key=f"metals_{name}"
        )

        for metal in selected_metals:
            fig, summary = yearly_plot_bar(df, metal)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(summary, use_container_width=True)

# --- Tab 2: Correlation Analysis ---
with tab2:
    for df, name in zip(dataframes, file_names):
        st.subheader(f"Correlation: {name}")
        metals = [m for m in metal_columns if m in df.columns]
        site_sel = st.multiselect(
            f"Sites for {name}", sites, default=sites, key=f"site_corr_{name}"
        )
        df_sub = df[df['site'].isin(site_sel)]
        correlation_analysis(df_sub, metals, site_sel, title=name)

# --- Tab 3: Violin Plot ---
with tab3:
    for df, name in zip(dataframes, file_names):
        st.subheader(f"Violin Plot: {name}")
        metals = [m for m in metal_columns if m in df.columns]
        metal_sel = st.selectbox(f"Metal for {name}", metals, key=f"metal2_{name}")
        fig = plot_violin_plot(df, metal_sel)
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Kruskal-Wallis Test ---
with tab4:
    for df, name in zip(dataframes, file_names):
        st.subheader(f"Kruskal-Wallis Test: {name}")
        sites = sorted(df['site'].unique())
        metals = [m for m in metal_columns if m in df.columns]
        site_column = st.multiselect(
            f"Sites for {name}", sites, default=sites, key=f"site3_{name}"
        )
        df_sub = df[df['site'].isin(site_column)]
        kruskal_df = kruskal_wallis_by_test(
            df_sub, metals, site_column, n_bootstrap=1000, ci_level=0.95
        )
        st.write("Kruskal-Wallis Test Results:")
        st.dataframe(kruskal_df)

# --- Tab 5: Theil-Sen Trend Analysis ---
with tab5:
    for df, name in zip(dataframes, file_names):
        st.subheader(f"Time Variation: {name}")
        sites = sorted(df['site'].unique())
        metals = [m for m in metal_columns if m in df.columns]
        site_sel = st.multiselect(
            f"Sites for {name}", sites, default=sites, key=f"site5_{name}"
        )
        metal_sel = st.multiselect(
            f"Metals for {name}", metals, default=metals[:1], key=f"metal5_{name}"
        )
        df_sub = df[df['site'].isin(site_sel)]
        fig = timeVariation(df_sub, pollutants=metal_sel, statistic=statistic)
        st.plotly_chart(fig)
