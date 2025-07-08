"""
This module contains functions to create radar plots.
"""

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from matplotlib import font_manager
from mplsoccer import PyPizza
from pathlib import Path

from src.data_plots import calculate_radar_plot_data

# Get project root directory
project_root = Path(__file__).parent.parent

def create_radar_path(player_id, position_filter, minutes_played_filter, dribbles_filter):
    output_path = project_root / 'generated_images' / 'radar_plots' / f'{player_id}_{minutes_played_filter}min_{dribbles_filter}drib_{position_filter}.png'
    return str(output_path)


def create_radar_plot(df, player_id, position_filter, minutes_played_filter, dribbles_filter):
    """
    Create a radar plot for a player.

    Parameters
    ----------
    df: pd.DataFrame
        The dataframe with player stats.
    player_id: int
        The id of the player to calculate the data for.
    position_filter: str
        The position of the player to calculate the data for.
    minutes_played_filter: int
        The minimum minutes played to be included in the plot.
    dribbles_filter: int
        The minimum number of dribbles to be included in the plot.

    Returns
    -------
    fig: matplotlib.figure.Figure
        The radar plot.
    """ 
    # Get player and team name
    team_name = df.loc[df["player_id"] == player_id, "team_name"].values[0]
    player_name = df.loc[df["player_id"] == player_id, "player_short_name"].values[0]

    # Get player values and percentiles
    player_values, player_percentiles = calculate_radar_plot_data(df, player_id)

    # Plot dimensions
    title_height_ratio = 0.15
    legend_height_ratio = 0.1
    figsize = (12, 12)

    # Plot colors
    background_color = "#f2f4ee"
    dark_color = "#053225"
    general_stats_color = "#DC851F"
    dribble_stats_color = "#6D98BA"
    danger_dribble_stats_color = "#CA2E55"

    # Text styles
    h1_size = 18
    h2_size = 16
    h3_size = 14
    p_size = 12
    label_size = 8
    alpha = 0.4

    # Load font
    font_manager.fontManager.addfont('assets/Futura.ttc')
    prop = font_manager.FontProperties(fname='assets/Futura.ttc')

    # Apply styling
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams.update({
        'text.color': dark_color,
        'axes.labelcolor': dark_color,
        'axes.edgecolor': dark_color,
        'xtick.color': dark_color,
        'ytick.color': dark_color,
        'grid.color': dark_color,
    })

    # Create figure
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 1, height_ratios=[title_height_ratio, 1-title_height_ratio-legend_height_ratio, legend_height_ratio])
    
    # Set background
    fig.set_facecolor(background_color)
    
    # Title axis
    heading_ax = fig.add_subplot(gs[0])
    heading_ax.axis('off')
    
    # Main plot axis
    main_ax = fig.add_subplot(gs[1], polar=True)
    main_ax.set_facecolor(background_color)

    # Legend axis
    legend_ax = fig.add_subplot(gs[2])
    legend_ax.axis('off')

    # Add heading
    dribblers_text = position_filter.lower() if position_filter != "All" else "dribblers"
    heading_ax.text(0.01, 0.8, f"{player_name} - {team_name}", fontsize=h1_size, ha='left', va='center')
    heading_ax.text(0.01, 0.55, f'Per 90 stats vs other {dribblers_text}* at Euro 2024', fontsize=p_size, ha='left', va='center', alpha=alpha)

    # Add Euros 2024 logo
    logo = mpimg.imread(project_root / 'assets' / 'euro_2024_logo.png')
    imagebox = OffsetImage(logo, zoom=0.2)
    ab = AnnotationBbox(imagebox, (0.98, 0.7), xycoords='axes fraction', box_alignment=(1, 0.5), frameon=False)
    heading_ax.add_artist(ab)

    # MAIN
    params = [
        "Goals", "Assists", "Shots", "xG",
        "Completed Dribbles", "Failed Dribbles", "Attempted Dribbles", "Dribble Success Rate",
        "Danger Dribbles", "xG From\nDanger Dribbles", "Goals From\nDanger Dribbles"
    ]

    slice_colors = [general_stats_color] * 4 + [dribble_stats_color] * 4 + [danger_dribble_stats_color] * 3
    params_colors = [general_stats_color] * 4 + [dribble_stats_color] * 4 + [danger_dribble_stats_color] * 3

    # Init PyPizza class
    baker = PyPizza(
        params=params,                          # List of parameters
        background_color=background_color,      # Background color
        straight_line_color=background_color,   # Lines between slices
        straight_line_lw=1,                     # Linewidth for straight lines
        last_circle_color=background_color,     # Color for last circle
        last_circle_lw=2,                       # Linewidth of last circle
        other_circle_lw=0,                      # Linewidth for other circles
        inner_circle_size=5,                    # Size of inner circle
    )

    # Plot pizza
    baker.make_pizza(
        player_percentiles,                     # List of values
        ax=main_ax,
        param_location=115,
        color_blank_space="same",               # Color to fill blank space of slices
        blank_alpha=alpha,                      # Alpha for blank-space colors
        slice_colors=slice_colors,              # Color for individual slices
        value_bck_colors=slice_colors,          # Background color for the values box
        kwargs_params=dict(                     # Labels of slices on the outside of the pizza                 
            fontsize=p_size,                    
            va="center",                        
        ),
        kwargs_slices=dict(                     # Edges of slices
            edgecolor=background_color, 
            zorder=2, 
            linewidth=1
        ),
        kwargs_values=dict(                     # Values box
            color=background_color, 
            fontsize=p_size, 
            zorder=3,
            bbox=dict(
                edgecolor=background_color, 
                facecolor=background_color,
                boxstyle="round,pad=0.4", 
                lw=1
            )
        )
    )

    # Replace slice text with actual values (normally shows percentiles)
    texts = baker.get_value_texts()
    for i, text in enumerate(texts):
        text.set_text(str(player_values[i]))

    # Set param label colors individually
    param_texts = baker.get_param_texts()
    for i, text in enumerate(param_texts):
        text.set_color(params_colors[i])


    # LEGEND
    players_text = position_filter.lower() if position_filter != "All" else "players"
    legend_ax.text(0.01, 0.25, f'*: {players_text} with at least {minutes_played_filter} minutes and {dribbles_filter} attempted dribbles', fontsize=label_size, ha='left', va='center', alpha=alpha)
    legend_ax.text(0.01, 0.01, 'Danger dribbles: dribbles that end in a shot within 15 seconds', fontsize=label_size, ha='left', va='center', alpha=alpha)
    legend_ax.text(0.99, 0.01, 'Data provided by StatsBomb', fontsize=label_size, ha='right', va='center', alpha=alpha)

    # Save plot
    default_kwargs = {
        'bbox_inches': 'tight',
        'pad_inches': 0.5,
        'facecolor': background_color,
        'dpi': 300
    }
    
    # Generate output path, save figure and return figure and path
    output_path = create_radar_path(player_id, position_filter, minutes_played_filter, dribbles_filter)
    fig.savefig(output_path, **default_kwargs)
    
    return fig, output_path