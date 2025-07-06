"""
This module contains functions to calculate the playing time of players.
"""

import pandas as pd


def calculate_period_lengths(df):
    """ 
    Get the length of each period in a game.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with Statsbomb event data for a certain game.

    Returns
    -------
    df_periods: pd.DataFrame
        Dataframe with the length of each period in a game.
    """

    df_end = df.loc[df['type_name'] == 'Half End', ['period', 'timestamp', 'minute', 'second', 'type_name', 'team_name']]
    df_periods = pd.DataFrame(columns=['period', 'length', 'additional_time', 'minutes_played', 'seconds_played', 'game_minute', 'game_second'])

    # Only check for first half, second half and extra time but not for penalties
    for period, total_length in [(1, 45), (2, 90), (3, 105), (4, 120)]:
        if period in df_end['period'].values:
            df_end_period = df_end.loc[df_end['period'] == period, ['timestamp', 'minute', 'second']].iloc[0]

            # Get played time of this period in minutes and seconds
            df_end_period['minutes_length'] = df_end_period['timestamp'].hour * 60 + df_end_period['timestamp'].minute
            df_end_period['seconds_length'] = df_end_period['timestamp'].second
            
            # Get period length and additional time in seconds
            period_length = df_end_period['minutes_length'] * 60 + df_end_period['seconds_length']
            period_additional_time = (df_end_period['minute'] * 60) + df_end_period['second'] - (total_length * 60)

            df_periods = pd.concat([
                df_periods,
                pd.DataFrame([{
                    'period': period,
                    'length': period_length,
                    'additional_time': period_additional_time,
                    'minutes_played': df_end_period['minutes_length'],
                    'seconds_played': df_end_period['seconds_length'],
                    'game_minute': df_end_period['minute'],
                    'game_second': df_end_period['second']
                }])
            ], ignore_index=True)

    return df_periods.reset_index(drop=True)


def get_substitution_events(df):
    """
    Get the substitution events for a given game.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with Statsbomb event data for a certain game.

    Returns
    -------
    df_subs: pd.DataFrame
        Dataframe with the substitution events for a given game.
    """
    subs_mask = (df['type_name'] == 'Substitution')
    subs_columns = ['match_id', 'period', 'minute', 'second', 'type_name', 'team_name', 'player_id', 'substitution_replacement_id']
    df_subs = df.loc[subs_mask, subs_columns]
    
    # Rename the columns to be more descriptive about the substitution
    df_subs.rename(columns={
        'player_id': 'player_off',
        'substitution_replacement_id': 'player_on'
    }, inplace=True)

    # Add column for substitution time
    df_subs['sub_time'] = df_subs['minute'] * 60 + df_subs['second']
    
    return df_subs.reset_index(drop=True)


def get_red_card_events(df):
    """
    Get the red card events for a given game.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with Statsbomb event data for a certain game.

    Returns
    -------
    df_cards: pd.DataFrame
        Dataframe with the red card events for a given game.
    """
    red_card_names = ['Red Card', 'Second Yellow']

    # Init mask
    cards_mask = pd.Series(False, index=df.index)

    # Check each column if it exists and update mask
    if 'foul_committed_card_name' in df.columns:
        cards_mask = cards_mask | df['foul_committed_card_name'].isin(red_card_names)
    
    if 'bad_behaviour_card_name' in df.columns:
        cards_mask = cards_mask | df['bad_behaviour_card_name'].isin(red_card_names)
    
    # Add card columns that exist
    card_columns = ['match_id', 'period', 'minute', 'second', 'type_name', 'team_name', 'player_id']
    if 'foul_committed_card_name' in df.columns:
        card_columns.append('foul_committed_card_name')
    if 'bad_behaviour_card_name' in df.columns:
        card_columns.append('bad_behaviour_card_name')

    # Get cards
    df_cards = df[cards_mask][card_columns]
    
    # Add column for card time
    df_cards['red_card_time'] = df_cards['minute'] * 60 + df_cards['second']
    
    return df_cards.reset_index(drop=True)


