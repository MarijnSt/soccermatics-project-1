"""
This module contains functions to calculate the dribble stats for players.
"""

def calculate_dribble_stats(df):
    """
    Calculate the number of dribbles for a player in a season.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with all dribbles data for all matches of a given competition and season.

    Returns
    -------
    df_dribbles: pd.DataFrame
        A dataframe with the dribbles for each player: completed, failed and total dribbles.
    """

    # Count dribbles per player
    df_dribble_stats = (df
                        .groupby(['player_id', 'outcome_name'])
                        .size()
                        .unstack(fill_value=0))
    
    df_dribble_stats = df_dribble_stats.rename(columns={
        'Complete': 'completed_dribbles', 
        'Incomplete': 'failed_dribbles'
    })

    # Calculate total dribbles
    df_dribble_stats['attempted_dribbles'] = df_dribble_stats['completed_dribbles'] + df_dribble_stats['failed_dribbles']

    # Calculate success rate
    df_dribble_stats['dribble_success_rate'] = df_dribble_stats['completed_dribbles'] / df_dribble_stats['attempted_dribbles']

    return df_dribble_stats.reset_index()


def calculate_danger_dribble_stats(df):
    """
    Calculate the danger dribbles of players and the xG that came from them for the whole season.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with all dribbles data for all matches of a given competition and season.

    Returns
    -------
    df_danger_dribbles_stats: pd.DataFrame
        A dataframe with the danger dribble stats of players for the whole season.
    """

    # Filter for danger dribbles
    df_danger_dribbles = df[df['danger_dribble'] == True]

    # Group by player_id and calculate danger dribble stats
    df_danger_dribbles_stats = (df_danger_dribbles
                                .groupby('player_id')
                                .agg(
                                    danger_dribbles=('player_id', 'count'),  # Count danger dribbles
                                    danger_dribbles_xg=('xg_from_dribble', 'sum'),  # Sum xG created
                                    dribbles_to_goals=('dribble_to_goal', 'sum')  # Count dribbles to goals
                                )
                                .reset_index())
    
    # Calculate xG per dribble
    df_danger_dribbles_stats['xg_per_danger_dribble'] = df_danger_dribbles_stats['danger_dribbles_xg'] / df_danger_dribbles_stats['danger_dribbles']

    return df_danger_dribbles_stats