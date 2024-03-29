# College Football Comparisons

**3/29/24: Currently broken due to Streamlit and Streamlit-Aggrid updates. Working on a fix.**

This package creates a streamlit app that can be found here: https://college-football-comparisons.streamlit.app/.

## Using the App

The app asks the user to select an FBS school and a season (currently 2014-2023). Once a team has been selected, the app displays the team's closest statistical comparisons in the dataset. Closeness is determined by the Statistical Similarity Score (SSS), a custom metric explained below. The user can click on a comparison to view more details about the similarities (and differences) between the two teams.

By default, SSS takes both offensive and defensive stats into account, as well as both regular box score and advanced stats. The user can change the app settings to compare just offenses or defenses and remove advanced stats from consideration.

## Statistical Similarity Score
 
