import streamlit as st
import pandas as pd
import numpy as np
from src.radar_plot import create_radar_plot
from src.pitch_plot import create_pitch_plot

@st.cache_data
def filter_player_stats(df_player_stats, minutes_played_filter, dribbles_filter):
    df = df_player_stats.copy()

    # Apply filters
    if minutes_played_filter:
        df = df[df["playing_time"] >= minutes_played_filter * 60]
    if dribbles_filter:
        df = df[df["attempted_dribbles"] >= dribbles_filter]

    # Convert playing time to minutes for display
    df["playing_time"] = df["playing_time"] / 60

    return df


@st.cache_data(show_spinner="Creating radar plot...")
def show_radar_plot(df, player_id, minutes_played_filter, dribbles_filter):
    fig, path = create_radar_plot(df, player_id, minutes_played_filter, dribbles_filter)
    return fig, path


@st.cache_data(show_spinner="Creating pitch plot...")
def show_pitch_plot(df_dribbles, player_id, player_name, team_name):
    fig, path = create_pitch_plot(df_dribbles, player_id, player_name, team_name)
    return fig, path


# Get player stats and dribbles
df_player_stats = pd.read_parquet("data/player_stats.parquet")
df_dribbles = pd.read_parquet("data/dribbles.parquet")

st.title("Best dribblers at Euro 2024")
st.write("This app analyzes the dribbling performance of players at Euro 2024.")

# Minutes and dribbles filters
col1, col2 = st.columns(2)
with col1:
    minutes_played_filter = st.number_input("Minimum minutes played", min_value=0, max_value=900, value=270, step=1)
with col2:
    dribbles_filter = st.number_input("Minimum dribbles", min_value=0, max_value=100, value=10, step=1)

# Filter player stats
df_player_stats_filtered = filter_player_stats(df_player_stats, minutes_played_filter, dribbles_filter)
# st.write(f"Number of players: {len(df_player_stats_filtered)}")

# Select a player
st.subheader(f"Select a player to see their stats and dribbles")
selected_player = st.dataframe(
    df_player_stats_filtered,
    column_config={
        "player_short_name": st.column_config.TextColumn(
            "Player",
            help="The name of the player"
        ),
        "team_name": st.column_config.TextColumn(
            "Team",
            help="The team of the player"
        ),
        "playing_time": st.column_config.NumberColumn(
            "Playing time",
            help="Number of minutes played by the player",
            format="%.0f",
        ),
        "goals": st.column_config.NumberColumn(
            "Goals",
            help="The number of goals scored by the player",
            format="%.0f",
        ),
        "assists": st.column_config.NumberColumn(
            "Assists",
            help="The number of assists by the player",
            format="%.0f",
        ),
        "shots": st.column_config.NumberColumn(
            "Shots",
            help="The number of shots taken by the player",
            format="%.0f",
        ),
        "shots_xg": st.column_config.NumberColumn(
            "Shots xG",
            help="Total xG from shots taken by the player",
            format="%.4f",
        ),
        "attempted_dribbles": st.column_config.NumberColumn(
            "Attempted dribbles",
            help="The total number of dribbles attempted by the player",
            format="%.0f",
        ),
        "completed_dribbles": st.column_config.NumberColumn(
            "Completed dribbles",
            help="The number of completed dribbles by the player",
            format="%.0f",
        ),
        "failed_dribbles": st.column_config.NumberColumn(
            "Failed dribbles",
            help="The number of failed dribbles by the player",
            format="%.0f",
        ),
        "dribble_success_rate": st.column_config.NumberColumn(
            "Dribble success rate",
            help="The success rate of dribbles by the player",
            format="%.2f",
        ),
        "danger_dribbles": st.column_config.NumberColumn(
            "Danger dribbles",
            help="Danger dribbles lead to a shot within 15 seconds",
            format="%.0f",
        ),
        "danger_dribbles_xg": st.column_config.NumberColumn(
            "Danger dribbles xG",
            help="Total xG from shots that were taken after a danger dribble",
            format="%.4f",
        ),
        "dribbles_to_goals": st.column_config.NumberColumn(
            "Dribbles to goals",
            help="The number of dribbles that lead to a goal",
            format="%.0f",
        ),
        "xg_per_danger_dribble": st.column_config.NumberColumn(
            "xG per danger dribble",
            help="Average xG per danger dribble",
            format="%.4f",
        ),

    },
    column_order=[
        "player_short_name", "team_name", "playing_time",
        "goals", "assists", "shots", "shots_xg",
        "attempted_dribbles", "completed_dribbles", "failed_dribbles", "dribble_success_rate",
        "danger_dribbles", "danger_dribbles_xg", "dribbles_to_goals", "xg_per_danger_dribble",

    ],
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun"
)

if not selected_player["selection"]["rows"]:
    st.info("Select a player to proceed with the analysis.")
    st.stop()

# Get stats for the selected player
selected_id = selected_player["selection"]["rows"][0]
selected_player_id = df_player_stats_filtered.iloc[selected_id]["player_id"]
selected_player_name = df_player_stats_filtered.iloc[selected_id]["player_short_name"]
selected_player_team = df_player_stats_filtered.iloc[selected_id]["team_name"]
# st.write(f"Selected player: {selected_player_id} - {selected_player_name} ({selected_player_team})")

# Show radar plot
fig, path = show_radar_plot(df_player_stats_filtered, selected_player_id, minutes_played_filter, dribbles_filter)
st.pyplot(fig)
st.image(path)

# Show pitch plot
fig, path = show_pitch_plot(df_dribbles, selected_player_id, selected_player_name, selected_player_team)
st.pyplot(fig)
st.image(path)