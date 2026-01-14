import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")



st.title("Pipline Rank")


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

pivoted_kpi = pivoted_kpi.drop(columns=["rorb_score","om_score","reinvestment_score","Year","Qtr"])


column_order = [
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

pivoted_kpi = pivoted_kpi[column_order]


# ---- display

percent_cols = {
    "RORB": "Operating Income ÷ Net Plant",
    "% Negotiated Rate": "Negotiated Revenue ÷ Total Revenue",
    "% Discount Rate" : "Discount Revenue ÷ Total Revenue",
    "% Volume Growth/Decline": "YoY throughput change"
}

ratio_cols = {
    "O&M Intensity": "O&M Expense ÷ Rate Base",
    "Unit Operating Cost": "O&M Expense ÷ Throughput",
    "Capital Intensity": "Rate Base ÷ Throughput",
    "Reinvestment Ratio": "Capital Expenditures ÷ Depreciation"
}



display_df = pivoted_kpi.copy()

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
            label=col,
            help=desc,
            format="%.3f"
        )


st.dataframe(
    display_df,
    #use_container_width=True,
    height=600,
    column_config=column_config
)






with st.expander("KPI Methodology"):
    st.markdown("""
    **RORB** = Operating Income ÷ Net Plant  
    **O&M Intensity** = O&M Expense ÷ Rate Base  
    **Unit Operating Cost** = O&M Expense ÷ Throughput  
    **Capital Intensity** = Rate Base ÷ Throughput  
    **Reinvestment Ratio** = Capital Expenditures ÷ Depreciation  
    """)






##------Plotly---------



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
    "Underperformers": ((x_min + x_med) / 2, (y_min + y_med) / 2),
    "Efficient Earners": ((x_med + x_max) / 2, (y_min + y_med) / 2),
}

# Scatter plot with asset labels
fig = px.scatter(
    pivoted_kpi,
    x="RORB",
    y="O&M Intensity",
    text="Asset",                # show asset names
    hover_name="Asset",
    color="Capital Posture"
)

# Median lines
fig.add_vline(x=x_med, line_dash="dash")
fig.add_hline(y=y_med, line_dash="dash")

# Asset label styling
fig.update_traces(
    textposition="middle right",     # try top right / bottom right if crowded
    textfont_size=11,
    textfont_color="rgba(0,0,0,0.65)"
)

# Quadrant annotations (closer to center)
fig.add_annotation(
    x=quad_centers["Under Pressure"][0],
    y=quad_centers["Under Pressure"][1],
    text="<b>Under Pressure</b><br>High returns, high costs",
    showarrow=False,
    font=dict(size=12, color="gray"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Inefficient Earners"][0],
    y=quad_centers["Inefficient Earners"][1],
    text="<b>Inefficient Earners</b><br>Low returns, high costs",
    showarrow=False,
    font=dict(size=12, color="red"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Underperformers"][0],
    y=quad_centers["Underperformers"][1],
    text="<b>Underperformers</b><br>Low returns, low costs",
    showarrow=False,
    font=dict(size=12, color="gray"),
    align="center"
)

fig.add_annotation(
    x=quad_centers["Efficient Earners"][0],
    y=quad_centers["Efficient Earners"][1],
    text="<b>Efficient Earners</b><br>High returns, low costs",
    showarrow=False,
    font=dict(size=12, color="green"),
    align="center"
)

# Layout
fig.update_layout(
    title="Pipeline Economic Performance Quadrant",
    xaxis_title="Return on Rate Base (RORB)",
    yaxis_title="O&M Intensity (O&M ÷ Rate Base)",
    height=700,
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)


with st.sidebar:
    st.header("Filters")

