import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")



st.title("Pipline Stats")


from db.repository import fetch_operating_revenue, fetch_miles,fetch_volume,fetch_negotiated_revenue,fetch_net_plant,fetch_kpis,fetch_asset,fetch_operating_revenue_all,fetch_revenue_data_all,fetch_volume_data_all

df_asset = fetch_asset()

df_asset = df_asset.drop_duplicates(subset=['Asset'])

df_asset= df_asset.sort_values(by='Asset', ascending=True)

df_asset = df_asset["Asset"].tolist()



asset = st.selectbox("Pipeline", df_asset)




##-----GET REVENUE-------
st.subheader("Revenue")

df_rev_data = fetch_revenue_data_all(asset)

df_rev_data  = df_rev_data.rename(columns={"(a)": "Account"})



df_rev_data_pivot= (
    df_rev_data
    .pivot_table(
        index="Account",
        columns="Year",
        values="Revenue",
         # or mean, first, max, etc.
    ))


df_rev_data_pivot = df_rev_data_pivot.style.format("{:,.0f}")



st.dataframe(
    df_rev_data_pivot,
    use_container_width=True,
)


##-----GET VOLUME-------
st.subheader("Volume (Dth)")

df_vol_data = fetch_volume_data_all(asset)

df_vol_data  = df_vol_data.rename(columns={"(a)": "Account"})





df_vol_data_pivot= (
    df_vol_data
    .pivot_table(
        index="Account",
        columns="Year",
        values="Volume",
         # or mean, first, max, etc.
    ))


df_vol_data_pivot = df_vol_data_pivot.style.format("{:,.0f}")



st.dataframe(
    df_vol_data_pivot,
    use_container_width=True,
)






