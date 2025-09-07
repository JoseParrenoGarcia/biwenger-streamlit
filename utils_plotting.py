import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


POSITION_COLOURS = {
            "1 - Portero": "rgb(253, 216, 53)",
            "2 - Defensa": "rgb(30, 136, 229)",
            "3 - Centrocampista": "rgb(67, 160, 71)",
            "4 - Delantero": "rgb(244, 81, 30)"
        }

POSITION_ORDER = [
    "1 - Portero",
    "2 - Defensa",
    "3 - Centrocampista",
    "4 - Delantero"
]

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
        category_orders={position_col: POSITION_ORDER},  # <-- force legend order
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

def render_value_timeseries(
    df: pd.DataFrame,
    *,
    title: str = "Evolución del valor de mercado",
    date_col: str = "date",
    value_col: str = "value",
    player_col: str = "player_name",
    players: list[str] | None = None,
    height: int = 420,
    days_back: int = 365,
) -> go.Figure:
    """
    Minimal time-series: one line per player for 'value' over time.
    """
    # Basic validation
    missing = [c for c in [date_col, value_col, player_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No time-series data available",
            x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False
        )
        fig.update_layout(height=height, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[date_col, value_col])

    if players:
        d = d[d[player_col].isin(players)]

    d = d.sort_values([player_col, date_col])

    if days_back == 365:
        markers = False
    else:
        markers = True

    fig = px.line(
        d,
        x=date_col,
        y=value_col,
        color=player_col,
        height=height,
        markers=markers,
        category_orders={player_col: POSITION_ORDER},
        color_discrete_sequence=px.colors.qualitative.G10,
    )

    fig.add_hline(y=0, line_dash="dot", line_color="grey")

    fig.update_traces(
        connectgaps=True,
        hovertemplate="<b>%{fullData.name}</b><br>Fecha: %{x}<br>Valor: %{y}<extra></extra>"
    )
    fig.update_layout(
        title=title + ": " + value_col,
        xaxis_title="Fecha",
        yaxis_title="Valor",
        legend_title_text="Jugador",
    )

    return fig
