"""
This module contains functions to calculate the basic stats for players.
"""

import pandas as pd


def calculate_goals_assists(df):
    """
    Calculate the number of goals and assists for each player.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with all Statsbomb event data for all matches of a given competition and season.

    Returns
    -------
    df: pd.DataFrame
        A dataframe with the number of goals and assists for each player.
    """

    # Filter for goals
    goals_mask = ((df["outcome_id"] == 97) & (df["period"] != 5))       # goal id is 97, don't count penalties, own goals don't have a outcome_id
    df_goals = df.loc[goals_mask, ["player_id"]].copy()
    df_goals_count = df_goals.groupby("player_id").size().reset_index(name="goals")

    # Filter for assists
    assists_mask = (df["pass_goal_assist"] == True)
    df_assists = df.loc[assists_mask, ["player_id"]].copy()

    # Count assists per player
    df_assists_count = df_assists.groupby("player_id").size().reset_index(name="assists")

    # Merge goals and assists
    df_goals_assists = pd.merge(df_goals_count, df_assists_count, on="player_id", how="outer")

    # Fill missing values with 0
    df_goals_assists["goals"] = df_goals_assists["goals"].fillna(0)
    df_goals_assists["assists"] = df_goals_assists["assists"].fillna(0)

    # Set goals and assists to int
    df_goals_assists["goals"] = df_goals_assists["goals"].astype(int)
    df_goals_assists["assists"] = df_goals_assists["assists"].astype(int)

    return df_goals_assists


def calculate_shots_xg(df):
    """
    Calculate number of shots and total xG.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with all Statsbomb event data for all matches of a given competition and season.

    Returns
    -------
    df_xg_shots: pd.DataFrame
        Dataframe with xG from shots for players in a game.
    """
    
    # Filter for shots
    shots_mask = (df['type_name'] == 'Shot')
    df_shots = df.loc[shots_mask, ['player_id', 'type_name', 'shot_statsbomb_xg']].copy()
    df_shots.rename(columns={'shot_statsbomb_xg': 'shots_xg'}, inplace=True)

    # Group by player and count shots and sum xG
    df_xg_shots = df_shots.groupby('player_id').agg({'type_name': 'count', 'shots_xg': 'sum'}).reset_index()
    df_xg_shots.rename(columns={'type_name': 'shots'}, inplace=True)

    return df_xg_shots