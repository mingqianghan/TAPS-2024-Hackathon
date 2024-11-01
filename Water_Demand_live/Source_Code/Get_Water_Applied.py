import pandas as pd

def get_irrigation_data(treatment_id, start_date, end_date, file_path):
    # Load the DataFrame
    irrigation_supplied = pd.read_excel(file_path, 
                                         sheet_name='Irrigation amounts', 
                                         header=1)

    # Convert the column names (excluding the ID column) to datetime, handling errors for non-date columns
    converted_columns = []
    for col in irrigation_supplied.columns:
        try:
            converted_columns.append(pd.to_datetime(col))
        except ValueError:
            converted_columns.append(col)  # Keep the non-date column as is (e.g., 'Total')

    # Update the DataFrame's columns
    irrigation_supplied.columns = converted_columns

    # Locate the row(s) with the specified treatment ID
    located_row = irrigation_supplied[irrigation_supplied['ID'] == treatment_id]

    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Select columns that fall within the specified date range
    time_series_columns = irrigation_supplied.columns[1:]  # Exclude the ID column
    selected_columns = [col for col in time_series_columns if isinstance(col, pd.Timestamp) and start_date <= col <= end_date]

    # Create a time series DataFrame with the index set to dates and a column for water applied
    segmented_data = located_row[selected_columns].transpose()  # Transpose to have dates as index
    segmented_data.columns = ['Irrigation Applied']  # Rename the column to 'Irrigation Applied'

    # Generate a complete date range from start_date to end_date
    full_date_range = pd.date_range(start=start_date, end=end_date)

    # Reindex the segmented data to this full date range, filling missing dates with 0
    segmented_data = segmented_data.reindex(full_date_range, fill_value=0)
    segmented_data.index.name = 'Date'

    # Locate the "Total" column for the specified treatment ID
    if 'Total' in irrigation_supplied.columns:
        total_irrigation = irrigation_supplied.loc[irrigation_supplied['ID'] == treatment_id, 'Total'].values[0]
    else:
        total_irrigation = None  # Handle case if "Total" column does not exist

    return total_irrigation, segmented_data

# Example of how to call the function
# treatment_id = 1
# start_date = '2024-07-10'
# end_date = '2024-10-30'
# file_path = 'Water Demand/Data_Required/Management_Data/2024_TAPS_management.xlsx'

# total_irrigation, time_series_data = get_irrigation_data_V2(treatment_id, start_date, end_date, file_path)

import pandas as pd

def read_precipitation_series(file_path, start_date=None, end_date=None):
    # Load the DataFrame and parse the 'TIMESTAMP' column as dates
    weather_timeseries = pd.read_csv(file_path, parse_dates=['TIMESTAMP'])

    # Set TIMESTAMP as index and handle NaN values in PRECIP by replacing them with 0
    weather_timeseries.set_index('TIMESTAMP', inplace=True)
    weather_timeseries['PRECIP'].fillna(0, inplace=True)
    
    # Convert start and end dates to datetime, if provided
    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)

    # Get the closest available date for start and end if they are not present in the index
    if start_date and start_date not in weather_timeseries.index:
        start_date = weather_timeseries.index[weather_timeseries.index.get_loc(start_date, method='nearest')]
    if end_date and end_date not in weather_timeseries.index:
        end_date = weather_timeseries.index[weather_timeseries.index.get_loc(end_date, method='nearest')]

    # Filter the DataFrame to the specified date range
    if start_date and end_date:
        precipitation_time_series = weather_timeseries.loc[start_date:end_date, ['PRECIP']]
    elif start_date:
        precipitation_time_series = weather_timeseries.loc[start_date:, ['PRECIP']]
    elif end_date:
        precipitation_time_series = weather_timeseries.loc[:end_date, ['PRECIP']]
    else:
        precipitation_time_series = weather_timeseries[['PRECIP']]
    
    # Rename column to 'Precipitation' for clarity
    precipitation_time_series.columns = ['Precipitation']

    return precipitation_time_series

# Example of how to call the function
# file_path = 'Water Demand/Data_Required/Weather_Data/colby_station_kansas_mesonet.csv'
# start_date = '2024-04-01'
# end_date = '2024-10-15'
# precipitation_data = read_precipitation_series(file_path, start_date=start_date, end_date=end_date)
# print(precipitation_data)

def find_Total_Water_Applied_Per_Date(precipe_Time_Series,irrigation_time_series_data):
    combined_series = pd.concat([precipe_Time_Series, irrigation_time_series_data], axis=1, join='outer')
    # Sum the precipitation data, filling NaN values with 0
    combined_series['Total Water Applied'] = combined_series.sum(axis=1, skipna=True)
    # combined_series.info()

    return combined_series