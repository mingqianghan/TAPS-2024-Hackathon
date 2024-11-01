from Water_Demand_live.Source_Code.image_retriever import image_retriever
from Water_Demand_live.Source_Code.create_field_time_series import EXtract_images_create_time_series_for_plots2
import Water_Demand_live.Source_Code.Plot_Water_Stress_Time_Series_V3 as VisulizePlot



def make_water_demand_plot(plot_id, date_input):

    tiff_path = "C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Ceres Imaging Water Stress/WithWaterIndex"
    tiff_images_dates = image_retriever(tiff_path)  #create nested list containing image path and time
    # satilite_dates = {print(item[0]) for item in tiff_images_dates}  # Use a set for faster lookups
    field_time_series = EXtract_images_create_time_series_for_plots2(tiff_images_dates)



    #Plotting water demand of a plot over time, based on the user input
    #plot_id = int(input("Provide plot id or 'q' to quit: "))
    #date_input = str(input("Provide date or 'q' to quit: "))

    plot = VisulizePlot.plot_water_stress_over_time8(field_time_series, plot_id,date_input)
   
    
    return plot
    
