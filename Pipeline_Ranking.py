import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
      .block-container {
        padding-top: 0.75rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
      }
      h1 {
        font-size: 1.55rem !important;
      }
      div[data-testid="stMarkdownContainer"] p {
        font-size: 0.95rem;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



st.title("Pipeline Rank")


from db.repository import fetch_operating_revenue, fetch_miles,fetch_volume,fetch_negotiated_revenue,fetch_net_plant,fetch_kpis


# ---- user input
year = st.selectbox("Year", ["2022", "2023", "2024"], index=2)

# ---- fetch data
df_revenue = fetch_operating_revenue(year)

df_miles = fetch_miles(year)

df_volume = fetch_volume(year)

df_negotiated_revenue = fetch_negotiated_revenue(year)

df_net_plant = fetch_net_plant(year)

df_kpis = fetch_kpis(year)

pivoted_kpi = df_kpis.pivot_table(
    index=["Asset", "Qtr", "Year"],
    columns="Metric",
    values="Value",
    aggfunc="first"   # use mean/sum if duplicates exist
).reset_index()




conditions = [
    pivoted_kpi["% Negotiated Rate"] < 0.49,
    pivoted_kpi["% Negotiated Rate"].between(0.49, 0.59, inclusive="both"),
    pivoted_kpi["% Negotiated Rate"] >= 0.59
]

choices = [
    "Cost of Service",
    "Mixed",
    "Negotiated"
]

pivoted_kpi["Rate Structure"] = np.select(
    conditions,
    choices,
    default="Unknown"
)
  

def classify_capital_posture(ratio):
    if pd.isna(ratio):
        return None
    elif ratio < 0.8:
        return "Harvested"
    elif ratio <= 1.2:
        return "Maintained"
    else:
        return "Growth"

pivoted_kpi["Capital Posture"] = pivoted_kpi["Reinvestment Ratio"].apply(classify_capital_posture)

pivoted_kpi["rorb_score"] = pivoted_kpi["RORB"].rank(pct=True) * 100
pivoted_kpi["om_score"] = (1 - pivoted_kpi["O&M Intensity"].rank(pct=True)) * 100

pivoted_kpi["reinvestment_score"] = (
    1 - (pivoted_kpi["Reinvestment Ratio"] - 1).abs().clip(upper=1)
) * 100

# Neutral floor so growth is not punished
pivoted_kpi["reinvestment_score"] = pivoted_kpi["reinvestment_score"].clip(lower=40)


pivoted_kpi["final_score"] = (
    0.5 * pivoted_kpi["rorb_score"]
  + 0.3 * pivoted_kpi["om_score"]
  + 0.2 * pivoted_kpi["reinvestment_score"]

)

pivoted_kpi["Rank"] = pivoted_kpi["final_score"].rank(ascending=False, method="min").astype(int)

pivoted_kpi = pivoted_kpi.drop(columns=["rorb_score","om_score","reinvestment_score","Year","Qtr"])

def slider_range(df, column, label):
    series = df[column].dropna()
    if series.empty:
        return None
    min_val = float(series.min())
    max_val = float(series.max())
    return st.slider(label, min_val, max_val, (min_val, max_val))

with st.sidebar:
    st.header("Filters")
    mobile_view = st.toggle("Mobile-friendly view", value=False)
    st.caption("Financial")
    rorb_range = slider_range(pivoted_kpi, "RORB", "RORB (%)")
    st.caption("Cost")
    om_range = slider_range(pivoted_kpi, "O&M Intensity", "O&M Intensity (ratio)")
    cap_range = slider_range(pivoted_kpi, "Capital Intensity", "Capital Intensity (ratio)")
    unit_op_range = slider_range(pivoted_kpi, "Unit Operating Cost", "Unit Operating Cost (per unit)")
    st.caption("Capital")
    reinvestment_range = slider_range(pivoted_kpi, "Reinvestment Ratio", "Reinvestment Ratio (ratio)")

filtered_kpi = pivoted_kpi.copy()
if rorb_range:
    filtered_kpi = filtered_kpi[filtered_kpi["RORB"].between(*rorb_range)]
if om_range:
    filtered_kpi = filtered_kpi[filtered_kpi["O&M Intensity"].between(*om_range)]
if cap_range:
    filtered_kpi = filtered_kpi[filtered_kpi["Capital Intensity"].between(*cap_range)]
if unit_op_range:
    filtered_kpi = filtered_kpi[filtered_kpi["Unit Operating Cost"].between(*unit_op_range)]
if reinvestment_range:
    filtered_kpi = filtered_kpi[filtered_kpi["Reinvestment Ratio"].between(*reinvestment_range)]

if filtered_kpi.empty:
    st.warning("No rows match the current filters.")
    st.stop()


column_order = [
    "Rank",
    "Asset",
    "RORB",
    "Rate Structure",
    "Capital Posture",
    "O&M Intensity",
    "Unit Operating Cost",
    "Capital Intensity",
    "Reinvestment Ratio",
    "% Negotiated Rate",
    "% Discount Rate",
    "% Volume Growth/Decline",
    "final_score",
]

filtered_kpi = filtered_kpi[column_order]

mobile_column_order = [
    "Rank",
    "Asset",
    "RORB",
    "O&M Intensity",
    "Rate Structure",
    "Capital Posture",
]


# ---- display

percent_cols = {
    "RORB": "Operating Income / Net Plant",
    "% Negotiated Rate": "Negotiated Revenue / Total Revenue",
    "% Discount Rate" : "Discount Revenue / Total Revenue",
    "% Volume Growth/Decline": "YoY throughput change"
}

ratio_cols = {
    "O&M Intensity": "O&M Expense / Rate Base",
    "Unit Operating Cost": "O&M Expense / Throughput",
    "Capital Intensity": "Rate Base / Throughput",
    "Reinvestment Ratio": "Capital Expenditures / Depreciation"
}



display_df = filtered_kpi.copy()
if mobile_view:
    display_df = display_df[mobile_column_order]

# Scale percent KPIs for display
for col in percent_cols:
    if col in display_df.columns:
        display_df[col] = display_df[col] * 100


column_config = {}

# Percent KPIs
for col, desc in percent_cols.items():
    if col in display_df.columns:
        column_config[col] = st.column_config.NumberColumn(
            label=col,
            help=desc,
            format="%.1f%%"
        )

# Ratio KPIs
for col, desc in ratio_cols.items():
    if col in display_df.columns:
        column_config[col] = st.column_config.NumberColumn(
            label=(
                "Unit Operating Cost ($/Dth)" if col == "Unit Operating Cost"
                else col
            ),
            help=desc,
            format="%.3f"
        )


st.dataframe(
    display_df,
    use_container_width=True,
    height=360 if mobile_view else 600,
    hide_index=True,
    column_config=column_config
)






with st.expander("KPI Methodology"):
    st.markdown("""
    **RORB** = Operating Income / Net Plant  
    **O&M Intensity** = O&M Expense / Rate Base  
    **Unit Operating Cost** = O&M Expense / Throughput  
    **Capital Intensity** = Rate Base / Throughput  
    **Reinvestment Ratio** = Capital Expenditures / Depreciation  
    """)






##------Plotly---------

st.markdown(
    "**This view compares capital returns against operating cost pressure to highlight where pipeline economics are structurally strong versus fragile.**"
)

import plotly.express as px

# Compute medians
x_med = pivoted_kpi["RORB"].median()
y_med = pivoted_kpi["O&M Intensity"].median()

# Axis ranges
x_min, x_max = pivoted_kpi["RORB"].min(), pivoted_kpi["RORB"].max()
y_min, y_max = pivoted_kpi["O&M Intensity"].min(), pivoted_kpi["O&M Intensity"].max()

# Quadrant centers
quad_centers = {
    "Under Pressure": ((x_med + x_max) / 2, (y_med + y_max) / 2),
    "Inefficient Earners": ((x_min + x_med) / 2, (y_med + y_max) / 2),
    "Mature / Stable Systems": ((x_min + x_med) / 2, (y_min + y_med) / 2),
    "Efficient Earners": ((x_med + x_max) / 2, (y_min + y_med) / 2),
}

# Scatter plot with asset labels
fig = px.scatter(
    filtered_kpi,
    x="RORB",
    y="O&M Intensity",
    text=None if mobile_view else "Asset",  # reduce clutter on mobile
    hover_name="Asset",
    color="Capital Posture",
    color_discrete_map={
        "Growth": "green",
        "Maintained": "royalblue",
        "Harvested": "firebrick",
    },
)

# Median lines
fig.add_vline(x=x_med, line_dash="dash")
fig.add_hline(y=y_med, line_dash="dash")

# Asset label styling
fig.update_traces(
    textposition="middle right",     # try top right / bottom right if crowded
    textfont_size=9 if mobile_view else 11,
    textfont_color="rgba(0,0,0,0.65)"
)

# Quadrant annotations (closer to center)
fig.add_annotation(
    x=quad_centers["Under Pressure"][0],
    y=quad_centers["Under Pressure"][1],
    text="<b>Under Pressure</b><br>High returns, high costs",
    showarrow=False,
    font=dict(size=10 if mobile_view else 12, color="gray"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Inefficient Earners"][0],
    y=quad_centers["Inefficient Earners"][1],
    text="<b>Inefficient Earners</b><br>Low returns, high costs",
    showarrow=False,
    font=dict(size=10 if mobile_view else 12, color="gray"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Mature / Stable Systems"][0],
    y=quad_centers["Mature / Stable Systems"][1],
    text="<b>Mature / Stable Systems</b><br>Low returns, low costs",
    showarrow=False,
    font=dict(size=10 if mobile_view else 12, color="gray"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Efficient Earners"][0],
    y=quad_centers["Efficient Earners"][1],
    text="<b>Efficient Earners</b><br>High returns, low costs",
    showarrow=False,
    font=dict(size=10 if mobile_view else 12, color="gray"),
    align="center"
)

# Layout
fig.update_layout(
    title=f"{year} Pipeline Economic Performance Quadrant",
    xaxis_title="Return on Rate Base (RORB)",
    yaxis_title="O&M Intensity (O&M / Rate Base)",
    height=440 if mobile_view else 700,
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

