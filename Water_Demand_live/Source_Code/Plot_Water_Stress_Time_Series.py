import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from Plot_Class import DefinePlot


def plot_water_stress_over_time5(field_time_series, plot_index, specified_date, num_cols=3, smoothing_window=5):
    """
    Plots water stress index maps for a specified plot over time and a time series plot of the mean water stress index.

    Parameters:
    - field_time_series: List of data entries, where each entry contains a date and plot data.
    - plot_index: Integer index of the plot to analyze (e.g., 0, 1, 2, etc.).
    - specified_date: Date until which to plot the data, must be within the time series.
    - smoothing_window: Size of the moving average window.
    """

    if specified_date:
        if isinstance(specified_date, str):
            specified_date = pd.to_datetime(specified_date).date()
        elif isinstance(specified_date, pd.Timestamp):
            specified_date = specified_date.date()
    # Define kc values for maize at various growth stages
    kc_values = {
        'Planting': 0.3,  # Before planting
        'V9': 0.7,        # Vegetative Stage 9
        'V12': 1.2,       # Vegetative Stage 12
        'VT/R1': 1.4,     # Tasseling / R1 Stage
        'R2': 1.2,        # R2 Stage (grain fill)
    }
    
    # Define colors for growth stages
    stage_colors = {
        'Planting': 'blue',
        'V9': 'green',
        'V12': 'yellow',
        'VT/R1': 'orange',
        'R2': 'red',
    }

    # Define descriptive labels for growth stages
    descriptive_labels = {
        'Planting': 'Planting',
        'V9': 'V9 - Vegetative',
        'V12': 'V12 - Tasseling',
        'VT/R1': 'VT/R1 - R1 Stage',
        'R2': 'R2 - Grain Fill',
    }
    
    growth_stages = list(kc_values.keys())
    
    # Initialize lists to store dates, mean water stress values, and calculated water demand
    dates = []
    water_stress_means = []
    water_demands = []
    growth_stage_dates = []
    growth_stage_labels = []

    # Load reference evapotranspiration data
    reference_et_df = pd.read_excel('Data_Required/Weather_Data/ref_evapotranspiration.xlsx')
    reference_et_df['Date'] = pd.to_datetime(reference_et_df['Date']).dt.date

    # num_plots = len(field_time_series)
    # num_rows = math.ceil(num_plots / num_cols)
    # fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 5 * num_rows))
    # axes = axes.flatten()  # Flatten the axes array for easier indexing

    # Initialize variable to store planting date
    planting_date = None

    # Iterate through each date in `field_time_series`
    for i, date_entry in enumerate(field_time_series):
        date = pd.to_datetime(date_entry[0]).date()  # Convert to datetime and extract only the date portion
        plots_data = date_entry[2]

        # Get data for the specified plot on this date
        plot_data = plots_data.loc[plots_data['Plot #'] == plot_index].squeeze()

        if not plot_data.empty:
            # Create a `DefinePlot` object for this date and plot
            plot = DefinePlot(plot_data, date)

            # Get water stress plot and its mean value
            water_stress_plot = plot.get_water_stress()
            mean_water_stress = plot.get_mean_water_stress()

            # Store date and mean water stress in lists for plotting
            dates.append(date)
            water_stress_means.append(mean_water_stress)

            # Get planting date and determine the current growth stage
            if planting_date is None:
                planting_date = pd.to_datetime(plot.get_planting_date()).date()
            
            current_growth_stage = 'Planting'  # Default stage is planting
            days_since_planting = (date - planting_date).days

            # Determine growth stage based on days since planting
            if days_since_planting >= 0:
                if days_since_planting < 30:
                    current_growth_stage = 'Planting'
                elif days_since_planting < 60:
                    current_growth_stage = 'V9'
                elif days_since_planting < 90:
                    current_growth_stage = 'V12'
                elif days_since_planting < 120:
                    current_growth_stage = 'VT/R1'
                else:
                    current_growth_stage = 'R2'

                # Append the growth stage transition date and label
                growth_stage_dates.append(date)
                growth_stage_labels.append(current_growth_stage)

            # Retrieve the corresponding reference ET for the current date
            et_row = reference_et_df[reference_et_df['Date'] == date]
            if not et_row.empty:
                reference_et = et_row['refET'].values[0]
            else:
                reference_et = 0

            # Calculate water demand based on current growth stage and ET
            kc = kc_values.get(current_growth_stage, 0)
            water_demand = kc * reference_et * mean_water_stress
            water_demands.append(water_demand)

            #show the variation of water stress for the plot specified
            # ax = axes[i]
            # im = ax.imshow(water_stress_plot, cmap='turbo')
            # ax.set_title(f"Plot {plot.get_plot_id()} on {date}")
            # ax.axis('off')

        else:
            #print('No Plots to show')
            # axes[i].axis('off')
            pass

    # # Remove empty axes
    # for j in range(i + 1, len(axes)):
    #     axes[j].axis('off')

    # Add a single colorbar for the entire grid
    # cbar = fig.colorbar(im, ax=axes, orientation='vertical', fraction=0.02, pad=0.02)
    # cbar.set_label('Index Value')

    # plt.tight_layout()
    # plt.show()

    # Prepare data for time series plotting
    if dates:
        # Create a DataFrame for time series analysis
        time_series_df = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Mean Water Stress': water_stress_means,
            'Water Demand': water_demands
        })

        # Set date as index and reindex to fill missing dates
        time_series_df.set_index('Date', inplace=True)
        time_series_df = time_series_df.reindex(pd.date_range(start=time_series_df.index.min(), end=time_series_df.index.max()))

        # Interpolate missing values
        time_series_df.interpolate(method='time', inplace=True)

        # Apply moving average for smoothing
        time_series_df['Mean Water Stress'] = time_series_df['Mean Water Stress'].rolling(window=smoothing_window, min_periods=1).mean()
        time_series_df['Water Demand'] = time_series_df['Water Demand'].rolling(window=smoothing_window, min_periods=1).mean()

        # Filter data to include only from planting date to specified date
        time_series_df = time_series_df[planting_date:specified_date]

        print(time_series_df)

        # Plot the mean water stress and water demand over time
        plt.figure(figsize=(10, 6))
        plt.plot(time_series_df.index, time_series_df['Water Demand'], marker='x', linestyle='-', color='r', label='Water Demand (mm)')

        # Add vertical lines for growth stage transitions with corresponding colors
        for i, growth_stage_date in enumerate(growth_stage_dates):
            if planting_date <= growth_stage_date <= specified_date:
                growth_stage = growth_stage_labels[i]
                plt.axvline(x=growth_stage_date, color=stage_colors[growth_stage], linestyle='--', label=descriptive_labels[growth_stage])

        plt.xlabel("Date")
        plt.ylabel("Water Demand (mm)")
        plt.title(f"Water Demand and Mean Water Stress Over Time for Plot ID {plot.get_plot_id()}\n (from {planting_date} to {specified_date})")
        plt.xticks(rotation=45)

        # Create a legend with unique growth stages
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), title="Growth Stages", bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

        # Print the dates and mean water stress values for reference
        #print("Dates, Mean Water Stress Index Values, and Water Demand:")
        for d, ws, wd in zip(time_series_df.index, time_series_df['Mean Water Stress'], time_series_df['Water Demand']):
            #print(f"Date: {d.date()}, Mean Water Stress: {ws:.2f}, Water Demand: {wd:.2f}")
            specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object

            # print('specified date',specified_date_dt, 'date in data:',d.date())
            # print('specified date',specified_date_dt)
            if specified_date_dt == d.date():
                water_demand = wd
                plot.set_present_water_demand(water_demand)

    return plot




