# Wildcat Hackathon 2024 🏆
[![Python](https://img.shields.io/badge/python-latest-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[[![CSS](https://img.shields.io/badge/CSS-Style-blue?logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Plotly](https://img.shields.io/badge/visualization-Plotly-blue)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Data%20Analysis-Pandas-150458?logo=pandas)](https://pandas.pydata.org/)
[![GeoPandas](https://img.shields.io/badge/Geospatial-GeoPandas-green?logo=python&logoColor=white)](https://geopandas.org/en/stable/)


**A dashboard utilizing data analysis, interactivity, and visualization to enhance sustainable water use, leveraging datasets from the [Testing Ag Performance Solutions (TAPS)](https://www.k-state.edu/taps/) program**
## ▶️ Demo
![](https://github.com/mingqianghan/TAPS-2024-Hackathon/blob/main/demo/demo.gif)
## 🔢 Data
- **Crop Water Stress Index (CWSI)**: Provided by Ceres Imaging
- **Management Data**: Collected by TAPS 
- **Soil Moisture Content (SMC)**: Measured using neutron probes.
- **Weather Data**: Sourced from [Kansas Mesonet](https://mesonet.k-state.edu/)

## 🚀 Features Overview
- Displays a geosatellite map with either a CWSI or SMC heat map overlay, selectable by the user.
- Highlights field plots experiencing water stress, allowing users to identify plots with the highest and lowest water stress levels.
- Enables users to click on individual plots to access detailed information about crop water status.
- Provides time series information based on a selected date, including irrigation, precipitation, water deficit, and water excess.
- Shows the water required by plants on a selected date and tracks cumulative irrigation from the beginning of the planting season up to that date.
- Uses OpenAI to generate actionable summaries from dashboard insights, offering users a quick, high-level overview of plot-specific conditions.
![](https://github.com/mingqianghan/TAPS-2024-Hackathon/blob/main/demo/Overview.png)

## 📂 Files

- **Water_Demand_live/** 
  - **Source_Code/** - Contains code for crop water status analysis
- **data process/** - Scripts for preprocessing CWSI images (not used by the dashboard)
- **data/** - Data used for the project
- **demo/** - Contains slides, GIFs, and other presentation materials
- **pages/**
  - `Crop Water Status.py` -  Dashboard "Crop Water Status" page source code
- `Home.py` -Dashboard "Home" page source code
- `Home_styles.html` - CSS style for custom styling on the "Home" dashboard page
- `calender_styles.css` - CSS style for styling calendar components in the dashboard
- `run_streamlit.bat` - Batch script to start the Streamlit server for local development
- `water_demand_style.html` - CSS style with custom styling on the "Crop Water Status" dashboard page

## 🤖 Contributors
- [Mingqiang Han](https://github.com/mingqianghan)
- [Albert Benson](https://github.com/aabensonAI)




