import streamlit as st
import pandas as pd
import numpy as np

# Get player stats
df_player_stats = pd.read_parquet("data/player_stats.parquet")

# Get dribbles
df_dribbles = pd.read_parquet("data/dribbles.parquet")

st.title("Best dribblers at Euro 2024")
st.write("This app analyzes the dribbling performance of players at Euro 2024.")

# Minutes and dribbles filters
col1, col2 = st.columns(2)
with col1:
    minutes_played_filter = st.number_input("Minimum minutes played", min_value=0, max_value=900, value=270, step=1)
with col2:
    dribbles_filter = st.number_input("Minimum dribbles", min_value=0, max_value=100, value=10, step=1)

st.markdown(f"Your selected options: {minutes_played_filter}")
st.markdown(f"Your selected options: {dribbles_filter}")


# Filter player stats
def filter_player_stats(df_player_stats, minutes_played_filter, dribbles_filter):
    df = df_player_stats.copy()
    if minutes_played_filter:
        df = df[df["playing_time"] >= minutes_played_filter * 60]
    if dribbles_filter:
        df = df[df["attempted_dribbles"] >= dribbles_filter]
    return df

df_player_stats_filtered = filter_player_stats(df_player_stats, minutes_played_filter, dribbles_filter)


st.write(f"Number of players: {len(df_player_stats_filtered)}")
st.dataframe(df_player_stats_filtered)

st.dataframe(df_dribbles)
st.write(f"Number of dribbles: {len(df_dribbles)}")
