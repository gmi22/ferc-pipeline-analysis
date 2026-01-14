import pandas as pd
from db.connections import get_connection
from db.queries import GET_OPERATING_REVENUE,GET_Miles,GET_OPEX,GET_Volume,GET_Negotiated_Revenue,GET_NetPlant,GET_KPIs,GET_Assets,GET_OPERATING_REVENUE_ALL

def fetch_operating_revenue(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_revenue = pd.read_sql(
        GET_OPERATING_REVENUE,
        conn,
        params=("OperatingRevenues", year)
    )
    conn.close()
    return df_revenue


def fetch_miles(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_miles = pd.read_sql(
        GET_Miles,
        conn,
        params=(year,)
    )
    conn.close()
    return df_miles



def fetch_opex(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_opex = pd.read_sql(
        GET_OPEX,
        conn,
        params=("OperationExpense", year)
    )
    conn.close()
    return df_opex



def fetch_depreciation(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_depreciation = pd.read_sql(
        GET_Volume,
        conn,
        params=("DepreciationExpense", year)
    )
    conn.close()
    return df_depreciation



def fetch_volume(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_volume = pd.read_sql(
        GET_Volume,
        conn,
        params=("RevenuesFromTransportationOfGasOfOthersThroughTransmissionFacilitiesAbstract", year)
    )
    conn.close()
    return df_volume



def fetch_negotiated_revenue(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_negotiated_revenue = pd.read_sql(
        GET_Negotiated_Revenue,
        conn,
        params=(year,)
    )
    conn.close()
    return df_negotiated_revenue



def fetch_net_plant(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_netplant = pd.read_sql(
        GET_NetPlant,
        conn,
        params=("UtilityPlantAndNuclearFuelNet",year)
    )
    conn.close()
    return df_netplant


def fetch_kpis(year: int) -> pd.DataFrame:
    conn = get_connection()
    df_kpis = pd.read_sql(
        GET_KPIs,
        conn,
        params=(year,)
    )
    conn.close()
    return df_kpis



def fetch_asset() -> pd.DataFrame:
    conn = get_connection()
    df_assets = pd.read_sql(
        GET_Assets,
        conn,

    )
    conn.close()
    return df_assets


def fetch_operating_revenue_all() -> pd.DataFrame:
    conn = get_connection()
    df_revenue_all = pd.read_sql(
        GET_OPERATING_REVENUE_ALL,
        conn,
        params=("OperatingRevenues",)
    )
    conn.close()
    return df_revenue_all


