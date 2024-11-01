def water_content_time_series():
    import pandas as pd

    # Load water content data
    water_content = pd.read_excel("C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Water_Content/24 KSU TAPS Neutron Tube Readings_VWC.xlsx", header=2)
    water_content = water_content.iloc[:, :4]  # Keep only the first four columns

    # Convert 'Date' column to datetime if it's not already
    water_content['Date'] = pd.to_datetime(water_content['Date'])

    # Initialize a nested list to store [date as string, data_frame]
    date_dataframes = []  # List to hold [date, data_frame] pairs

    # Loop over each unique date and create separate DataFrames
    for date in water_content['Date'].unique():
        date_str = date.strftime('%Y-%m-%d')  # Extract date as a string in YYYY-MM-DD format
        date_df = water_content[water_content['Date'] == date].reset_index(drop=True)  # Filter rows with the same date
        date_dataframes.append([date_str, date_df])  # Append [date as string, data_frame] to the list

    # Optionally print the nested list to check the result
    # for idx, (date_str, df) in enumerate(date_dataframes):
    #     print(f"Entry {idx + 1}: Date: {date_str}")
    #     print(df)
    #     print()  # For spacing

    return date_dataframes  # Return the nested list of [date as string, data_frame]


