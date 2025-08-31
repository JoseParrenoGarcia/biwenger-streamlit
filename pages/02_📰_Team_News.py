import streamlit as st

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="News scraper")

# --- Global variables ---
TEAMS = [
    "Alaves", "Athletic Bilbao", "Atletico Madrid", "Barcelona", "Betis",
    "Celta de Vigo", "Elche", "Espanyol", "Getafe", "Girona",
    "Levante", "Mallorca", "Osasuna", "Oviedo", "Rayo Vallecano",
    "Real Madrid", "Real Sociedad", "Sevilla FC", "Valencia", "Villareal"
]

# --- Team selector top of page ---
clicked_team = None

# First row (10 teams)
cols = st.columns(10)
for i in range(10):
    with cols[i].container(border=True):
        st.write("🛡️ [Logo placeholder]")  # replace with st.image() later
        if st.button(TEAMS[i], key=f"btn_{TEAMS[i]}", use_container_width=True):
            clicked_team = TEAMS[i]

# Second row (next 10 teams)
cols = st.columns(10)
for i in range(10, 20):
    with cols[i-10].container(border=True):
        st.write("🛡️ [Logo placeholder]")
        if st.button(TEAMS[i], key=f"btn_{TEAMS[i]}", use_container_width=True):
            clicked_team = TEAMS[i]

if clicked_team:
    st.success(f"You clicked: {clicked_team}")

