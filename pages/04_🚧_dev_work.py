import streamlit as st
import pandas as pd
from utils import (
    load_player_stats,
    load_market_value,
    load_player_matches,
)

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Dev Work")

# --- Global variables ---
player_stats_pd = load_player_stats()
player_matches_pd = load_player_matches()

st.write(player_matches_pd)

