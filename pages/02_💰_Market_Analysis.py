import streamlit as st
import pandas as pd
from utils import (
    load_player_stats,
    load_current_team_players,
    load_market_value,
    join_data
)
from utils_plotting import (
    render_player_scatter,
    POSITION_COLOURS,
    render_value_timeseries
)
from utils_layouts import filter_layouts

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Analisis de Mercado")

# --- Global variables ---
player_stats_pd = load_player_stats()
current_team_pd = load_current_team_players()

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
    st.subheader("Evolucion del valor de mercado")
    st.write("###### Escoge jugadores a analizar")

    timeseries_filter_cols = st.columns([1, 2])

    with timeseries_filter_cols[0]:
        selected_players = st.multiselect(
            "Selecciona los jugadores",
            options=unique_players,
        )

    with timeseries_filter_cols[1]:
        period_filter = st.radio("Selecciona el numero de dias:",
                                 options=[7, 14, 30, 365],
                                 index=3,
                                 horizontal=True)

    # market_value_pd = load_market_value(player_names=selected_players)
    market_value_pd = join_data(player_names=selected_players)
    market_value_pd = market_value_pd[market_value_pd['date'] >= (market_value_pd['date'].max() - pd.Timedelta(days=period_filter))]

    if selected_players:
        fig_ts = render_value_timeseries(
            df=market_value_pd,
            title='Evolución del valor de mercado',
            date_col="date",
            value_col="market_value_eur",
            player_col="player_name",
            height=420,
            days_back=period_filter,
        )
        st.plotly_chart(fig_ts, use_container_width=True)

        fig_ts = render_value_timeseries(
            df=market_value_pd,
            title='Evolución del cambio diario del valor de mercado',
            date_col="date",
            value_col="value_change_1d",
            player_col="player_name",
            height=420,
            days_back=period_filter,
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.warning("No jugadores seleccionados")