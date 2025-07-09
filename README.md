# Soccermatics Pro - Project 1

## Project description
In the first project of the Soccermatics Pro course we got the task to analyse a player and more specifically a part of their game we enjoyed. We could use any available open data.

I decided to focus on Euro 2024 because it's the most recent tournament for which StatsBomb has open data.

As a Belgian football fan I wanted to analyse our team and chose to analyse Doku's dribbling ability. He's one of our most promising talents but he gets a lot of criticism as well. A lot of fans say that all his fancy dribbling doesn't really contribute that much to the team. That sounded like a pretty good research question to me!

## Analysis

We had to present a simple analysis with two figures in a way that coaches would easily understand. I created two plots:

1) Radar plot with different per 90 metrics
    * Easy to understand: score on the outside of the ring is good, inside of the ring is bad
    * Different metrics in one clear picture
    * Quickly analyse a player's profile: focus on dribbles, more of a finisher, dangerous player
    * Gives an idea how a player compares to the sample: the radar shows scores as percentiles
    * Can be improved with feedback from coaches: what is important for certain player roles? How can we translate that into new metrics?

2) Pitch plot with all dribbles of a player
    * Where does a player like to dribble?
    * Does a player have any zones where he's really dangerous or vulnerable?

These two plots can give a clear insight into the profile of a player and more specificaly his dribbling performance at the tournament.

> I posted my report on LinkedIn which you can read [here](https://www.linkedin.com/in/marijn-stammeleer).

## Streamlit app

When I was developing the analysis for Doku I played around a lot with different filters: comparing players of similar positions, increasing or decreasing the minimum amount of time played or dribbles attempted. Besides that I also looked at how other players performed.

It was really interesting to see so I developed a Streamlit app where you can generate the plots for other players with different parameters. You can find that app [here](https://dribblers-euro-2024.streamlit.app).


## Repository structure
[notebooks/](notebooks)
- Contains all the notebooks used to explore the data and create the visualisations
- Most code was refactored into seperate modules
- [radar_plot.ipynb](notebooks/radar_plot.ipynb): used to create and test out the radar plot
- [pitch_plot.ipynb](notebooks/pitch_plot.ipynb): used to create and test out the pitch plot
- [doku_analysis.ipynb](notebooks/doku_analysis.ipynb): my old analysis which I reworked into the radar and pitch plots

[src/](src)
- Contains all refactored code that's used to get the data from StatsBomb, transform it and use it to create visualisations

[dribble_analysis.py](dribble_analysis.py)
- Code for the Streamlit app

[data/](data)
- To speed up the Streamlit app, I decided to create two parquet files with the finished player stats and dribbles
- This data is created by running the [create_data.py](create_data.py) file

[assets/](assets)
- Contains the fonts and image(s) used in the plots