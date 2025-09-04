from supabase_client.connection import get_supabase_client
from supabase_client.utils import (
    check_if_table_exists
)
import streamlit as st
import pandas as pd
import numpy as np

supabase = get_supabase_client()
player_stats_table_name = "biwenger_player_stats"
if not check_if_table_exists(supabase, player_stats_table_name):
    st.warning(f"⚠️ Table '{player_stats_table_name}' does not exist.")

current_team_table_name = "biwenger_current_team"
if not check_if_table_exists(supabase, current_team_table_name):
    st.warning(f"⚠️ Table '{current_team_table_name}' does not exist.")

player_value_table_name = "biwenger_player_value"
if not check_if_table_exists(supabase, player_value_table_name):
    st.warning(f"⚠️ Table '{player_value_table_name}' does not exist.")


@st.cache_data
def load_player_stats() -> pd.DataFrame:
    result = supabase.table(player_stats_table_name).select("*").execute()
    if result and result.data:
        # Remove unwanted keys from each record
        filtered_data = [
            {k: v for k, v in record.items() if k not in ['id', 'created_at']}
            for record in result.data
        ]
        return (
            pd.DataFrame(filtered_data)
            .assign(points_per_value=lambda df: np.round(np.maximum(0, df['points'] / df['value'].replace(0, pd.NA))*100_000, 2),
                    ratio_purchase_sales=lambda df: np.round(np.maximum(0, df['market_purchases_pct'] / df['market_sales_pct']).replace(0, pd.NA), 2),
                    position=lambda df: df['position'].map({
                        'Defender': '2 - Defensa',
                        'Forward': '4 - Delantero',
                        'Goalkeeper': '1 - Portero',
                        'Midfielder': '3 - Centrocampista'
                    })
                    )
        )
    return pd.DataFrame()

@st.cache_data
def load_current_team_players() ->  pd.DataFrame:
    result = supabase.table(current_team_table_name).select("*").execute()
    if result and result.data:
        # Remove unwanted keys from each record
        filtered_data = [
            {k: v for k, v in record.items() if k not in ['id', 'created_at']}
            for record in result.data
        ]
        return pd.DataFrame(filtered_data)
    return pd.DataFrame()

@st.cache_data
def load_market_value() -> pd.DataFrame:
    result = supabase.table(player_value_table_name).select("*").limit(5_000).execute()

    if result and result.data:
        # Remove unwanted keys from each record
        filtered_data = [
            {k: v for k, v in record.items() if k not in ['id', 'created_at']}
            for record in result.data
        ]
        df = pd.DataFrame(filtered_data)

        # Convert date column to datetime and sort
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['player_name', 'date']).reset_index(drop=True)

        # Group by player to calculate changes and rolling averages
        df = df.groupby('player_name').apply(lambda group: group.assign(
            # Day-on-day change
            value_change_1d=group['market_value_eur'].diff(),
            value_change_1d_pct=group['market_value_eur'].pct_change() * 100,

            # Week-on-week change (7 days)
            value_change_7d=group['market_value_eur'].diff(periods=7),
            value_change_7d_pct=group['market_value_eur'].pct_change(periods=7) * 100,

            # Month-on-month change (30 days)
            value_change_30d=group['market_value_eur'].diff(periods=30),
            value_change_30d_pct=group['market_value_eur'].pct_change(periods=30) * 100,

            # Rolling averages
            value_avg_7d=group['market_value_eur'].rolling(window=7, min_periods=1).mean(),
            value_avg_14d=group['market_value_eur'].rolling(window=14, min_periods=1).mean(),
            value_avg_30d=group['market_value_eur'].rolling(window=30, min_periods=1).mean()
        )).reset_index(drop=True)

        return df.sort_values(['player_name', 'date'], ascending=[True, False])
    return pd.DataFrame()
