from src.matches import get_all_match_ids, load_all_events
from src.player_stats import calculate_player_stats
from src.dribbles import get_all_dribbles

# Get all match ids
match_ids = get_all_match_ids(competition_id=55, season_id=282)

# Get all events
print("Combining all events...")
df_all_events = load_all_events(match_ids)

# Get all player stats
print("Calculating player stats...")
df_player_stats = calculate_player_stats(match_ids, df_all_events, min_playing_time=1, min_attempted_dribbles=0)

# Save to parquet
print("Saving to parquet...")
df_player_stats.to_parquet("data/player_stats.parquet", index=False)

# Get all dribbles
print("Getting all dribbles...")
df_dribbles = get_all_dribbles(match_ids, df_all_events)

# Save to parquet
print("Saving to parquet...")
df_dribbles.to_parquet("data/dribbles.parquet", index=False)

print("Done!")