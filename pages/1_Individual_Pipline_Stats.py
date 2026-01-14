import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")



st.title("Pipline Stats")


from db.repository import fetch_operating_revenue, fetch_miles,fetch_volume,fetch_negotiated_revenue,fetch_net_plant,fetch_kpis,fetch_asset,fetch_operating_revenue_all

df_asset = fetch_asset()

df_asset = df_asset.drop_duplicates(subset=['Asset'])

df_asset= df_asset.sort_values(by='Asset', ascending=True)

df_asset = df_asset["Asset"].tolist()



asset = st.selectbox("Pipeline", df_asset)



df_revenue_all = fetch_operating_revenue_all()


df_revenue_filtered = df_revenue_all[df_revenue_all["Asset"] == asset]

revenue_pivot_df = (
    df_revenue_filtered
    .pivot_table(
        index="Asset",
        columns="Year",
        values="operating_revenue",
        aggfunc="sum"   # or mean, first, max, etc.
    ))






st.dataframe(
    revenue_pivot_df ,
    use_container_width=True,
)


