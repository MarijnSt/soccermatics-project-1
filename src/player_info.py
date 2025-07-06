"""
This module contains functions to get the player info from the StatsBomb API.
"""

import pandas as pd
from mplsoccer import Sbopen

# Init StatsBomb parser
parser = Sbopen()


def get_player_positions(match_id):
    """
    Get the positions of players in a game.

    Parameters
    ----------
    match_id: int
        The match id of the game to get the player positions for.

    Returns
    -------
    df_player_positions: pd.DataFrame
        A dataframe with the player id and all the positions they played in a game.
    """
    # Get match event data and filter for player events
    df = parser.event(match_id)[0]
    df = df[df['player_id'].notna() & df['position_id'].notna()]

    # Group by player and collect unique positions
    df_player_positions = (
        df.groupby('player_id')['position_id']
        .agg(lambda x: set(x.astype(int)))
        .reset_index()
        .rename(columns={'position_id': 'positions'})
    )
    
    return df_player_positions

def get_player_info(match_ids):
    """
    Get player info (id, short name and position) from the Statsbomb lineups and tactics data.

    Parameters
    ----------
    match_ids: list
        A list of all match ids for a given competition and season

    Returns
    -------
    df_player_info: pd.DataFrame
        A dataframe with all basic player info.
    """

    # Init empty list to store all players
    all_players_data = []

    # Loop through all matches and add relevant player info to all_players_data
    for match_id in match_ids:
        # Get basic player info
        df_lineup = parser.lineup(match_id)[
            ['match_id', 'player_id', 'player_name', 'player_nickname', 'team_name']
        ]
        
        # Get positions of all players in the game
        df_player_positions = get_player_positions(match_id)

        # Merge player info with player positions
        match_player_data = pd.merge(
            df_lineup, 
            df_player_positions, 
            on='player_id', 
            how='left'
        )

        all_players_data.append(match_player_data)

    # Create dataframe with all data
    df_all_players = pd.concat(all_players_data, ignore_index=True)

    # Rename nickname to short_name
    df_all_players.rename(columns={'player_nickname': 'player_short_name'}, inplace=True)

    # Group by player_id and combine all positions into a single set
    df_unique_players = (
        df_all_players.groupby('player_id')
        .agg({
            'player_name': 'first',
            'player_short_name': 'first', 
            'team_name': 'first',
            'positions': lambda x: set().union(*x.dropna())  # Combine all position sets and drop null values
        })
        .reset_index()
    )

    return df_unique_players