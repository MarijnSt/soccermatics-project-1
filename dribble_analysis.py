import streamlit as st
import pandas as pd
import numpy as np
from src.radar_plot import create_radar_plot, create_radar_path
from src.pitch_plot import create_pitch_plot, create_pitch_path
import os

@st.cache_data
def filter_player_stats(df_player_stats, position_filter, minutes_played_filter, dribbles_filter):
    df = df_player_stats.copy()

    # Apply filters
    if position_filter != "All":
        if position_filter == "Defenders":
            df = df[df["position"] == "defender"]
        elif position_filter == "Midfielders":
            df = df[df["position"] == "midfielder"]
        elif position_filter == "Forwards":
            df = df[df["position"] == "forward"]
    if minutes_played_filter:
        df = df[df["playing_time"] >= minutes_played_filter * 60]
    if dribbles_filter:
        df = df[df["attempted_dribbles"] >= dribbles_filter]

    # Convert playing time to minutes for display
    df["playing_time"] = df["playing_time"] / 60

    return df


def show_radar_plot(df, player_id, position_filter, minutes_played_filter, dribbles_filter):
    # Check if plot already exists
    plot_path = create_radar_path(player_id, position_filter, minutes_played_filter, dribbles_filter)
    if os.path.exists(plot_path):
        return plot_path

    fig, path = create_radar_plot(df, player_id, position_filter, minutes_played_filter, dribbles_filter)
    return path


def get_pitch_path(df_dribbles, player_id, player_name, team_name):
    # Check if plot already exists
    plot_path = create_pitch_path(player_id)
    if os.path.exists(plot_path):
        return plot_path

    fig, path = create_pitch_plot(df_dribbles, player_id, player_name, team_name)
    return path


# Get player stats and dribbles
df_player_stats = pd.read_parquet("data/player_stats.parquet")
df_dribbles = pd.read_parquet("data/dribbles.parquet")

st.title("Best dribblers at Euro 2024")
st.write("This app generates radar and pitch plots for the dribbling performance of players at Euro 2024.")

# Minutes and dribbles filters
with st.sidebar:
    st.subheader("Filter players")
    position_filter = st.segmented_control(
        "Position", 
        ["All", "Defenders", "Midfielders", "Forwards"],
        default="All"
    )
    minutes_played_filter = st.number_input("Minimum minutes played", min_value=0, max_value=900, value=270, step=1)
    dribbles_filter = st.number_input("Minimum dribbles", min_value=0, max_value=100, value=10, step=1)

# Filter player stats
df_player_stats_filtered = filter_player_stats(df_player_stats, position_filter, minutes_played_filter, dribbles_filter)
# st.write(f"Number of players: {len(df_player_stats_filtered)}")

# Select a player
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

with st.spinner("Generating radar plot..."):
    # Show radar plot
    radar_path = show_radar_plot(df_player_stats_filtered, selected_player_id, position_filter, minutes_played_filter, dribbles_filter)
    st.image(radar_path)
    #st.pyplot(fig)
    st.write(f"This radar plot shows how {selected_player_name} performed compared to other players from the table at the top of the page. Changing the player filters will also change this plot.")
    st.write(f"All stats are normalized to per 90 minutes. This gives a better comparison of players with different playing times.")
    st.write(f"Scores at the outer edge of the radar plot are among the best, while scores at the inner edge are among the worst compared to the other players.")

with st.spinner("Generating pitch plot..."):
    # Show pitch plot
    pitch_path = get_pitch_path(df_dribbles, selected_player_id, selected_player_name, selected_player_team)
    st.image(pitch_path)
    #st.pyplot(fig)
    st.write(f"This pitch plot shows all the dribbles of {selected_player_name} at Euro 2024. It shows successful, failed and danger dribbles.")
    st.write(f"Danger dribbles are dribbles that ended in a shot within 15 seconds. The size of the dribble points is scaled according to the xG of the shot.")