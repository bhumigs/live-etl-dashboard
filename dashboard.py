# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data
from report_generator import generate_pdf_report

# ----------------------------
# Auto-refresh every 10 seconds
# ----------------------------
st_autorefresh(interval=10000, limit=None, key="live_dashboard")

# ----------------------------
# Dashboard Header
# ----------------------------
st.title("📊 Live ETL Dashboard (Multi-source)")
st.markdown(
    "Upload CSV, JSON, or provide an API URL returning JSON. Dashboard updates automatically."
)

# ----------------------------
# Sidebar: Data Input
# ----------------------------
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV/JSON file", type=["csv", "json"]
)
api_url = st.sidebar.text_input("Or enter API URL returning JSON")

# ETL output path
DATA_FILE = "data/etl_output.csv"

# ----------------------------
# Run ETL based on user input
# ----------------------------
df = None

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    with st.spinner("⚡ Running ETL on uploaded file..."):
        raw_df = pd.read_csv(
            uploaded_file) if file_type == "csv" else pd.read_json(uploaded_file)
        df = transform_data(raw_df)
        load_data(df, target_path=DATA_FILE)
    st.success("✅ ETL completed from uploaded file!")

elif api_url:
    with st.spinner("⚡ Running ETL on API data..."):
        try:
            # Make sure extract_data handles URLs
            raw_df = extract_data(api_url)
            df = transform_data(raw_df)
            load_data(df, target_path=DATA_FILE)
            st.success("✅ ETL completed from API data!")
        except Exception as e:
            st.error(f"❌ Failed to fetch API data: {e}")

else:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        st.warning("No data uploaded yet. Please provide a file or API URL.")
        st.stop()

# ----------------------------
# Detect date column
# ----------------------------
date_cols = df.select_dtypes(include=["object", "datetime"]).columns.tolist()
date_column = None
for col in date_cols:
    try:
        df[col] = pd.to_datetime(
            df[col], errors='coerce', infer_datetime_format=True)

        date_column = col
        break
    except Exception:
        continue

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

# Categorical filters
categorical_cols = df.select_dtypes(include="object").columns.tolist()
selected_category = {}
for col in categorical_cols:
    options = df[col].unique().tolist()
    selected_category[col] = st.sidebar.multiselect(
        f"Filter {col}", options, default=options
    )

# Numeric filters
numeric_cols = df.select_dtypes(include="number").columns.tolist()
selected_numeric = {}
for col in numeric_cols:
    min_val, max_val = float(df[col].min()), float(df[col].max())
    selected_numeric[col] = st.sidebar.slider(
        f"{col} range", min_val, max_val, (min_val, max_val)
    )

# Apply filters
filtered_df = df.copy()
for col, vals in selected_category.items():
    filtered_df = filtered_df[filtered_df[col].isin(vals)]
for col, val_range in selected_numeric.items():
    filtered_df = filtered_df[(filtered_df[col] >= val_range[0]) & (
        filtered_df[col] <= val_range[1])]

# Date range filter
# Date range filter
if date_column:
    # Drop missing datetime values
    filtered_dates = filtered_df[date_column].dropna()
    if not filtered_dates.empty:
        start_date, end_date = filtered_dates.min(), filtered_dates.max()
        selected_range = st.sidebar.slider(
            "Select Date Range",
            min_value=start_date,
            max_value=end_date,
            value=(start_date, end_date)
        )
        filtered_df = filtered_df[
            (filtered_df[date_column] >= selected_range[0]) &
            (filtered_df[date_column] <= selected_range[1])
        ]
    else:
        st.warning("Date column exists but has no valid dates.")

# ----------------------------
# KPIs / Metrics
# ----------------------------
st.subheader("Key Metrics")
if numeric_cols:
    cols = st.columns(len(numeric_cols))
    for i, col in enumerate(numeric_cols):
        value = filtered_df[col].sum()
        cols[i].metric(label=f"Total {col}", value=f"{value:,.2f}")
else:
    st.info("No numeric columns for metrics.")

st.markdown("---")

# ----------------------------
# Filtered Data Table & CSV Download
# ----------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df)

st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# ----------------------------
# Charts Helper
# ----------------------------


def safe_to_image(fig):
    try:
        return fig.to_image(format="png")
    except Exception:
        st.warning("⚠️ Chart export disabled — install Chrome or Kaleido.")
        return None


# Scatter Chart
if len(numeric_cols) >= 2:
    fig_scatter = px.scatter(
        filtered_df,
        x=numeric_cols[0],
        y=numeric_cols[1],
        color=categorical_cols[0] if categorical_cols else None,
        hover_data=filtered_df.columns
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    scatter_img = safe_to_image(fig_scatter)
    if scatter_img:
        st.download_button("Download Scatter Chart PNG",
                           scatter_img, "scatter_chart.png", "image/png")

# Bar Chart
if categorical_cols and numeric_cols:
    fig_bar = px.bar(
        filtered_df,
        x=categorical_cols[0],
        y=numeric_cols[0],
        color=categorical_cols[0],
        barmode="group"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    bar_img = safe_to_image(fig_bar)
    if bar_img:
        st.download_button("Download Bar Chart PNG", bar_img,
                           "bar_chart.png", "image/png")

# Line Chart
if date_column and numeric_cols:
    selected_numeric_column = st.sidebar.selectbox(
        "Select numeric column for time series", numeric_cols)
    fig_line = px.line(
        filtered_df.sort_values(date_column),
        x=date_column,
        y=selected_numeric_column
    )
    st.plotly_chart(fig_line, use_container_width=True)
    line_img = safe_to_image(fig_line)
    if line_img:
        st.download_button("Download Line Chart PNG",
                           line_img, "line_chart.png", "image/png")

# ----------------------------
# PDF Report
# ----------------------------
st.markdown("---")
st.subheader("📄 Reporting")

if st.button("Generate PDF Report", key="pdf_report"):
    try:
        pdf_path = generate_pdf_report(filtered_df)
        st.success(f"✅ PDF generated: {pdf_path}")
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "Download PDF Report",
                pdf_file,
                os.path.basename(pdf_path),
                "application/pdf"
            )
    except Exception as e:
        st.error(f"❌ Error generating PDF: {e}")
