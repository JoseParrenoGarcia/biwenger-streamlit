import streamlit as st
import pandas as pd
from utils import (
    load_player_stats,
    load_market_value,
    load_player_matches,
    join_data
)

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Dev Work")

# --- Global variables ---
player_stats_pd = load_player_stats()
player_matches_pd = load_player_matches()
player_value_pd = load_market_value()

# Work with Mbappe
mbappe_stats = (
    player_stats_pd[player_stats_pd['player_name'] == 'Mbappé']
    .drop(columns=['season', 'position', 'team', 'status_detail', 'min_value', 'max_value', 'value'])
    .rename(columns={'points': 'total_points',
                     'average': 'points_per_game'},
            )
)

mbappe_value = player_value_pd[player_value_pd['player_name'] == 'Mbappé']
mbappe_matches = (
    player_matches_pd[player_matches_pd['player_name'] == 'Mbappé']
    .drop(columns=['season_label', 'best_xi', 'events', 'team', 'as_of_date'])
)


mbappe_full_data = pd.merge(
    mbappe_value,
    mbappe_matches,
    left_on=['player_name', 'date'],
    right_on=['player_name', 'match_date'],
    how='left'
)

mbappe_full_data = pd.merge(
    mbappe_full_data,
    mbappe_stats,
    left_on=['player_name', 'date'],
    right_on=['player_name', 'as_of_date'],
    how='left',
)


st.dataframe(mbappe_full_data)
st.write(mbappe_matches)
st.write(mbappe_stats)
# st.write(mbappe_value)
