import geopandas as gpd
import pandas as pd
from Water_Demand_live.Source_Code.extract_Water_Stress_index import extract_index
from pyproj import Transformer

def EXtract_images_create_time_series_for_plots2(tiff_images_dates):
    # Load planting and growth stage dates
    
    planting_dates_growth_dates = pd.read_excel("C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Management_Data/Planting_Times_and_Growth_Dates.xlsx")
    shape_file_path = "C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024/data/Plot Boundaries/Map with all plots/2024_Colby_TAPS_Harvest_Area.shp"

    # Initialize a transformer for converting to UTM Zone 14N (EPSG:32614)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True)
    
    field_time_series = []
    for i in tiff_images_dates:
        patha = i[1]
        
        # Load the shapefile for the plots
        plot = gpd.read_file(shape_file_path)
        
        # Extract bounding boxes for each plot
        bounding_boxes = plot['geometry'].apply(lambda geom: geom.bounds)
        bbox_df = pd.DataFrame(bounding_boxes.tolist(), columns=['minx', 'miny', 'maxx', 'maxy'])

        bbox_df_area = bbox_df

        # # Apply the coordinate transformation to each bounding box corner
        # bbox_df_area[['top_left_x', 'top_left_y']] = bbox_df_area[['minx', 'maxy']].apply(
        #     lambda row: transformer.transform(row['minx'], row['maxy']), axis=1, result_type='expand'
        # )
        # bbox_df_area[['bottom_right_x', 'bottom_right_y']] = bbox_df[['maxx', 'miny']].apply(
        #     lambda row: transformer.transform(row['maxx'], row['miny']), axis=1, result_type='expand'
        # )
        
        # Add top-left and bottom-right coordinates
        bbox_df['top_left_y'] = bbox_df['maxy'].round(7)
        bbox_df['top_left_x'] = bbox_df['minx'].round(7)
        bbox_df['bottom_right_y'] = bbox_df['miny'].round(7)
        bbox_df['bottom_right_x'] = bbox_df['maxx'].round(7)

        # Optionally add a plot identifier and TRT column for merging
        bbox_df['Plot #'] = plot['Plot_ID']
        bbox_df['TRT'] = plot['TRT_ID']
        bbox_df['Block_ID'] = plot['Block_ID']

        # Calculate accurate area based on the original geometry after reprojecting coordinates
        plot['Area'] = plot.to_crs("EPSG:32614")['geometry'].area  # Area in square meters
        bbox_df['Area'] = plot['Area'].values

        # Select relevant columns
        bbox_df = bbox_df[['top_left_y', 'top_left_x', 'bottom_right_y', 'bottom_right_x', 'Plot #', 'TRT', 'Block_ID', 'Area']]

        # Merge planting and growth stage dates with bbox_df based on Field id/TRT
        bbox_df = bbox_df.merge(
            planting_dates_growth_dates[['Field id', 'Planting', 'V9', 'V12', 'VT/R1', 'R2']],
            left_on='TRT', 
            right_on='Field id', 
            how='left'
        ).drop(columns=['Field id'])

        # Extract the water stress index for the plots based on updated bounding boxes
        plots_df = extract_index(patha, bbox_df)
        
        # Append the resulting data to the list, including the date and plots data
        i.append(plots_df)
        
        field_time_series.append(i)

    return field_time_series
