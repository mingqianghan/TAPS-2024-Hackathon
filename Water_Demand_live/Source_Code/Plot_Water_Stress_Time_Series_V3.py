import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from Water_Demand_live.Source_Code.Plot_Class_V2 import DefinePlot
from Water_Demand_live.Source_Code.align_water_series import align_water_series
from Water_Demand_live.Source_Code.smooth_and_gap_fill import smooth_and_gap_fill
from Water_Demand_live.Source_Code.water_content_time_series import water_content_time_series
from Water_Demand_live.Source_Code.Get_Water_Applied import get_irrigation_data
from Water_Demand_live.Source_Code.make_plot_figures import make_Plot_figures
from Water_Demand_live.Source_Code.Get_Water_Applied import read_precipitation_series
from Water_Demand_live.Source_Code.Get_Water_Applied import find_Total_Water_Applied_Per_Date
# from Water_Demand_live.Source_Code.Make_Recomendation import makeRecomendation






def plot_water_stress_over_time8(field_time_series, plot_index, specified_date, num_cols=3, smoothing_window=5):
    """
    Plots water stress index maps for a specified plot over time and a time series plot of the mean water stress index.

    Parameters:
    - field_time_series: List of data entries, where each entry contains a date and plot data.
    - plot_index: Integer index of the plot to analyze (e.g., 0, 1, 2, etc.).
    - specified_date: Date until which to plot the data, must be within the time series.
    - smoothing_window: Size of the moving average window.
    """

    # Load reference evapotranspiration data
    reference_et_df = pd.read_excel('C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Weather_Data/ref_evapotranspiration.xlsx')
    reference_et_df['Date'] = pd.to_datetime(reference_et_df['Date']).dt.date
    irrigation_File_Path = 'C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Management_Data/2024_TAPS_management.xlsx'


    weather_path = 'C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Weather_Data/colby_station_kansas_mesonet.csv'
    # Handling specified_date format


    if specified_date:
        if isinstance(specified_date, str):
            specified_date = pd.to_datetime(specified_date).date()
        elif isinstance(specified_date, pd.Timestamp):
            specified_date = specified_date.date()
    
    # Define kc values and colors for maize growth stages
    kc_values = {'Planting': 0.3, 'V9': 0.7, 'V12': 1.2, 'VT/R1': 1.4, 'R2': 1.2}
    
    
    dates, water_stress_means, water_demands, growth_stage_dates, growth_stage_labels = [], [], [], [], []

    
    # Planting date variable
    planting_date = None

    # Iterate through each date in `field_time_series`
    for i, date_entry in enumerate(field_time_series):
        date = pd.to_datetime(date_entry[0]).date()
        plots_data = date_entry[2]

        # Get data for the specified plot on this date
        plot_data = plots_data.loc[plots_data['Plot #'] == plot_index].squeeze()

        if not plot_data.empty:
            plot = DefinePlot(plot_data, specified_date)
            water_stress_plot = plot.get_water_stress()
            mean_water_stress = plot.get_mean_water_stress()
            plot_area = plot.get_plot_area()
            block_id = plot.get_block_id()
            dates.append(date)
            water_stress_means.append(mean_water_stress)

            if planting_date is None:
                planting_date = pd.to_datetime(plot.get_planting_date()).date()

            # Determine growth stage
            days_since_planting = (date - planting_date).days
            current_growth_stage = 'Planting'
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
                growth_stage_dates.append(date)
                growth_stage_labels.append(current_growth_stage)


        
        

            et_row = reference_et_df[reference_et_df['Date'] == date]
            reference_et = et_row['refET'].values[0] if not et_row.empty else 0
            kc = kc_values.get(current_growth_stage, 0)
            water_demand = kc * reference_et * mean_water_stress
            water_demands.append(water_demand)

    # Prepare time series data
    if dates:
        time_series_df = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Mean Water Stress': water_stress_means,
            'Water Demand': water_demands
        })
        time_series_df.set_index('Date', inplace=True)
        time_series_df = time_series_df.reindex(pd.date_range(start=time_series_df.index.min(), end=time_series_df.index.max()))
        time_series_df.interpolate(method='time', inplace=True)
        time_series_df['Mean Water Stress'] = time_series_df['Mean Water Stress'].rolling(window=smoothing_window, min_periods=1).mean()
        time_series_df['Water Demand'] = time_series_df['Water Demand'].rolling(window=smoothing_window, min_periods=1).mean()

        water_demand = pd.DataFrame(time_series_df['Water Demand'])

        # Estimate water demand of the field over time in cubic mm
        start_date = planting_date
        end_date = specified_date
        treatment_id = plot.get_TreatmentID()
        Total_irrigation, irrigation_timeSeries = get_irrigation_data(treatment_id, start_date, end_date, irrigation_File_Path) # get irrigation data

        Precipitation = read_precipitation_series(weather_path,start_date= start_date,end_date=end_date)

        Total_Water_Applied = find_Total_Water_Applied_Per_Date(Precipitation,irrigation_timeSeries)

        # print(irrigation_timeSeries.info())


        # Set total irrigation for a plot
        
        Total_irrigation = round(np.sum(Total_Water_Applied['Irrigation Applied']),2) # find total irrigationfor the period
        Total_irrigation = Total_irrigation * 0.0254 #total irrigationin meters
        Plot_Area = round(plot.get_plot_area(),2) #plot area in square meter
        Total_irrigation = Total_irrigation * Plot_Area # Total irrigation in cubic meters
        Total_irrigation = round(Total_irrigation * 1000) # Total irrigation for the specified period in liters
        

        #print(Total_irrigation)
        
        plot.set_Total_irrigation(Total_irrigation)
        print(plot.get_Total_irrigation())
        water_content = align_water_series(water_demand, smooth_and_gap_fill(water_content_time_series(), plot_index) * 6)
        time_series_df = time_series_df[planting_date:specified_date]
        water_content = water_content[planting_date:specified_date]

        Water_Required =  water_content['Water Content'] - time_series_df['Water Demand']
        Water_Required = pd.DataFrame(Water_Required,columns=['Water Required'])
        

        # Create interactive plotly plot

        #Please note time_series_df is the water demand for the entire period
        #water_demand water demand is the water demand for the specified period

        
        fig= make_Plot_figures(Water_Required=Water_Required,
                                      specified_date = specified_date,
                                      time_series_df = time_series_df,
                                      Total_Applied_Water=Total_Water_Applied,plot= plot,
                                      planting_date= planting_date,
                                      Precipitation_Water_Applied= Precipitation,
                                      Irrigation_Water_Applied= irrigation_timeSeries)

        
        # print(Water_Required.info())
        
        #fill plot attibute for current water required

        for d , wr in zip(Water_Required.index,Water_Required['Water Required']):
            specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object
            # print(wr)
            # print(d.date)

            if specified_date_dt == d.date():

                if wr >0:
                    wr = round(wr,2)
                    # print(wr)
                    plot.set_waterRequired(0)

                if wr <0:
                    wr = -1*round(wr,2)
                    # print(wr)
                    plot.set_waterRequired(wr)


        #fill plot attribute prese water demand

        for d , wd in zip(time_series_df.index,time_series_df['Water Demand']):
            specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object
            # print(wr)
            # print(d.date)

            if specified_date_dt == d.date():
                wd = round(wd,2)
                # print(wr)
                plot.set_present_water_demand(wd)

        #fill plot attribute for present water content
        
        for d , wc in zip(water_content.index,water_content['Water Content']):
            specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object
            # print(wr)
            # print(d.date)

            if specified_date_dt == d.date():
                wc = round(wc,2)
                # print(wr)
                plot.setPresentWaterContent(wc)


        #fill plot attribute for current total water applied

        for d , tw , water_applied_irrigation, water_applied_precipitation in zip(Total_Water_Applied.index,
                            Total_Water_Applied['Total Water Applied'],
                            Total_Water_Applied['Irrigation Applied'],
                            Total_Water_Applied['Precipitation']):
            
            specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object
            # print(tw)
            # print(d.date)

            if specified_date_dt == d.date():
                print(tw)
                tw = round(tw,2) # total Water
                water_applied_irrigation = round(water_applied_irrigation,2)
                water_applied_precipitation = round(water_applied_precipitation,2)
                # print(wr)
                plot.setTotal_CurrentApplied_Water(tw)
                plot.setPrecipitationApplied(water_applied_precipitation)
                plot.setIrrigationApplied(water_applied_irrigation)
                
                




        

                
        # for d, ws, wd,wr,wc in zip(time_series_df.index, time_series_df['Mean Water Stress'], time_series_df['Water Demand'],Water_Required['Water Required'],water_content):
        #     #print(f"Date: {d.date()}, Mean Water Stress: {ws:.2f}, Water Demand: {wd:.2f}")
        #     specified_date_dt = pd.to_datetime(specified_date).date()  # Convert to date object
        #     # print(specified_date_dt)
        #     # print(d.date())

        #     print(wr)

        #     # print('specified date',specified_date_dt, 'date in data:',d.date())
        #     # print('specified date',specified_date_dt)
        #     if specified_date_dt == d.date():
        #         print(wr)
        #         plot.set_present_water_demand(wd)
        #         plot.set_waterRequired(wr)
        #         plot.set_water_content(wc)


        # recomendation = makeRecomendation(plot) #make a recomendation statement to the farmer

        plot.set_plot_graph(fig)  # Save plotly figure in plot object
        # plot.setRecomendationStatment(recomendation)
        # fig.show()

    return plot