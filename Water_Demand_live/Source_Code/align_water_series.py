import pandas as pd
import numpy as np

def align_water_series(water_demand_df, water_content_df):
    """
    Aligns the dates in water demand and water content dataframes by adding missing dates with zero values in water content.
    
    Parameters:
    - water_demand_df: DataFrame containing water demand with 'Date' as the index.
    - water_content_df: DataFrame containing water content with 'Date' as the index.
    
    Returns:
    - Aligned water content DataFrame with missing dates filled with zero values.
    """

    # Identify dates in water_demand_df that are missing in water_content_df
    missing_dates = water_demand_df.index.difference(water_content_df.index)

    # Create a new DataFrame for the missing dates with zero water content
    missing_data_df = pd.DataFrame(index=missing_dates, data={'Water Content': 0})

    # Append missing dates with zero water content to the original water_content_df
    aligned_water_content_df = pd.concat([water_content_df, missing_data_df]).sort_index()
    aligned_water_content_df['Water Content']= aligned_water_content_df['Water Content'].rolling(window=5, min_periods=1).mean()

    # # Fill in any gaps with interpolation or smoothing as needed
    # aligned_water_content_df.interpolate(method='time', inplace=True)

    return aligned_water_content_df