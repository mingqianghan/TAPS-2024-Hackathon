# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 16:26:33 2024

@author: mingqiang
"""
import streamlit as st
from Water_Demand_live.Source_Code.Water_Demand import make_water_demand_plot
from Water_Demand_live.Source_Code.Make_Recomendation import makeRecomendation

from streamlit_calendar import calendar

def get_irrigation_info(required_water):
    if required_water is not None:
        if required_water == 0:
            symbol = '🌱'
            metric_value = f"{symbol} {required_water:.2f}″"
            return metric_value, 'optimal', 'optimal'
        else:
            symbol = '🔥'
            metric_value = f"{symbol} {required_water:.2f}″"
            return metric_value, 'deficit', 'deficit'
    else:
        return '➖', 'deficit', '➖'

with open("water_demand_style.html", "r") as file:
    page2_html_content = file.read()
st.markdown(page2_html_content, unsafe_allow_html=True)

with open("calender_styles.css", "r") as f:
    calendar_css = f.read()
    

plot_id = st.session_state.get("plot_id", 804)

with st.sidebar:
    selected_calender = calendar(custom_css=calendar_css)
    with st.container(border=True): 
        st.markdown('Dates with Available Data')
        st.markdown('05/01/2024 - 08/30/2024')


if selected_calender.get('callback') == 'dateClick':
    selected_date = selected_calender['dateClick']['date']
else:
    selected_date =  st.session_state.get("date", "2024-08-30")


try:
    plt = make_water_demand_plot(plot_id, selected_date)
    
    block_id = plt.get_block_id()
    trt_id = plt.get_TreatmentID()

    title_text = f"Block {block_id} - TRT {trt_id}"
    st.markdown(f"<h3 style='text-align: center;'>Crop Water Status: {title_text}</h3>", 
                unsafe_allow_html=True)


    column = st.columns([2.8, 1.2])
    water_plt = plt.get_plot_graph()

    with column[0]:
        st.html('<span class="column_plotly"></span>')
        st.plotly_chart(water_plt, use_container_width=True)
        

    with column[1]:
        cur_water_demand = plt.get_waterRequired()
        prep = plt.getPrecipitationApplied()
        irrigation = plt.getIrrigationApplied()
        tot_irrigation = plt.get_Total_irrigation()
        
        metric_value, sign, delta_value = get_irrigation_info(cur_water_demand)
        
        st.markdown('##### Current Status')
        st.markdown(
        f"""
        <div data-testid="stMetric" class="unique-metric">
            <div data-testid="stMetricLabel">Required Water<div>
            <div data-testid="stMetricValue" class="{sign}">{metric_value} </div>
            <div data-testid="stMetricDelta" class="{sign}">{delta_value} </div>
        </div>
        """,
        unsafe_allow_html=True,)
        
        if cur_water_demand is None:
            pre_info = '➖'
            irri_info = '➖'
        else:
            pre_info = f"{prep:.2f}″"
            irri_info = f"{irrigation:.2f}″"
        
        l, r = st.columns(2)
        with l:
            st.html('<span class="low_indicator"></span>')
            st.metric('Precipitation', pre_info)
        with r:
            st.html('<span class="high_indicator"></span>')
            st.metric('Irrigation', irri_info)
        
        st.metric('Cumulative Irrigation', 
                  f"{int(tot_irrigation):,} L")
        
        if st.button("AI Recommendations"):
            with st.container(border=True):
                AI_str = makeRecomendation(plt)
                st.write(AI_str)
except Exception as e:
    print(e)
    title_text = "Whoops! It seems the data for this date decided to take a little break."
    st.markdown(
    f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        font-size: 24px;
        font-family: Arial, sans-serif;
        color: #555;
        text-align: center;">
        <h3>{title_text}</h3>
    </div>
    """,
    unsafe_allow_html=True
    )
    



    
    
    
    