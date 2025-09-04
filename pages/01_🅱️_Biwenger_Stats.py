import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_player_stats,
    load_current_team_players
)
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

# --- Helper plotting functions ---
def render_player_scatter(
    df: pd.DataFrame,
    *,
    x_metric: str,
    y_metric: str,
    position_col: str = "position",
    player_name_col: str = "player_name",
    current_team_players: list[str] | None = None,
    extra_highlight_players: list[str] | None = None,
    position_colors: dict | None = None,
    show_tertiles: bool = True,
    height: int = 600,
) -> go.Figure:
    """
    Build a reusable scatter plot for player stats.

    Args:
        df: DataFrame with at least x_metric, y_metric, position_col, player_name_col.
        x_metric, y_metric: columns to plot on axes.
        position_col: column used for color grouping.
        player_name_col: column used for hover/labels.
        current_team_players: names to highlight with style A (purple).
        extra_highlight_players: names to highlight with style B (black).
        position_colors: mapping for position -> color string.
        show_tertiles: draw 33% and 67% quantile guide lines for both axes.
        height: chart height.

    Returns:
        Plotly Figure.
    """
    import numpy as np

    if df.empty:
        # Return an empty figure with a friendly annotation
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display with the current filters",
            x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False
        )
        fig.update_layout(height=height, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    if x_metric not in df.columns or y_metric not in df.columns:
        missing = [c for c in [x_metric, y_metric] if c not in df.columns]
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    # Ensure numeric (avoid plotly choking on strings)
    df_plot = df.copy()
    df_plot[x_metric] = np.round(pd.to_numeric(df_plot[x_metric], errors="coerce"),2)
    df_plot[y_metric] = np.round(pd.to_numeric(df_plot[y_metric], errors="coerce"), 2)
    df_plot = df_plot.dropna(subset=[x_metric, y_metric])

    # Default colors if none provided
    if position_colors is None:
        position_colors = {
            "1 - Portero": "rgb(253, 216, 53)",
            "2 - Defensa": "rgb(30, 136, 229)",
            "3 - Centrocampista": "rgb(67, 160, 71)",
            "4 - Delantero": "rgb(244, 81, 30)",
        }

    # Base scatter by position
    fig = px.scatter(
        df_plot,
        x=x_metric,
        y=y_metric,
        color=position_col,
        color_discrete_map=position_colors,
        hover_name=player_name_col if player_name_col in df_plot.columns else None,
        hover_data={
            x_metric: True,
            y_metric: True,
            position_col: False,
        },
        height=height,
    )

    # Helper for highlight layer
    def _highlight_layer(players: list[str], marker_color: str, line_color: str):
        if not players:
            return
        sub = df_plot[df_plot[player_name_col].isin(players)]
        if sub.empty:
            return
        fig.add_trace(
            go.Scatter(
                x=sub[x_metric],
                y=sub[y_metric],
                mode="markers",
                marker=dict(color=marker_color, line=dict(width=2, color=line_color), size=10),
                text=[
                    f"<b>{name}</b><br><br>{x_metric}: {x_val}<br>{y_metric}: {y_val}"
                    for name, x_val, y_val in zip(
                        sub[player_name_col], sub[x_metric], sub[y_metric]
                    )
                ],
                hoverinfo="text",
                showlegend=False,
            )
        )

    # Highlights
    _highlight_layer(current_team_players or [], "rgb(125, 60, 152)", "rgb(187, 143, 206)")
    _highlight_layer(extra_highlight_players or [], "black", "grey")

    # Tertile guides
    if show_tertiles and not df_plot.empty:
        try:
            x_tertiles = [df_plot[x_metric].quantile(q) for q in (0.33, 0.67)]
            y_tertiles = [df_plot[y_metric].quantile(q) for q in (0.33, 0.67)]
            guide_color = "rgb(248, 196, 113)"

            for x_val in x_tertiles:
                if pd.notna(x_val) and np.isfinite(x_val):
                    fig.add_vline(x=x_val, line_dash="dash", line_color=guide_color)
            for y_val in y_tertiles:
                if pd.notna(y_val) and np.isfinite(y_val):
                    fig.add_hline(y=y_val, line_dash="dash", line_color=guide_color)
        except Exception:
            # If quantiles fail for any reason, continue without guides
            pass

    # Axis titles & layout polish
    fig.update_layout(
        xaxis_title=x_metric.replace("_", " ").title(),
        yaxis_title=y_metric.replace("_", " ").title(),
        legend_title_text="Posición",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


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

    # --- Filter data based on selection ---
    if season:
        player_stats_pd = player_stats_pd[player_stats_pd['season'].isin(season)]
    if position:
        player_stats_pd = player_stats_pd[player_stats_pd['position'].isin(position)]
    if team:
        player_stats_pd = player_stats_pd[player_stats_pd['team'].isin(team)]

    # --- Visualise ---
    with st.container(border=True):
        position_colors = {
            "1 - Portero": "rgb(253, 216, 53)",
            "2 - Defensa": "rgb(30, 136, 229)",
            "3 - Centrocampista": "rgb(67, 160, 71)",
            "4 - Delantero": "rgb(244, 81, 30)"
        }

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
            position_colors=position_colors,
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
        # st.write(player_stats_pd)

        chart_cols_2 = st.columns([1, 1, 4])
        x_metric = chart_cols_2[0].selectbox("X-axis ", chart_metrics, index=0)
        y_metric = chart_cols_2[1].selectbox("Y-axis ", chart_metrics, index=1)

        fig = render_player_scatter(
            player_stats_pd,
            x_metric=x_metric,
            y_metric=y_metric,
            position_col="position",
            player_name_col="player_name",
            current_team_players=current_team_players,
            extra_highlight_players=[jugador_a_simular, jugador_a_simular_text],
            position_colors=position_colors,
            show_tertiles=True,
            height=chart_height,
        )

        st.plotly_chart(fig, use_container_width=False, key="simulation_chart")


