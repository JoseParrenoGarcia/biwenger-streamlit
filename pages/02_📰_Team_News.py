import streamlit as st
import os

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="News scraper")

# --- Global variables ---
TEAMS = [
    "Alaves", "Athletic Bilbao", "Atletico Madrid", "Barcelona", "Betis",
    "Celta de Vigo", "Elche", "Espanyol", "Getafe", "Girona",
    "Levante", "Mallorca", "Osasuna", "Oviedo", "Rayo Vallecano",
    "Real Madrid", "Real Sociedad", "Sevilla FC", "Valencia", "Villareal"
]

CREST_DIR = "./team_crests"

# --- Team selector top of page ---
clicked_team = None

# First row (10 teams)
cols = st.columns(10)
for i in range(10):
    team = TEAMS[i]
    with cols[i].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        if os.path.exists(crest_path):
            st.image(crest_path, use_container_width=True)
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            clicked_team = team

# Second row (next 10 teams)
cols = st.columns(10)
for i in range(10, 20):
    team = TEAMS[i]
    with cols[i-10].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        if os.path.exists(crest_path):
            st.image(crest_path, use_container_width=True)
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            clicked_team = team

if clicked_team:
    st.success(f"You clicked: {clicked_team}")

