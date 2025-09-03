import streamlit as st
from supabase_client.connection import get_supabase_client
from supabase_client.utils import (
    check_if_table_exists
)
import pandas as pd

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="News scraper")

# --- Session state initialization ---

# --- Global variables ---
supabase = get_supabase_client()
player_stats_table_name = "biwenger_player_stats"
if not check_if_table_exists(supabase, player_stats_table_name):
    st.warning(f"⚠️ Table '{player_stats_table_name}' does not exist.")

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
            .assign(points_per_value=lambda df: df['points'] / df['value'].replace(0, pd.NA),
                    position=lambda df: df['position'].map({
                        'Defender': '2 - Defensa',
                        'Forward': '4 - Delantero',
                        'Goalkeeper': '1 - Portero',
                        'Midfielder': '3 - Centrocampista'
                    })
                    )
        )
    return pd.DataFrame()

player_stats_pd = load_player_stats()

unique_teams = sorted(player_stats_pd['team'].dropna().unique().tolist())
unique_position = sorted(player_stats_pd['position'].dropna().unique().tolist())
unique_players = sorted(player_stats_pd['player_name'].dropna().unique().tolist())
unique_season = sorted(player_stats_pd['season'].dropna().unique().tolist(), reverse=True)

# --- Main page ---
st.title("Explora las estadisticas de los jugadores de Biwenger")

# --- Filters ---
with st.container(border=True):
    cols = st.columns(4)
    season = cols[0].multiselect(
        "Temporada",
        options=unique_season,
        default=unique_season[0]
    )

    position = cols[1].multiselect(
        "Posicion",
        options=unique_position,
    )

    team = cols[2].multiselect(
        "Equipo",
        options=unique_teams,
    )

    highlight_players = cols[3].multiselect(
        "Destacar jugadores",
        options=unique_players,
    )

    # --- Chart layout cols ---
    metric_cols = ['points', 'value', 'matches_played', 'average']
    x_metric = cols[0].selectbox("X-axis", metric_cols, index=0)
    y_metric = cols[1].selectbox("Y-axis", metric_cols, index=1)

    # --- Filter data based on selection ---
    if season:
        player_stats_pd = player_stats_pd[player_stats_pd['season'].isin(season)]
    if position:
        player_stats_pd = player_stats_pd[player_stats_pd['position'].isin(position)]
    if team:
        player_stats_pd = player_stats_pd[player_stats_pd['team'].isin(team)]

    # Calculate tertiles for X and Y axes
    x_tertiles = [player_stats_pd[x_metric].quantile(q) for q in [0.33, 0.67]]
    y_tertiles = [player_stats_pd[y_metric].quantile(q) for q in [0.33, 0.67]]

    # --- Visualise ---
    st.subheader("Estadisticas a vista de grafica")

