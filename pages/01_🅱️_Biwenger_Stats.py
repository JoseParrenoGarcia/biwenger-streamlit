import streamlit as st
import pandas as pd
import numpy as np
from utils import (
    load_player_stats,
    load_current_team_players
)
from utils_plotting import (
    render_player_scatter,
    POSITION_COLOURS
)
from utils_layouts import filter_layouts
import re

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Estadisticas de jugadores de Biwenger")

# --- Session state initialization ---

# --- Global variables ---
player_stats_pd = load_player_stats()
current_team_pd = load_current_team_players()

unique_teams = sorted(player_stats_pd['team'].dropna().unique().tolist())
unique_position = sorted(player_stats_pd['position'].dropna().unique().tolist())
unique_players = sorted(player_stats_pd['player_name'].dropna().unique().tolist())
unique_season = sorted(player_stats_pd['season'].dropna().unique().tolist(), reverse=True)
current_team_players = sorted(current_team_pd['name'].dropna().unique().tolist())

# --- Main page ---
st.title("Explora las estadisticas de los jugadores de Biwenger")

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
        chart_metrics = ['points', 'value', 'matches_played', 'average', 'points_per_value']
        x_metric = chart_cols[0].selectbox("X-axis", chart_metrics, index=0)
        y_metric = chart_cols[1].selectbox("Y-axis", chart_metrics, index=1)

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

    with st.container(border=True):
        st.subheader("Simula el valor por puntos segun tu coste esperado")
        st.write("###### Si vas a fichar a un jugador, ¿cuanto te costaria por punto?")

        jugador_a_simular = st.selectbox("Jugador a simular", options=unique_players)
        jugador_a_simular_text = jugador_a_simular + ' (Simulado)'

        coste_de_jugador = re.sub(r"[^\d]", "", st.text_input("Coste del jugador (€)", value="€2,500,000"))
        coste_de_jugador = int(coste_de_jugador) if coste_de_jugador else 0

        player_stats_pd_simulation = (
            player_stats_pd.copy()
            .query("player_name == @jugador_a_simular or player_name not in @unique_players")
            .assign(value = coste_de_jugador,
                    points_per_value = lambda df: np.round(np.maximum(0, df['points'] / df['value'].replace(0, pd.NA))*100_000, 2),
                    player_name = jugador_a_simular_text,
                    )
        )

        player_stats_pd = pd.concat([player_stats_pd_simulation, player_stats_pd])

        chart_cols_2 = st.columns([1, 1, 4])
        x_metric = chart_cols_2[0].selectbox("X-axis ", chart_metrics, index=0)
        y_metric = chart_cols_2[1].selectbox("Y-axis ", chart_metrics, index=len(chart_metrics)-1)

        fig = render_player_scatter(
            player_stats_pd,
            x_metric=x_metric,
            y_metric=y_metric,
            position_col="position",
            player_name_col="player_name",
            current_team_players=current_team_players,
            extra_highlight_players=[jugador_a_simular, jugador_a_simular_text],
            position_colors=POSITION_COLOURS,
            show_tertiles=True,
            height=chart_height,
        )

        st.plotly_chart(fig, use_container_width=False, key="simulation_chart")


