import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_player_stats,
    load_current_team_players,
    load_market_value
)
from utils_plotting import render_player_scatter, POSITION_COLOURS
from utils_layouts import filter_layouts

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Analisis de Mercado")

# --- Global variables ---
player_stats_pd = load_player_stats()
current_team_pd = load_current_team_players()
market_value_pd = load_market_value()

unique_teams = sorted(player_stats_pd['team'].dropna().unique().tolist())
unique_position = sorted(player_stats_pd['position'].dropna().unique().tolist())
unique_players = sorted(player_stats_pd['player_name'].dropna().unique().tolist())
unique_season = sorted(player_stats_pd['season'].dropna().unique().tolist(), reverse=True)
current_team_players = sorted(current_team_pd['name'].dropna().unique().tolist())

# --- Main page ---
st.title("Explora las tendencias de mercado")

# --- Filters ---
with st.container(border=True):
    season, position, team, highlight_players = filter_layouts(
        unique_season=unique_season,
        unique_position=unique_position,
        unique_teams=unique_teams,
        unique_players=unique_players
    )

    # --- Filter data based on selection ---
    if season:
        player_stats_pd = player_stats_pd[player_stats_pd['season'].isin(season)]
    if position:
        player_stats_pd = player_stats_pd[player_stats_pd['position'].isin(position)]
    if team:
        player_stats_pd = player_stats_pd[player_stats_pd['team'].isin(team)]

    # --- Visualise ---
    with st.container(border=True):
        chart_height = 450

        st.subheader("Estadísticas a vista de gráfica")
        st.write("###### Escoge las métricas a comparar:")

        chart_cols = st.columns([1, 1, 4])
        chart_metrics = ['market_purchases_pct', 'market_sales_pct', 'market_usage_pct', 'ratio_purchase_sales', 'value']
        x_metric = chart_cols[0].selectbox("X-axis", chart_metrics, index=len(chart_metrics)-1)
        y_metric = chart_cols[1].selectbox("Y-axis", chart_metrics, index=len(chart_metrics)-2)

        fig = render_player_scatter(
            player_stats_pd,
            x_metric=x_metric,
            y_metric=y_metric,
            position_col="position",
            player_name_col="player_name",
            current_team_players=current_team_players,
            extra_highlight_players=highlight_players,
            position_colors=POSITION_COLOURS,
            show_tertiles=True,
            height=chart_height,
        )

        st.plotly_chart(fig, use_container_width=False, key="main_chart")

# st.dataframe(player_stats_pd.head())
# st.write(market_value_pd.shape)
# st.write(market_value_pd)