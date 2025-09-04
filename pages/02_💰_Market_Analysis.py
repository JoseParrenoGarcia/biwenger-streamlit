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

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Analisis de Mercado")

# --- Global variables ---
player_stats_pd = load_player_stats()
current_team_pd = load_current_team_players()
market_value_pd = load_market_value()

st.write(market_value_pd.shape)
st.write(market_value_pd)