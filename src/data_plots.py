"""
This module contains functions to prepare the data for plotting.
"""


from scipy import stats


def filter_players_by_position(df, position):
    """
    Filter players who have played in any of the specified positions.
    
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame with player stats including 'positions' column.
    position: str
        The position to filter by. Valid positions are: Defenders, Midfielders and Forwards.
    
    Returns
    -------
    pd.DataFrame
        Filtered player stats DataFrame.
    
    Raises
    ------
    ValueError
        If position is not one of the accepted values: "Defenders", "Midfielders" or "Forwards".
    """
    # Get position ids
    match position:
        case "Defenders":
            position_ids = {2, 3, 4, 5, 6, 7, 8}
        case "Midfielders":
            position_ids = {9, 10, 11, 12, 13, 14, 15, 16}
        case "Forwards":
            position_ids = {17, 18, 19, 20, 21, 22, 23, 24, 25}
        case _:
            raise ValueError(f"Invalid position: {position}. Valid positions are: Defenders, Midfielders and Forwards.")
    
    print(position_ids)
    
    return df[df['positions'].apply(lambda x: bool(x & position_ids))]


def calculate_radar_plot_data(df, player_id):
    """
    Calculate the data for the radar plot.

    Parameters
    ----------
    df: pd.DataFrame
        The dataframe with the player stats filtered by position (defender, midfielder, forward).
    player_id: int
        The id of the player to calculate the data for.

    Returns
    -------
    values: list
        The values for the radar plot.
    percentiles: list
        The percentiles for the radar plot.
    """

    plot_columns = [
        "goals_per90", "assists_per90", "shots_per90", "shots_xg_per90",
        "completed_dribbles_per90", "failed_dribbles_per90", "attempted_dribbles_per90", "dribble_success_rate",
        "danger_dribbles_per90", "danger_dribbles_xg_per90", "dribbles_to_goals_per90"
    ]

    columns_to_invert = ["failed_dribbles_per90"]

    # Create copy for percentile calculation
    df_percentile = df.copy()

    for column in columns_to_invert:
        df_percentile[column] = -df_percentile[column]

    # Filter for Doku
    df_player = df.loc[df["player_id"] == player_id, plot_columns]
    df_player_percentile = df_percentile.loc[df_percentile["player_id"] == player_id, plot_columns]

    # Values for radar plot
    values = [round(x, 2) for x in df_player.values[0]]

    # Calculate percentiles
    percentiles = [
        int(stats.percentileofscore(df_percentile[column], df_player_percentile[column].iloc[0])) 
        for column in plot_columns
    ]

    return values, percentiles