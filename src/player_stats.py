"""
This module contains functions to calculate the full player stats for a given player.
"""

from src.matches import get_all_match_ids, load_all_events
from src.dribbles import get_all_dribbles
from src.basic_stats import calculate_goals_assists, calculate_shots_xg
from src.dribble_stats import calculate_dribble_stats, calculate_danger_dribble_stats
from src.player_info import get_player_info
from src.playing_time import calculate_playing_time

def calculate_per90_columns(df, columns, playing_time_column="playing_time"):
    """
    Convert certainplayer stats to per 90 minutes.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame with player stats.
    columns: list
        List of columns to convert to per 90 minutes.
    playing_time_column: str
        Name of the column with the playing time.
    """

    # Filter out players with 0 playing time
    df_filtered = df[df[playing_time_column] > 0].copy()

    for column in columns:
        df_filtered[f"{column}_per90"] = df_filtered[column] / df_filtered[playing_time_column] * 5400

    return df_filtered


def calculate_player_stats(competition_id, season_id):
    """ 
    Create a dataframe with all player stats needed for the radar plot.

    Parameters
    ----------
    competition_id: int
        The id of the competition
    season_id: int
        The id of the season

    Returns
    -------
    df_player_stats: pd.DataFrame
        A dataframe with all relevant player stats.
    """

    # Get all match ids
    match_ids = get_all_match_ids(competition_id, season_id)

    # Combine all events for all matches
    df_all_events = load_all_events(match_ids)

    # Get all players in the tournament
    df_player_info = get_player_info(match_ids)

    # Init player stats dataframe based as a copy of the players info
    df_player_stats = df_player_info.copy()

    # Calculate playing time
    df_playing_time = calculate_playing_time(match_ids, df_all_events)

    # Calculate goals and assists
    df_goals_assists = calculate_goals_assists(df_all_events)

    # Calculate xG from shots
    df_xg_shots = calculate_shots_xg(df_all_events)

    # Get all dribbles
    df_dribbles = get_all_dribbles(match_ids, df_all_events)

    # Calculate dribbles
    df_dribble_stats = calculate_dribble_stats(df_dribbles)

    # Calculate danger dribbles
    df_danger_dribbles = calculate_danger_dribble_stats(df_dribbles)

    # Merge dataframes into df_player_stats
    df_player_stats = (
        df_player_stats
            .merge(df_playing_time, on='player_id', how='left')
            .merge(df_goals_assists, on='player_id', how='left')
            .merge(df_xg_shots, on='player_id', how='left')
            .merge(df_dribble_stats, on='player_id', how='left')
            .merge(df_danger_dribbles, on='player_id', how='left')
    )

    # Fill missing values with 0
    df_player_stats.fillna(0, inplace=True)             # Each column that can be empty is a number, so we can use fillna with 0
    
    # Convert int columns
    df_player_stats["playing_time"] = df_player_stats["playing_time"].astype(int)
    df_player_stats["goals"] = df_player_stats["goals"].astype(int)
    df_player_stats["assists"] = df_player_stats["assists"].astype(int)
    df_player_stats["shots"] = df_player_stats["shots"].astype(int)
    df_player_stats["completed_dribbles"] = df_player_stats["completed_dribbles"].astype(int)
    df_player_stats["failed_dribbles"] = df_player_stats["failed_dribbles"].astype(int)
    df_player_stats["attempted_dribbles"] = df_player_stats["attempted_dribbles"].astype(int)
    df_player_stats["danger_dribbles"] = df_player_stats["danger_dribbles"].astype(int)
    df_player_stats["dribbles_to_goals"] = df_player_stats["dribbles_to_goals"].astype(int)

    # Columns to convert to per 90 minutes
    convert_to_per90_columns = [
        "goals", "assists", "shots", "shots_xg",
        "completed_dribbles", "failed_dribbles", "attempted_dribbles",
        "danger_dribbles", "danger_dribbles_xg", "dribbles_to_goals"
    ]

    # Calculate per 90 columns
    df_player_stats = calculate_per90_columns(df_player_stats, convert_to_per90_columns)

    return df_player_stats.reset_index(drop=True)