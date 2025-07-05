"""
Module to load data from StatsBomb.
"""
import pandas as pd
from mplsoccer import Sbopen

# Init StatsBomb parser
parser = Sbopen()

def get_all_match_ids(competition_id, season_id):
    """
    Get all match ids for a given competition and season.

    Parameters
    ----------
    competition_id: int
        The id of the competition
    season_id: int
        The id of the season

    Returns
    -------
    match_ids: list
        A list of all match ids for a given competition and season
    """
    df_all_matches = parser.match(competition_id=competition_id, season_id=season_id)
    match_ids = df_all_matches['match_id'].tolist()
    
    return match_ids


def load_all_events(match_ids):
    """
    Combine all events for all matches for a given competition and season.

    Parameters
    ----------
    match_ids: list
        A list of all match ids for a given competition and season

    Returns
    -------
    df_all_events: pd.DataFrame
        A dataframe with all Statsbomb event data for all matches of a given competition and season
    """
    
    # Init empty list to store all events
    all_events = []

    # Loop through all matches
    for match_id in match_ids:
        df_match = parser.event(match_id)[0]
        all_events.append(df_match)

    # Concatenate all events
    df_all_events = pd.concat(all_events, ignore_index=True)

    return df_all_events