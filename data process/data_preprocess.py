"""
Created on Fri Oct 25 23:14:08 2024

@author: mingqiang
"""
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from rasterio.plot import show
from rasterio.mask import mask
import rasterio
import os
import re


def save_index_values_as_geotiff(input_path, output_path, colormap ='turbo', showplots = True):
    """
    Save index values extracted from an RGB image to a GeoTIFF with geospatial metadata.

    Parameters:
    input_path (str): Path to the Water Stress raster file (GeoTIFF) containing RGB bands.
    output_path (str): Path to save the output GeoTIFF with index values.
    colormap (str): Colormap name to use (default is 'turbo').
    """
    # Load the RGB bands and metadata from the original raster
    with rasterio.open(input_path) as src:
        red = src.read(1).astype(np.float32) / 255
        green = src.read(2).astype(np.float32) / 255
        blue = src.read(3).astype(np.float32) / 255
        meta = src.meta  # Get all metadata

    # Stack RGB channels into a single (H x W x 3) array and reshape for KDTree
    rgb = np.stack([red, green, blue], axis=-1).reshape(-1, 3)

    # Create the colormap and extract RGB values for 256 levels
    cmap = plt.get_cmap(colormap, 256)
    colors = cmap(np.linspace(0, 1, 256))[:, :3]  # RGB values (Nx3)
    index_range = np.linspace(0, 1, 256)  # Range of index values

    # Use KDTree for efficient color matching
    tree = KDTree(colors)
    _, idx = tree.query(rgb)

    # Convert the matched indices to corresponding values in the index range
    index_values = index_range[idx].reshape(red.shape)

    # Update metadata for the single-band GeoTIFF output
    meta.update(
        dtype=rasterio.float32,  # Set datatype to float32
        count=1,  # Single-band output
        compress='lzw'  # Optional compression for efficient storage
    )

    # Save the index values with the original geospatial information
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(index_values.astype(rasterio.float32), 1)

    if showplots:
        # Display the original RGB image and the colorized index values
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.imshow(np.stack([red, green, blue], axis=-1))
        plt.title("Original RGB Image")
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(index_values, cmap=colormap)
        plt.colorbar(label='Index Value')
        plt.title("Colorized Index Values")
        plt.axis('off')

        plt.show()
        

def project_plot_boundary(image_path, shape_path, segmented_figure_path,
                          colormap ='turbo', savesegmentedplots = True): 
    
    with rasterio.open(image_path) as src: 
        image = src.read(1)
        image_crs = src.crs
        transform = src.transform
        profile = src.profile

    # Load and Reproject the Shapefile 
    gdf = gpd.read_file(shape_path)
    if gdf.crs != image_crs:
        gdf = gdf.to_crs(image_crs)
        
    
    # Plot the NDVI Image with Matplotlib
    fig, ax = plt.subplots(figsize=(8, 8))
    show(image, ax=ax, transform=transform, cmap=colormap, vmin=0, vmax=1)

    statistics = []
    
    for idx, row in gdf.iterrows():
        centroid = row['geometry'].centroid  # Get the centroid of each plot
        block_id = row.get('Block_ID', 'N/A')  
        trt_id = row.get('TRT_ID', 'N/A')
        plot_id = row.get('Plot_ID', 'N/A')
        
        
        # Create a mask and extract the corresponding image region
        masked_image, masked_transform = mask(
            dataset=rasterio.open(image_path), 
            shapes=[row['geometry']], 
            crop=True, 
            filled=True, 
            pad=True, 
            pad_width=1,
            nodata=np.nan
        )
        
        if savesegmentedplots:
            # Create an output directory if it doesn't exist
            os.makedirs(segmented_figure_path, exist_ok=True)
            # Save the segmented image to a file
            output_path = os.path.join(segmented_figure_path, f'plot_{block_id}_{trt_id}.tif')
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(masked_image)

        
        # Replace zero values with NaN only in padding areas
        masked_image = np.where(masked_image == 0, np.nan, masked_image)
        
        # print(f"B:{block_id} T:{trt_id}:")
        # print(masked_image)
        
        # Calculate descriptive statistics, ignoring NaN values
        mean_value = np.nanmean(masked_image)
        max_value = np.nanmax(masked_image)
        min_value = np.nanmin(masked_image)
        std_dev = np.nanstd(masked_image)
        
        # Calculate quartiles
        quartiles = np.nanpercentile(masked_image, [25, 50, 75, 100])
        q1, q2, q3, q4 = quartiles  # Q1 = 25th, Q2 = 50th (median), Q3 = 75th, Q4 = max
        
        
        # Store statistics
        statistics.append({
            'Block_ID': block_id,
            'TRT_ID': trt_id,
            'Plot_ID': plot_id,
            'Mean': mean_value,
            'Std Dev': std_dev,
            'Min': min_value,
            'Max': max_value,
            'Q1 (25%)': q1,
            'Q2 (50%)': q2,
            'Q3 (75%)': q3,
            'Q4 (100%)': q4
        })
        
    
        # Annotate with Block ID and Treatment ID
        ax.text(centroid.x, centroid.y, f"B:{block_id}\nT:{trt_id}",
                ha='center', va='center', fontsize=7, color='black')

    # Plot the shapefile boundaries
    gdf.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1)
    
    # Display the plot
    plt.axis('off')
    plt.show()
    
    # Return statistics as a DataFrame for easy analysis
    return pd.DataFrame(statistics)
        



input_folder_path = "../data/Ceres Imaging Water Stress/Original"
output_folder_path = "../data/Ceres Imaging Water Stress/WithWaterIndex"
shape_path = "../data/Plot Boundaries/Map with all plots/2024_Colby_TAPS_Harvest_Area.shp"
segmented_figure_path = "../data/Ceres Imaging Water Stress/segmented"
stat_file = "../data/Ceres Imaging Water Stress/stat_summary.csv"

# Define the regex pattern for the file name (e.g., 2024-07-29_Water Stress.tif)
pattern = re.compile(r"\d{4}-\d{2}-\d{2}_Water Stress\.tif$")

# List all files in the specified folder
matching_files = [f for f in os.listdir(input_folder_path) if pattern.match(f)]

'''
# Loop over matching files and covert to image with water stress index
for filename in matching_files:
    original_file = os.path.join(input_folder_path, filename)
    output_file = os.path.join(output_folder_path, filename)
    save_index_values_as_geotiff(original_file, output_file, showplots = True)
'''

 
# Loop over matching files and append data to the output file
for filename in matching_files:
    index_image_path = os.path.join(output_folder_path, filename)

    # Extract date from the filename
    segments = filename.split('_')
    date = segments[0]

    # Construct the segmented file path
    segmented_file_path = os.path.join(segmented_figure_path, segments[0])

    # Generate the stat DataFrame
    stat = project_plot_boundary(index_image_path, shape_path, segmented_file_path, 
                                 colormap='turbo', savesegmentedplots=False)

    '''
    # Insert 'Date' column at the first position
    stat.insert(0, 'Date', date)

    # Check if the output file exists and write header only if it does not
    write_header = not os.path.exists(stat_file)

    # Append the DataFrame to the CSV file
    stat.to_csv(stat_file, mode='a', index=False, header=write_header)

    print(f"Appended data from {filename} to {stat_file}")
    '''
