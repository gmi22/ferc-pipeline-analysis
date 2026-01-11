import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")



st.title("Main App")
st.write("Select a page from the sidebar")

from db.repository import fetch_operating_revenue, fetch_miles,fetch_volume,fetch_negotiated_revenue,fetch_net_plant,fetch_kpis

st.title("Operating Revenue")

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



pivoted_kpi["Asset Economics"] = np.where(pivoted_kpi['% Negotiated Rate'] > .60, 'Negotiated', 'Cost of Service')  

def classify_capital_posture(ratio):
    if pd.isna(ratio):
        return None
    elif ratio < 0.8:
        return "Harvested"
    elif ratio <= 1.2:
        return "Maintained"
    else:
        return "Expanded"

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
    "Asset Economics",
    "Capital Posture",
    "O&M Intensity",
    "Unit Operating Cost",
    "Capital Intensity",
    "Reinvestment Ratio",
    "% Negotiated Rate",
    "% Volume Growth/Decline",
    "final_score",
]

pivoted_kpi = pivoted_kpi[column_order]


# ---- display

percent_cols = {
    "RORB": "Operating Income ÷ Net Plant",
    "% Negotiated Rate": "Negotiated Revenue ÷ Total Revenue",
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
    use_container_width=True,
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




fig, ax = plt.subplots(figsize=(12, 10))

# Scatter
ax.scatter(
    pivoted_kpi["RORB"],
    pivoted_kpi["O&M Intensity"],
    alpha=0.10
)

# Median lines
ax.axvline(pivoted_kpi["RORB"].median(), linestyle="--")
ax.axhline(pivoted_kpi["O&M Intensity"].median(), linestyle="--")

# Quadrant labels
ax.text(
    0.75, 0.90,
    "Under Pressure\nHigh returns, high costs",
    transform=ax.transAxes,
    fontsize=10,
    ha="center",
    va="center",
    alpha=0.8
)

ax.text(
    0.25, 0.90,
    "Inefficient Earners\nLow returns, high costs",
    transform=ax.transAxes,
    fontsize=10,
    ha="center",
    va="center",
    alpha=0.8
)

ax.text(
    0.25, 0.10,
    "Underperformers\nLow returns, low costs",
    transform=ax.transAxes,
    fontsize=10,
    ha="center",
    va="center",
    alpha=0.8
)

ax.text(
    0.75, 0.10,
    "Efficient Earners\nHigh returns, low costs",
    transform=ax.transAxes,
    fontsize=10,
    ha="center",
    va="center",
    alpha=0.8
)

# Labels
ax.set_xlabel("Return on Rate Base (RORB)")
ax.set_ylabel("O&M Intensity (O&M ÷ Rate Base)")
ax.set_title("Pipeline Economic Performance Quadrant")

# Optional annotations
for _, row in pivoted_kpi.iterrows():
    ax.annotate(
        row["Asset"],
        (row["RORB"], row["O&M Intensity"]),
        fontsize=8,
        alpha=0.7
    )

plt.tight_layout()

# 🔑 THIS is the Streamlit line
st.pyplot(fig)


