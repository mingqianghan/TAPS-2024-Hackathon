import rasterio
import numpy as np
import geopandas as gpd
from rasterio.plot import show
import matplotlib.pyplot as plt
from shapely.geometry import box

# Function to extract water stress index using bounding boxes
def extract_index(image_path, bbox_df):
    with rasterio.open(image_path) as src:
        # Initialize a list to store water stress index values for each plot
        water_index_values = []
        mean_water_index = []

        # #Plot the GeoTIFF image
        # fig, ax = plt.subplots(figsize=(10, 10))
        # show(src,title="Water Stress Index with Plot Boundaries",cmap='turbo')

        # Overlay bounding boxes on the image and extract values
        for _, row in bbox_df.iterrows():
            # Use the coordinates for plotting
            top_left_x, top_left_y = row['top_left_x'], row['top_left_y']
            bottom_right_x, bottom_right_y = row['bottom_right_x'], row['bottom_right_y']
            
            #Create a bounding box polygon
            bbox = box(top_left_x, bottom_right_y, bottom_right_x, top_left_y)
            
            # #Plot the bounding box
            # plot_bbox = gpd.GeoSeries([bbox], crs=src.crs)  # Use the same CRS as the shapefile
            # plot_bbox.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=1.5)

            # # Extract the indices of the bounding box in the raster
            window = src.window(top_left_x, bottom_right_y, bottom_right_x, top_left_y)

            # Read the data from the specified window
            data = src.read(1, window=window)  # Assuming the water stress index is in the first band
            
            # Mask the data to get only the values within the bounding box
            masked_data = np.where(data > 0, data, np.nan)  # Replace out-of-bound values with NaN
            # Mask out any nodata values or other unwanted data

            #Calculate mean water index or other statistics (you can modify this as needed)
           # Calculate mean water index or other statistics (you can modify this as needed)
            if masked_data.size > 0:
                water_index = np.nanmean(masked_data)  # Use nanmean to ignore NaN values
            else:
                water_index = np.nan  # Handle the case where no valid data is found

            # Append the value to the list
            water_index_values.append(masked_data)
            mean_water_index.append(water_index)


        # print(water_index_values)
        
        # Store the extracted values in the bbox_df DataFrame
        bbox_df['plot_water_index'] =water_index_values
        bbox_df['Mean_Water_Stress'] = mean_water_index
    return bbox_df

# Example usage
# bbox_df = ...  # Your bounding box DataFrame
# image_path = "path/to/your/geotiff.tif"
# updated_bbox_df = extract_water_stress_index(image_path, bbox_df)

# Print the updated DataFrame
# print(updated_bbox_df[['plot_id', 'plot_water_index']])
