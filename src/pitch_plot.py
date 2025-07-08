"""
This module contains functions to create pitch plots.
"""

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from mplsoccer import Pitch
import numpy as np
from pathlib import Path

def create_pitch_plot(df_dribbles, player_id, player_name, team_name):
    """
    Create a pitch plot for a player.

    Parameters
    ----------
    df_dribbles: pd.DataFrame
        The dataframe with all dribbles of the season.
    player_id: int
        The id of the player to create the pitch plot for.
    player_name: str
        The name of the player to create the pitch plot for.
    team_name: str
        The name of the team of the player to create the pitch plot for.
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Filter dribbles for player
    df_player_dribbles = df_dribbles[df_dribbles['player_id'] == player_id]
    
    # Plot dimensions
    title_height_ratio = 0.05
    legend_height_ratio = 0.125
    figsize = (12, 11)
    #figsize = (10, 8)
    
    # Plot colors
    background_color = "#f2f4ee"
    dark_color = "#053225"
    danger_dribble_color = "#CA2E55"

    # Text styles
    font = 'Futura'
    h1_size = 18
    h2_size = 16
    h3_size = 14
    p_size = 12
    label_size = 10
    alpha = 0.4

    # Apply styling
    plt.rcParams['font.family'] = font
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
    main_ax = fig.add_subplot(gs[1])

    # Legend axis
    legend_ax = fig.add_subplot(gs[2])
    legend_ax.axis('off')



    # HEADING AXIS
    heading_ax.text(0.055, 0.8, f"{player_name} - {team_name}", fontsize=h1_size, ha='left', va='center')
    heading_ax.text(0.055, -0.1, f'All dribbles at Euro 2024', fontsize=p_size, ha='left', va='center', alpha=alpha)

    # Add Euros 2024 logo
    logo = mpimg.imread(project_root / 'assets' / 'euro_2024_logo.png')
    imagebox = OffsetImage(logo, zoom=0.2)
    ab = AnnotationBbox(
        imagebox, 
        (0.95, 0.5),                # Position of the logo (x, y)
        xycoords='axes fraction',   # Coordinate system for the position (fraction of the axes)
        box_alignment=(1, 0.5),     # Alignment of the logo relative to the position (x, y) (0, 0) is top left, (1, 1) is bottom right
        frameon=False,              # Remove frame
        zorder=100                  # Ensure the logo is on top of other elements
    )
    heading_ax.add_artist(ab)



    # MAIN AXIS
    pitch = Pitch(
        line_color=dark_color, 
        linewidth=0.5, 
        half=False, 
        goal_type='box', 
        corner_arcs=True,
        pad_bottom=0.1
    )
    pitch.draw(ax=main_ax)
    main_ax.set_facecolor(background_color)

    # Create style arrays based on conditions
    colors = np.where(
        (df_player_dribbles['outcome_name'] == "Complete") & 
        (df_player_dribbles['danger_dribble'] == True),
        danger_dribble_color,
        dark_color
    )

    alphas = np.where(
        df_player_dribbles['outcome_name'] == "Complete",
        1.0,
        0.4
    )

    # Size points based on xG
    sizes = 100 + (df_player_dribbles['xg_from_dribble'] * 1500)

    # Plot all points at once
    pitch.scatter(
        df_player_dribbles['x'], 
        df_player_dribbles['y'], 
        c=colors, 
        s=sizes, 
        alpha=alphas, 
        edgecolors="none", 
        ax=main_ax
    )



    # LEGEND AXIS
    legend_ax.scatter(0, 0, c=dark_color, s=300, alpha=0)
    legend_ax.scatter(1, 1, c=dark_color, s=300, alpha=0)

    legend_ax.text(0.0, 1.4, f'Danger dribbles: dribbles that end in a shot within 15 seconds', fontsize=label_size-2, ha='left', va='center', alpha=alpha)
    legend_ax.text(1, 1.4, f'Data provided by StatsBomb', fontsize=label_size-2, ha='right', va='center', alpha=alpha)

    # Completed dribbles
    total_completed_dribbles = len(df_player_dribbles[df_player_dribbles['outcome_name'] == "Complete"])
    legend_ax.scatter(0.05, 0.84, c=dark_color, s=400)
    legend_ax.text(0.05, 0.81, total_completed_dribbles, fontsize=label_size, ha='center', va='center', color=background_color)
    legend_ax.text(0.08, 0.81, 'Completed dribbles', fontsize=p_size, ha='left', va='center', color=dark_color)
    
    # Danger dribbles
    total_danger_dribbles = len(df_player_dribbles[df_player_dribbles['danger_dribble'] == True])
    legend_ax.scatter(0.43, 0.84, c=danger_dribble_color, s=400)
    legend_ax.text(0.43, 0.81, total_danger_dribbles, fontsize=label_size, ha='center', va='center', color=background_color)
    legend_ax.text(0.46, 0.81, 'Danger dribbles', fontsize=p_size, ha='left', va='center', color=danger_dribble_color)
    
    # Failed dribbles
    total_failed_dribbles = len(df_player_dribbles[df_player_dribbles['outcome_name'] == "Incomplete"])
    legend_ax.scatter(0.795, 0.84, c=dark_color, s=400, alpha=alpha, edgecolors='none')
    legend_ax.text(0.795, 0.81, total_failed_dribbles, fontsize=label_size, ha='center', va='center', color=background_color)
    legend_ax.text(0.825, 0.81, 'Failed dribbles', fontsize=p_size, ha='left', va='center', color=dark_color, alpha=alpha)

    # xG
    legend_ax.scatter(0.385, 0.2, c=danger_dribble_color, s=100)
    legend_ax.scatter(0.415, 0.2, c=danger_dribble_color, s=200)
    legend_ax.scatter(0.4525, 0.2, c=danger_dribble_color, s=400)
    legend_ax.text(0.56, 0.2, 'xG from dribble', fontsize=p_size, ha='center', va='center', color=danger_dribble_color)

    # Save plot
    default_kwargs = {
        'bbox_inches': 'tight',
        'pad_inches': 0.25,
        'facecolor': background_color,
        'dpi': 300
    }

    # Generate output path, save figure and return figure and path
    output_path = project_root / 'generated_images' / 'pitch_plots' / f'{player_id}.png'
    fig.savefig(output_path, **default_kwargs)
    
    return fig, str(output_path)