def calculate_playing_time_single_match(df):
    """ 
    Calculate the playing time (in seconds) of a player in a game.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with Statsbomb event data for a certain game.

    Returns
    -------
    df_playing_time: pd.DataFrame
        Dataframe with the playing time of a player in a game.
    """

    # Get period lengths and total game time
    df_periods = calculate_period_lengths(df)
    full_game_time = df_periods['length'].sum()

    # Get substitution events
    df_subs = get_substitution_events(df)

    # Get red card events
    df_reds = get_red_card_events(df)

    # Get players who played in the game and init their playing time
    df_players = df[['match_id', 'player_id']].drop_duplicates().dropna()    # dropna() because some events are not linked to players
    df_players['playing_time'] = full_game_time

    # Adapt playing time for players who were substituted
    for i, player in df_players.iterrows():
        player_id = player['player_id']
        player_playing_time = player['playing_time']
        
        # If player came on, how much time did they miss from the start of the game?
        if player_id in df_subs['player_on'].values:
            sub_on = df_subs[df_subs['player_on'] == player_id]
            period = sub_on['period'].iloc[0]
            missed_playing_time = sub_on['sub_time'].iloc[0]

            # loop through df_periods to add extra time to missed_playing_time from all periods before the sub
            for i, row in df_periods.iterrows():
                if row['period'] < period:
                    missed_playing_time += row['additional_time']
                else:
                    break

            total_playing_time = player_playing_time - missed_playing_time
            
            df_players.loc[df_players['player_id'] == player_id, 'playing_time'] = total_playing_time
        
        # If player came off, how much time did they miss to the end of the game?
        if player_id in df_subs['player_off'].values:
            sub_off = df_subs[df_subs['player_off'] == player_id]
            period = sub_off['period'].iloc[0]
            playing_time_before_sub = sub_off['sub_time'].iloc[0]

            missed_playing_time = full_game_time - playing_time_before_sub

            # loop through df_periods to add extra time to missed_playing_time from all periods after the sub
            for i, row in df_periods.iterrows():
                if row['period'] >= period and row['period'] < 4:
                    missed_playing_time += row['additional_time']
                else:
                    continue
            
            total_playing_time = player_playing_time - missed_playing_time
            
            df_players.loc[df_players['player_id'] == player_id, 'playing_time'] = total_playing_time
        
        # If player came off with a red card, how much time did they miss to the end of the game?
        if player_id in df_reds['player_id'].values:
            red_card_off = df_reds[df_reds['player_id'] == player_id]
            period = red_card_off['period'].iloc[0]
            playing_time_before_red_card = red_card_off['red_card_time'].iloc[0]
            missed_playing_time = full_game_time - playing_time_before_red_card

            # loop through df_periods to add extra time to missed_playing_time from all periods after the red card
            for i, row in df_periods.iterrows():
                if row['period'] >= period and row['period'] < 4:
                    missed_playing_time += row['additional_time']
                else:
                    continue
            
            total_playing_time = player_playing_time - missed_playing_time
            
            df_players.loc[df_players['player_id'] == player_id, 'playing_time'] = total_playing_time

    return df_players.reset_index(drop=True)


def calculate_playing_time(match_ids, df):
    """
    Calculate the playing time (in seconds) of players for the whole season.

    Parameters
    ----------
    match_ids: list
        A list of match ids to calculate the playing time for.
    df: pd.DataFrame
        A dataframe with all Statsbomb event data for all matches of a given competition and season.

    Returns
    -------
    df_playing_time: pd.DataFrame
        A dataframe with the playing time of players for the whole season.
    """

    # Init empty list for playing time dataframes
    playing_time_list = []

    # Loop through all matches and calculate the playing time for each player
    for match_id in match_ids:
        df_match = df[df['match_id'] == match_id]
        df_playing_time_match = calculate_playing_time_single_match(df_match)
        playing_time_list.append(df_playing_time_match)

    df_playing_time = pd.concat(playing_time_list)

    # Group by player_id and sum the playing time
    df_playing_time = df_playing_time.groupby('player_id').sum().reset_index()

    # Drop match_id column
    df_playing_time = df_playing_time.drop(columns=['match_id'])

    return df_playing_time