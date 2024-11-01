import pandas as pd

def smooth_and_gap_fill(data, plot_id, data_name='Water Content', date_index=0, data_index=1, data_column=3):
    from PIL import Image
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.interpolate import CubicSpline
    from datetime import datetime, timedelta

    # Key growth stage dates
    growth_stages = {
        "Planting": "2024-05-31",
        "V9": "2024-07-09",
        "V12": "2024-07-16",
        "VT": "2024-07-22",
        "R2": "2024-08-06"
    }

    # Loop through time points and fetch a particular plot's data
    data_in_time = []
    times = []

    # Loop through time and locate a particular plot's data
    for i in data:
        plots_in_time = i[data_index]
        time = i[date_index]

        # Filter for the specific plot
        plot = plots_in_time[plots_in_time['Plot #'] == plot_id]
        
        if plot.empty:
            continue
        else:
            plot_data_in_time = plot.iloc[0, data_column]
            data_in_time.append(plot_data_in_time)
            times.append(time)

    # Check if data was collected
    if not data_in_time:
        print(f"No data found for Plot ID {plot_id}.")
        return pd.DataFrame(columns=["Date", "Value"])

    # Convert date strings to datetime objects
    time_points_dates = [datetime.strptime(date, "%Y-%m-%d") for date in times]
    
    # Calculate the day intervals from the first date
    time_points_intervals = [(date - time_points_dates[0]).days for date in time_points_dates]

    # Create a cubic spline interpolation model
    cs_model = CubicSpline(time_points_intervals, data_in_time)

    # Generate smooth daily time points and evaluate the spline
    smooth_time = np.arange(0, max(time_points_intervals) + 1, 1)  # Daily interpolation over the range of days
    smooth_values = cs_model(smooth_time)

    # Generate continuous date series
    start_date = time_points_dates[0]
    smooth_dates = [start_date + timedelta(days=int(day)) for day in smooth_time]

    # Create a DataFrame with the dates and smoothed values
    smooth_df = pd.DataFrame({
        "Water Content": smooth_values
    }, index=smooth_dates)  # Set dates as the index

    # Plot original vs smoothed data
    # plt.figure(figsize=(12, 8))
    # plt.plot(time_points_intervals, data_in_time, 'o', label='Original Data (weekly)')
    # plt.plot(smooth_time, smooth_values, '-', label='Smoothed (daily)', color='orange')

    # # Mark growth stages on the x-axis
    # for stage, date_str in growth_stages.items():
    #     stage_date = datetime.strptime(date_str, "%Y-%m-%d")
    #     days_since_start = (stage_date - time_points_dates[0]).days
    #     plt.axvline(x=days_since_start, color='gray', linestyle='--', linewidth=1)
    #     plt.text(days_since_start, max(data_in_time), stage, rotation=90, 
    #              verticalalignment='bottom', fontsize=10, color='gray')

    # Set custom x-ticks and labels
    # tick_indices = np.arange(0, len(smooth_time), 7)  # Adjust tick frequency as needed
    # plt.xticks(smooth_time[tick_indices], rotation=45)

    # # Labeling the axes and title
    # plt.xlabel('Days since planting', fontsize=12)
    # plt.ylabel(data_name, fontsize=12)  # Use data_name for y-axis label
    # plt.legend()
    # plt.title(f'{data_name} Time Series with Smoothing for Plot ID {plot_id}', fontsize=14)

    # # Adjust layout to prevent clipping of tick labels
    # plt.tight_layout()
    # plt.show()

    return smooth_df
