# College Football Comparisons

This package creates a streamlit app that can be found here: https://college-football-comparisons.streamlit.app/.

Data for the app was gathered using the https://collegefootballdata.com/ APIs.

**4/17/2024: The requirements pin Streamlit and Streamlit-Aggrid to older versions. Streamlit-Aggrid is undergoing significant updates, and the app is broken with current versions. I plan to update compatibility once the updates reach a stable state.**

## Using the App

The app asks the user to select an FBS school and a season (currently 2014-2023). Once a team has been selected, the app displays the team's closest statistical comparisons in the dataset. Closeness is determined by the Statistical Similarity Score (SSS), a custom metric explained in the next section. The user can click on a comparison team to view more details about the similarities (and differences) between the two teams.

By default, SSS takes both offensive and defensive stats into account, as well as both regular box score and advanced stats. The user can change the app settings to compare just offenses or defenses and remove advanced stats from consideration.

## Statistical Similarity Score

### Overview

The SSS between teams $a$ and $b$ is defined as:

$$ SSS(a, b) = 1 - \frac{D(a, b)}{max_{x, y \in T} D(x, y)},$$

where $D$ is a Euclidean distance measure and $T$ is the set of all teams. The real work goes into defining a space where distances among teams can be measured.

### Defining a space

 * Use the collegefootballdata.com APIs to gather data
 * Preprocess the data to create a clean dataset with a set of columns from dump_columns.py
 * Standardize each column to have zero mean and unit variance
 * Transform the standardized dataset using Principal Component Analysis (PCA)
 * Keep just enough components to explain 90% of the variance in the data

Distances among teams are measured in this PCA subspace.

Note that the user can choose among 6 combinations of data they’d like the app to consider: [offense, defense, combined] x [advanced, no advanced]. The above process is actually completed 6 times, since each user-chosen data combination corresponds to a different subset of columns from dump_columns.py. In a sense, then, there are actually 6 different Statistical Similarity Scores defined in different spaces.

### Advantages

IN PROGRESS
