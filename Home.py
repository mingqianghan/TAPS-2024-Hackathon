import io
import base64
import rasterio
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_plotly_events import plotly_events
import os


pro_path = os.getcwd()

# File Paths
shape_file = os.path.join(pro_path, "data", "Plot Boundaries", "Map with all plots", "2024_Colby_TAPS_Harvest_Area.shp")
CWSI_csv_file = os.path.join(pro_path, "data", "Ceres Imaging Water Stress", "stat_summary.csv")
SMC_file = os.path.join(pro_path, "data", "Water_Content", "24 KSU TAPS Neutron Tube Readings_VWC.xlsx")

# Streamlit Dashboard Configuration
st.set_page_config(
    page_title="Smart Irrigation Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)
    
with open("Home_styles.html", "r") as file:
    html_content = file.read()

st.markdown(html_content, unsafe_allow_html=True)


@st.cache_data(show_spinner=True)
def load_large_file(SMC_file, CWSI_csv_file):
    soil_moisture_data = pd.read_excel(SMC_file, skiprows=3, header=None, usecols=[0, 1, 3]);
    water_stress_data = pd.read_csv(CWSI_csv_file)
    
    water_stress_data['Date'] = pd.to_datetime(water_stress_data['Date']).dt.date
    cwsi_dates = water_stress_data['Date'].unique()
    
    
    first_date = water_stress_data['Date'].min()
    first_date_data = water_stress_data[water_stress_data['Date'] == first_date]
    IDs = first_date_data[['Block_ID', 'TRT_ID', 'Plot_ID']]
    
    soil_moisture_data.columns = ['Date', 'Plot_ID', 'SMC']
    soil_moisture_data['Date'] = pd.to_datetime(soil_moisture_data['Date']).dt.date
    smc_dates = soil_moisture_data['Date'].unique()
    

    trt_id_dict = dict(zip(IDs['Plot_ID'], IDs['TRT_ID']))
    block_id_dict = dict(zip(IDs['Plot_ID'], IDs['Block_ID']))

    SMC_data = soil_moisture_data.copy()

    SMC_data['TRT_ID'] = soil_moisture_data['Plot_ID'].map(trt_id_dict)
    SMC_data['Block_ID'] = soil_moisture_data['Plot_ID'].map(block_id_dict)
    
    
    return SMC_data, sorted(smc_dates), water_stress_data, sorted(cwsi_dates), IDs
    
    
def prepare_watchlist_card_data(df, sorted_dates, selected_date, cname, method):
    change_pcts = []
    df_by_plots = []
    
    df_selected_date = df[df['Date'] == selected_date]
    
    if method == 'top':
        # Sort by the main column, then by TRT_ID as a secondary criterion
        data_3 = (
            df_selected_date
            .sort_values([cname, 'TRT_ID'], ascending=[False, True])
            .head(4)[[cname, 'TRT_ID', 'Block_ID']]
        )
    else:
        # Sort by the main column, then by TRT_ID as a secondary criterion
        data_3 = (
            df_selected_date
            .sort_values([cname, 'TRT_ID'], ascending=[True, True])
            .head(4)[[cname, 'TRT_ID', 'Block_ID']]
        )

    values = data_3[cname].tolist()
    trt_ids = data_3['TRT_ID'].tolist()
    block_ids = data_3['Block_ID'].tolist()
    
    
    loc = sorted_dates.index(selected_date)

    if loc == 0 and cname == 'Mean':
        prv_date = sorted_dates[loc]
        for trt_id, block_id in zip(trt_ids, block_ids):
            df_by_plot = df[(df['Date'] == prv_date) &
                             (df['TRT_ID'] == trt_id) & 
                             (df['Block_ID'] == block_id)]
            df_by_plot = df_by_plot[['Date', cname]]
            change_pcts.append([])
            df_by_plots.append(df_by_plot)
    elif (loc == 0 or loc == 1) and cname == 'SMC':
        prv_date = sorted_dates[loc]
        for trt_id, block_id in zip(trt_ids, block_ids):
            df_by_plot = df[(df['Date'] == prv_date)&
                             (df['TRT_ID'] == trt_id) & 
                             (df['Block_ID'] == block_id)]
            df_by_plot = df_by_plot[['Date', cname]]
            change_pcts.append([])
            df_by_plots.append(df_by_plot)
    else:
        prv_dates = sorted_dates[0:loc+1]
        for high_value, trt_id, block_id in zip(values, trt_ids, block_ids):
            
            df_by_plot = df[(df['Date'].isin(prv_dates)) &
                            (df['TRT_ID'] == trt_id) & 
                            (df['Block_ID'] == block_id)]
            df_by_plot = df_by_plot[['Date', cname]]
            
            loc -= 1
            prv_date = sorted_dates[loc]
            
            while True: 
                prv_data = df[(df['Date'] == prv_date) &
                              (df['TRT_ID'] == trt_id) &
                              (df['Block_ID'] == block_id)] 
                # Break the loop if data is found 
                if not prv_data.empty: 
                    break
                
                loc -= 1
                prv_date = sorted_dates[loc]
          
            value = prv_data[cname]
            pct_change = (high_value - value )/ value * 100
            change_pcts.append(pct_change.iloc[0])
            df_by_plots.append(df_by_plot)
    
    return values, trt_ids, block_ids, change_pcts, df_by_plots
    
    
def on_button_click(df_update, df_dates, selected_date, colname):
    if st.session_state.button_label == "🢁 Top Values":
        st.session_state.button_label = "🢃 Lowest Values"
        method = 'top'
    else:
        st.session_state.button_label = "🢁 Top Values"
        method = 'low'
        
    
    values, trt_ids, block_ids, change_pcts, df_by_plots \
        = prepare_watchlist_card_data(df_update, df_dates, selected_date, 
                                      colname, method)
        
    for v1, n1, n2, c, d in zip(values, trt_ids, block_ids, change_pcts, df_by_plots):
        name1 = f"Block {n2} - TRT {n1}"
        d_sorted = d.sort_values(by='Date')
        spark_line_data = d_sorted.iloc[:, -1].tolist()
        
        display_watchlist_card(name1, v1, c, spark_line_data, heat_type)

        
    
def display_metrics(data, datatype):     
    if datatype == 1:
        # low_value = data['Mean'].min(skipna=True)
        # high_value = data['Mean'].max(skipna=True)
        mean_value = data['Mean'].mean(skipna=True)
    
        # low_trt_id = data.loc[data['Mean'].idxmin(skipna=True), 'TRT_ID']
        # low_block_id = data.loc[data['Mean'].idxmin(skipna=True), 'Block_ID']
        
        # high_trt_id = data.loc[data['Mean'].idxmax(skipna=True), 'TRT_ID']
        # high_block_id = data.loc[data['Mean'].idxmax(skipna=True), 'Block_ID']
    
        txtinfo = 'CWSI'
    else:
        # low_value = data['SMC'].min(skipna=True)
        # high_value = data['SMC'].max(skipna=True)
        mean_value = data['SMC'].mean(skipna=True)
    
        # low_trt_id = data.loc[data['SMC'].idxmin(skipna=True), 'TRT_ID']
        #low_block_id = data.loc[data['SMC'].idxmin(skipna=True), 'Block_ID']
        
        # high_trt_id = data.loc[data['SMC'].idxmax(skipna=True), 'TRT_ID']
        # high_block_id = data.loc[data['SMC'].idxmax(skipna=True), 'Block_ID']
    
        txtinfo = 'SMC'

    
    st.html('<span class="bottom_indicator"></span>')
    st.metric(f"Average {txtinfo} Across the Field", f"{mean_value:.2f}")
      

def plot_sparkline(data, data_type):
    if len(data) == 1:
        # If there is only one point, use a marker instead of a line
        fig_spark = go.Figure(
            data=go.Scatter(
                y=data,
                mode="markers",
                marker=dict(color="red", size=8),
            )
        )
    else:
        fig_spark = go.Figure(
            data=go.Scatter(
                y=data,
                mode="lines",
                fill="tozeroy",
                line_color="red",
                fillcolor="pink",
            ),
        )
    fig_spark.update_traces(hovertemplate=f"{data_type}: %{{y:.2f}}")
    fig_spark.update_xaxes(visible=False, fixedrange=True)
    fig_spark.update_yaxes(visible=False, fixedrange=True)
    fig_spark.update_layout(
        showlegend=False,
        plot_bgcolor="#111111",
        height=70,
        margin=dict(t=0, l=0, b=0, r=0, pad=0),
    )
    return fig_spark


def display_watchlist_card(name1, cur_value, change_pct, series_data, datatype): 
    if datatype == 1:
        data_type = 'CWSI'
    else:
        data_type = 'SMC'
        
    with st.container(border=True): 
        st.html('<span class="watchlist_card"></span>')

        tl, tr = st.columns([2, 1])
        bl, br = st.columns([1, 1])

        with tl:
            st.html('<span class="watchlist_symbol_name"></span>')
            st.markdown(f"{name1}")

        with tr:
            if change_pct:
                negative_gradient = float(change_pct) < 0
                st.markdown(
                    f":{'red' if negative_gradient else 'green'}[{'▼' if negative_gradient else '▲'} {change_pct: .3f} %]"
                )
            else:
                st.markdown("➖")
                    

        with bl:
            with st.container():
                st.html('<span class="watchlist_price_label"></span>')
                st.markdown(f"Current {data_type}")

            with st.container():
                st.html('<span class="watchlist_price_value"></span>')
                st.markdown(f"{cur_value:.3f}")
        
        with br:
            fig_spark = plot_sparkline(series_data, data_type)
            st.plotly_chart(
                fig_spark, config=dict(displayModeBar=False), use_container_width=True
            )

    
# Helper function to encode image as Base64
def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode('utf-8')


# Function to generate map with solid white line around RGB GeoTIFF
def make_geo_info_map(bg_file, shape_file, heatmap_values, heat_type = 1, colormap = 'turbo'):
    with rasterio.open(bg_file) as src:
        rgb_image = src.read([1, 2, 3])
        rgb_image = np.moveaxis(rgb_image, 0, -1)
        bounds = src.bounds

    pil_image = Image.fromarray(rgb_image.astype(np.uint8))
    data_uri = image_to_base64(pil_image)

    gdf = gpd.read_file(shape_file).to_crs(epsg=4326)
    gdf = gdf.merge(heatmap_values.drop(['Block_ID', 'TRT_ID'], axis=1), on='Plot_ID', how='left')

    minx, miny, maxx, maxy = gdf.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    fig = go.Figure()

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",  # Use 'open-street-map' for better visibility and readability
            layers=[
                {
                    "sourcetype": "raster",
                    "source": [
                        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    ],
                    "below": "traces",  # Ensure satellite map is below all traces
                },
                {
                    "sourcetype": "image",
                    "source": data_uri,
                    "coordinates": [
                        [bounds.left, bounds.top],
                        [bounds.right, bounds.top],
                        [bounds.right, bounds.bottom],
                        [bounds.left, bounds.bottom],
                    ],
                    "below": "traces",  # Ensure RGB image is below traces
                },
            ],
            center=dict(lat=center_lat, lon=center_lon),
            zoom=17,
        ),
        uirevision='constant', # Keeps the zoom level and selection persistent
        margin=dict(r=0, l=0, t=0, b=0),
        autosize=True,
        height=790,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot background
    )

    fig.add_trace(go.Scattermapbox(
        lon=[bounds.left, bounds.right, bounds.right, bounds.left, bounds.left],
        lat=[bounds.top, bounds.top, bounds.bottom, bounds.bottom, bounds.top],
        mode='lines',
        line=dict(color='white', width=2),
        hoverinfo='skip',
    ))

    if heat_type == 1: 
        ctitle = 'CWSI'
        cmin = 0
        cmax = 1
    else: 
        ctitle = 'SMC'
        cmin = 0.1
        cmax = 0.4
          
    cmap = plt.get_cmap(colormap)

    def get_color(value, cmin, cmax):
        
        norm_value = (value - cmin) / (cmax - cmin)
        norm_value = np.clip(norm_value, 0, 1)
        rgba = cmap(norm_value)
        return f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3]})'

    # List to store metadata for each polygon and track their trace indices
    metadata_list = []
    polygon_trace_indices = []

    for _, row in gdf.iterrows():
        if row['geometry'].geom_type == 'Polygon':
            lon, lat = row['geometry'].exterior.xy
            block_id = row.get('Block_ID', 'N/A')
            trt_id = row.get('TRT_ID', 'N/A')
            plot_id = row.get('Plot_ID', 'N/A')
            
            if heat_type == 1:
                mean_heat_value = row.get('Mean', np.nan)
                min_heat_value = row.get('Min', np.nan)
                max_heat_value = row.get('Max', np.nan)
                color = get_color(mean_heat_value, cmin, cmax) if not np.isnan(mean_heat_value) else 'gray'
              

                fig.add_trace(go.Scattermapbox(
                    lon=list(lon), lat=list(lat),
                    fill="toself",
                    mode="lines",
                    line=dict(color='black', width=2),
                    fillcolor=color,
                    hoverinfo="text",
                    text=(
                        f"Block ID: {block_id}<br>"
                        f"TRT ID: {trt_id}<br>"
                        f"Mean: {mean_heat_value:.2f}<br>"
                        f"Min: {min_heat_value:.2f}<br>"
                        f"Max: {max_heat_value:.2f}"
                        ),
                    ))
            else:
                smc = row.get('SMC', np.nan)
                color = get_color(smc, cmin, cmax) if not np.isnan(smc) else 'gray'

                fig.add_trace(go.Scattermapbox(
                    lon=list(lon), lat=list(lat),
                    fill="toself",
                    mode="lines",
                    line=dict(color='black', width=2),
                    fillcolor=color,
                    hoverinfo="text",
                    text=(
                        f"Block ID: {block_id}<br>"
                        f"TRT ID: {trt_id}<br>"
                        f"SMC: {smc:.2f}"
                    ),
                ))
            
            trace_index = len(fig.data)  # Index of the current trace before adding it
            polygon_trace_indices.append(trace_index)

            # Append metadata for this trace
            metadata_list.append({"plot_id": plot_id})
        

    # Add a dummy marker trace to generate the colorbar
    fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=[None], lat=[None],
        marker=dict(
            size=0,
            color=[cmin, cmax],  # Set to the min and max values of 'Mean' for a meaningful color scale
            colorscale = colormap,  # Use the same colormap used in the map polygons
            colorbar=dict(
                title=ctitle,
                titleside="top",
                lenmode='pixels',
                len=260,
                thickness=18,
                x=0.9,
                y=0.8,
                yanchor='middle',
                outlinewidth=1,
                outlinecolor='#111111',
                bgcolor='rgba(0, 0, 0, 0)',   
                tickcolor='#111111',  # Make tick color visible
                titlefont=dict(
                    color='#fafafa',  # Color of the title for visibility
                    size=12
                ),
                tickfont=dict(
                    color='#fafafa',  # Color of the title for visibility
                    size=12
                ),
            ),
        ),
        showlegend=False
    ))


    selected_points = plotly_events(fig)
    
    # Handle selected points logic as before
    if selected_points:
        selected_point = selected_points[0]
        curve_number = selected_point['curveNumber']
    
        if curve_number in polygon_trace_indices:
            print(curve_number)
            polygon_index = polygon_trace_indices.index(curve_number) + 1
            plot_id = metadata_list[polygon_index]["plot_id"]
            
            st.session_state["plot_id"] = plot_id
            st.session_state["date"] = selected_date
            
            st.switch_page(r"pages\Crop Water Status.py")


