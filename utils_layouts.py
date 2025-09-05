import streamlit as st

def filter_layouts(unique_season, unique_position, unique_teams, unique_players):
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

    return season, position, team, highlight_players