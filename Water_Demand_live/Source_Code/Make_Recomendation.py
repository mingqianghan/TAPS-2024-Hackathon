## Recomendation Creation

import pandas as pd
from datetime import datetime, timedelta
import requests
from openai import OpenAI

#fetch Plot data at time t

def fetch_plot_data_at_time_T(plot):
  
    
    # Create a dictionary for this single row
    plot_data = {
        "Date": plot.getPlotDate(),
        "Plot ID": plot.get_plot_id,
        "Water Required": plot.get_waterRequired(),
        "Water Demand": plot.get_present_water_demand(),
        "Water Content": plot.getPresentWater_Content(),
        "Total Water Applied": plot.getTotal_CurrentApplied_Water(),
        "Irrigation": plot.getIrrigationApplied(),
        "Precipitation": plot.getPrecipitationApplied()
    }
            

    return plot_data  # Returning the list of individual DataFrames


def create_irrigation_prompt(date, plot_id, water_required, 
                             water_demand, soil_water_content,
                               total_water_applied, 
                               irrigation, precipitation):
    return f"""
    Given the following data for the crop field on {date} (Plot ID: {plot_id}):

    - Current water demand: {water_demand} inches
    - Water content in the soil: {soil_water_content} inches
    - Total water applied: {total_water_applied} inches
    - Recent irrigation: {irrigation} inches
    - Predicted precipitation: {precipitation} inches
    - Water required to maintain optimal conditions: {water_required} inches

    Please generate a recommendation for the user. The response should be conversational, clear,succinct and provide specific actions for the user. Include any helpful context about why this irrigation level is needed.

    Example response:
    "Based on the current conditions, it's recommended to apply {water_required} inches of irrigation today to maintain optimal soil moisture and meet crop water demand. This amount is calculated considering the current soil water content,
      total water applied, and the anticipated precipitation.
        Applying this level of irrigation will help reduce plant stress and support healthy growth."

    Provide the response as if you are advising the user directly.
    """



#

client = OpenAI(api_key= OPENAI_API_KEY2)

def generate_recommendation_chatgpt(irrigation_needed, plot_data):

    
    prompt = create_irrigation_prompt(plot_data['Date'],
                                        plot_data['Plot ID'], 
                                        plot_data['Water Required'], 
                                        plot_data['Water Demand'],
                                        plot_data['Water Content'],
                                        plot_data['Total Water Applied'],
                                        plot_data['Irrigation'],
                                        plot_data['Precipitation'])
    
    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return chat_response.choices[0].message.content



# Recommendation system

# plot_id = int(input("Provide plot id or 'q' to quit: "))
# date_input = str(input("Provide date or 'q' to quit: "))

def makeRecomendation(Plot):

    # Get recommendation from model
    irrigation_needed = 2
     
    plot_data = fetch_plot_data_at_time_T(Plot)
    # Generate conversational advice with ChatGPT
    recommendation = generate_recommendation_chatgpt(irrigation_needed, plot_data)
    return recommendation



