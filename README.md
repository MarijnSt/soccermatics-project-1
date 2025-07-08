# Soccermatics Pro - Project 1

In the first project of the Soccermatics Pro course we got the task to analyse a player and more specifically a part of their game we enjoyed. We could use any of the open data available.

Statsbomb has open data for Euro 2024 and I quickly chose to analyse Doku's dribbling ability as he was one of our better players at that tournament. I really enjoy his game but he gets a lot of criticism as well. A lot of fans say that all his fancy dribbling doesn't really contribute that much to the team.

You can read my analysis [here](https://www.linkedin.com/in/marijn-stammeleer).

I also developed a Streamlit app where you can generate the important plots for other players. You can find that [here](https://dribblers-euro-2024.streamlit.app).


### Important files/folder in this repository;
* dribble_analysis.py: Streamlit app that generates the two visualisations I made for this analysis
* src/: contain all the functions used to get the data from StatsBomb, transform it and use it to create visualisations
* notebooks/radar_plot.ipynb: notebook used to create and test out the radar plot to compare player stats
* notebooks/pitch_plot.ipynb: notebook used to create and test out pitch plot to show all dribbles of a player