if 'button_label' not in st.session_state:
     st.session_state.button_label = "🢁 Top Values"
     
with st.sidebar:
    data_type = ["Soil Moisture Content (SMC)", "Crop Water Stress Index (CWSI)"]
    selected_data = st.selectbox('Select Data Type', data_type, index=len(data_type) - 1)
    
    SMC_data, smc_dates, CWSI_data, cwsi_dates, IDs = load_large_file(SMC_file, CWSI_csv_file)
    IDs.to_excel('data.xlsx', index=False)
    
    
    if selected_data == data_type[1]:
        selected_date = st.selectbox('Select Date', cwsi_dates, index=len(cwsi_dates) - 1)
        df_selected_date = CWSI_data[CWSI_data['Date'] == selected_date]
    
        df_update = CWSI_data
        df_dates = cwsi_dates
        colname = 'Mean'
        bg_date = selected_date
        heat_type = 1;
        colormap = 'turbo'

    else:
        selected_date = st.selectbox('Select Date', smc_dates, index=len(smc_dates) - 1)
        df_selected_date = SMC_data[SMC_data['Date'] == selected_date]
        
        df_update = SMC_data
        df_dates = smc_dates
        colname = 'SMC'
    
        bg_date = min(cwsi_dates, key=lambda x: abs(x - selected_date))
        heat_type = 0
        colormap = 'Blues'

     
    with st.expander('About', expanded=True):
        st.write('''
           - Data  Source: [Testing Ag Performance Solutions (TAPS)](https://www.k-state.edu/taps/).
           - Location: [Colby, KS](https://www.google.com/maps/dir/Colby,+Kansas+67701//@39.3958296,-101.0935768,13z/data=!4m8!4m7!1m5!1m1!1s0x870acbe7f4a97a1f:0xba77014e4963936!2m2!1d-101.0523773!2d39.3958369!1m0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D) 
           - :orange[**CWSI**]: Provided by Ceres Imaging. Higher values reflect increased crop stress.
           - :orange[**SMC**]: Collected using neutron probes. Lower values indicate drier soil.
           ''')
                 

bg_file = os.path.join(pro_path, "data", "Ceres Imaging Water Stress", "RGB", f"{bg_date}_RGB.tif")


left_geo_chart, right_info = st.columns([3.5, 1.5])

with left_geo_chart:
    st.html('<span class="column_plotly"></span>')
    make_geo_info_map(bg_file, shape_file, df_selected_date, heat_type, colormap = colormap)
    
with right_info:
    st.markdown('<div class="top-block"> </div>', unsafe_allow_html=True)
    display_metrics(df_selected_date, heat_type)

    st.button(st.session_state.button_label, on_click=on_button_click(df_update, df_dates, selected_date, colname))
