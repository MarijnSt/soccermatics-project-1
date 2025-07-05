"""
Module to get all (danger) dribbles
"""

import numpy as np
import pandas as pd

def get_dribbles_single_match(df, shot_window=15):
    """
    Get all dribbles for a match and add xG from danger dribbles.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with all Statsbomb event data for a single match.

    Returns
    -------
    df_dribbles: pd.DataFrame
        A dataframe with all dribbles for a single match and the xG for danger dribbles.
    """
    
    # Period start times in seconds
    period_starts = {
        1: 0,          # First half: start at 0:00
        2: 45 * 60,    # Second half: start at 45:00
        3: 90 * 60,    # First ET: start at 90:00
        4: 105 * 60    # Second ET: start at 105:00
    }

    # Relevant columns
    relevant_columns = [
        "match_id", "period", "minute", "second", "type_name", "team_name", "player_id", "outcome_name", "x", "y", "shot_statsbomb_xg"
    ]

    # Init dribbles list
    dribbles_list = []

    # Iterate through periods
    for period in [1, 2, 3, 4]:
        # Get all dribbles
        dribbles_mask = (
            (df["type_name"] == "Dribble") &
            (df["period"] == period)
        )
        
        dribbles_df = df.loc[dribbles_mask, relevant_columns].copy()

        if dribbles_df.empty:
            continue

        # Get all shots
        shots_mask = (
            (df["type_name"] == "Shot") &
            (df["period"] == period)
        )

        shots_df = df.loc[shots_mask, relevant_columns].copy()

        if shots_df.empty:
            continue

        # Init new columns
        dribbles_df['danger_dribble'] = False
        dribbles_df['xg_from_dribble'] = 0.0
        dribbles_df['dribble_to_goal'] = False

        # Look for danger dribbles
        for idx, dribble in dribbles_df.iterrows():
            # Skip if dribble is not successful
            if dribble['outcome_name'] != 'Complete':
                continue

            dribble_time = dribble['minute'] * 60 + dribble['second']
            dribble_team = dribble['team_name']

            # Filter shots by team
            df_team_shots = shots_df[shots_df['team_name'] == dribble_team]

            # Skip if no shots for team
            if df_team_shots.empty:
                continue

            # Calculate shot window
            team_shots_times = df_team_shots["minute"] * 60 + df_team_shots["second"]
            team_shots_start = team_shots_times - shot_window
            team_shots_start = np.maximum(team_shots_start, period_starts[period])
            
            # Check if this dribble is within any shot window
            is_dangerous = np.any((team_shots_start <= dribble_time) & (dribble_time <= team_shots_times))
            
            if is_dangerous:
                # Find which shots match with this dribble
                matching_shots = (team_shots_start <= dribble_time) & (dribble_time <= team_shots_times)
                
                # Get the matching shots data
                df_matching_shots = df_team_shots.loc[matching_shots]
                
                # Update dataframe
                dribbles_df.at[idx, 'danger_dribble'] = True
                dribbles_df.at[idx, 'xg_from_dribble'] = df_matching_shots['shot_statsbomb_xg'].values[0]
                dribbles_df.at[idx, 'dribble_to_goal'] = True if df_matching_shots['outcome_name'].values[0] == 'Goal' else False

        dribbles_list.append(dribbles_df)

    # Concatenate all dribbles
    df_dribbles = pd.concat(dribbles_list)

    # Filter out columns that are not needed
    df_dribbles = df_dribbles[[
        'match_id', 'type_name', 'player_id', 
        'outcome_name', 'x', 'y', 
        'danger_dribble', 'xg_from_dribble', 'dribble_to_goal'
    ]]
    
    return df_dribbles


def get_all_dribbles(match_ids, df):
    """

    Get all dribbles for a season and add xG from danger dribbles.

    Parameters
    ----------
    match_ids: list
        A list of match ids to get the dribbles for.
    df: pd.DataFrame
        A dataframe with all Statsbomb event data for all matches of a given competition and season.

    Returns
    -------
    df_dribbles: pd.DataFrame
        A dataframe with all dribbles for a season and the xG from danger dribbles.
    """

    # Init empty list for dribbles
    dribbles_list = []

    # Loop through all matches and get dribbles
    for match_id in match_ids:
        df_match = df[df['match_id'] == match_id]
        df_dribbles_match = get_dribbles_single_match(df_match)
        dribbles_list.append(df_dribbles_match)

    # Concatenate all dribbles
    df_dribbles = pd.concat(dribbles_list)
    
    return df_dribbles