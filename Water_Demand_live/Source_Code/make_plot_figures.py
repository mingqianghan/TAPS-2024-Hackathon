import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_Plot_figures(Water_Required, Total_Applied_Water, Irrigation_Water_Applied, 
                      Precipitation_Water_Applied, 
                      planting_date, specified_date, 
                      time_series_df, plot):

          # Define colors and labels for growth stages
    stage_colors = {
        'Planting': '#59a89c',  # Lime Green
        'V9': '#004e98',        # Green
        'V12': '#f0c571',       # Yellow
        'VT/R1': '#a559aa',     # Orange
        'R2': '#cecece'         # Red
    }


    descriptive_labels = {
        'Planting': 'Planting', 'V9': 'V9 - Vegetative', 'V12': 'V12 - Tasseling',
        'VT/R1': 'VT/R1 - R1 Stage', 'R2': 'R2 - Grain Fill'
    }

    # Create subplots with a shared x-axis, Total Water Applied as the first plot
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.015,
        subplot_titles=["", "", "", ""],
        row_heights=[0.35, 0.65],
        specs=[[{"secondary_y": True}], [{}]]
        # subplot_titles=["Total Water Applied Over Time (Inverted)", "Water Required Over Time", 
        #                 "Irrigation Water Applied Over Time", "Precipitation Water Applied Over Time"]
    )

    # Plot the Total Water Applied as an inverted bar chart in the first subplot
    fig.add_trace(
        go.Bar(x=Total_Applied_Water.index, y=Total_Applied_Water['Total Water Applied'], 
               marker=dict(color='#00a6fb'), showlegend=True, name='Precipitation' ),
        row=1, col=1,  secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(x=Irrigation_Water_Applied.index, y=Irrigation_Water_Applied['Irrigation Applied'], 
               marker=dict(color='#fee440'), showlegend=True, name='Irrigation'),
        row=1, col=1, secondary_y=True
    )

    '''
    # Plot the Water Required data in the second subplot
    fig.add_trace(
        go.Scatter(x=Water_Required.index, y=Water_Required['Water Required'],
                   mode='lines+markers',
                   line=dict(color='red'),  
                   showlegend=False),
        row=2, col=1
    )
    '''
    # Add an invisible trace as a spacer to force a line break 
    fig.add_trace(go.Scatter(
    x=[None], y=[None], mode='lines', 
    line=dict(color='#3f3f3f'),
    showlegend=True, name=""
    ))

    # Water Surplus area (above zero) in the Water Required subplot
    water_surplus = Water_Required.where(Water_Required['Water Required'] > 0, 0)
    fig.add_trace(
        go.Scatter(
            x=Water_Required.index, 
            y=water_surplus['Water Required'],
            fill='tozeroy', 
            fillcolor='rgba(22,219,101,0.5)',  
            line=dict(color='rgba(4,71,28,1)'),
            name='Water Surplus'
        ),
        row=2, col=1
    )

    # Water Deficit area (below zero) in the Water Required subplot
    water_deficit = Water_Required.where(Water_Required['Water Required'] < 0, 0)
    fig.add_trace(
        go.Scatter(
            x=Water_Required.index, 
            y=water_deficit['Water Required'],
            fill='tozeroy', 
            fillcolor='rgba(255,89,94,0.5)',  
            line=dict(color='rgba(164,22,35,1)'),
            name='Water Deficit'
        ),
        row=2, col=1
    )

    '''
    # Plot the Irrigation Water Applied over time in the third subplot
    fig.add_trace(
        go.Scatter(x=Irrigation_Water_Applied.index, y=Irrigation_Water_Applied['Irrigation Applied'],
                   mode='lines+markers', name='Irrigation Water (inches)', 
                   line=dict(color='#2ec4b6')),
        row=3, col=1
    )
    
    # Plot the Precipitation Water Applied over time in the fourth subplot
    fig.add_trace(
        go.Scatter(x=Precipitation_Water_Applied.index, y=Precipitation_Water_Applied['Precipitation'],
                   mode='lines+markers', name='Precipitation (inches)', 
                   line=dict(color='teal')),
        row=4, col=1
    )
    '''
    
    # Add vertical lines for growth stages across all subplots
    growth_stages_dates2 = {
        'Planting': plot.get_planting_date().date(),
        'V9': plot.get_v9().date(),
        'V12': plot.get_v12().date(),
        'VT/R1': plot.get_vt_r1().date(),
        'R2': plot.get_r2().date()
    }
    for growth_stage_label, growth_stage_date in growth_stages_dates2.items():
        if planting_date <= growth_stage_date <= specified_date:
            color = stage_colors[growth_stage_label]
            # Add a vertical line for each growth stage in all subplots
            for row in range(1, 3):  # Apply to each row (1 to 4)
                fig.add_vline(
                    x=growth_stage_date, line=dict(color=color, dash='dash'),
                    row=row, col=1
                )
            
            # Add legend markers for each growth stage (only once)
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='lines',
                    line=dict(color=color, dash='dash'),
                    showlegend=True,
                    name=descriptive_labels[growth_stage_label]
                ),
                row=2, col=1
            )
            

    # Layout background adjustment
    # fig.update_layout(
    #     plot_bgcolor='rgba(0, 0, 0, 0)',
    #     paper_bgcolor='#393939',
    #     yaxis=dict(title="Total Water Applied"),  # Y-axis for the first plot
    #     yaxis2=dict(title="Water Required"),  # Y-axis for the second plot
    #     yaxis3=dict(title="Irrigation Applied"),  # Y-axis for the third plot
    #     yaxis4=dict(title="Precipitation"),  # Y-axis for the fourth plot
    #     xaxis=dict(tickangle=45),
    #     legend=dict(itemsizing='constant', groupclick='toggleitem'),
    #     font=dict(
    #         family="sans-serif",
    #         size=18,
    #         color = '#000000'
    #     ),
    #     height=1000
    # )

    fig.update_layout(
    xaxis=dict(gridcolor='rgba(0, 0, 0, 0)'),  # Invisible vertical grid lines for xaxis
    xaxis2=dict(gridcolor='rgba(0, 0, 0, 0)'), 
    xaxis3=dict(gridcolor='rgba(0, 0, 0, 0)'),  
    xaxis4=dict(gridcolor='rgba(0, 0, 0, 0)'),  
    )
    
    fig.update_yaxes(row=1, col=1,  secondary_y=False)
    fig.update_yaxes(row=1, col=1,  secondary_y=True)

    fig.update_layout(
    plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
    paper_bgcolor='#3f3f3f',  # Paper background color
    yaxis=dict(
        title="Precipitation (inches)",  # Y-axis for the first plot
        title_font=dict(color='white'),  # Y-axis title color
        tickfont=dict(color='white', size=13),  # Y-axis tick label color
        gridcolor='rgba(0, 166, 251, 0.3)',  # Horizontal grid line color
        zeroline=True,  # Show the zero line
        zerolinecolor='white',  # Color of the zero line
        autorange="reversed", 
    ),
    yaxis2=dict(
        title="Irrigation (inches)",  # Y-axis for the second plot
        title_font=dict(color='white'),  # Y-axis title color
        tickfont=dict(color='white', size=13),  # Y-axis tick label color
        gridcolor='rgba(254, 228, 64, 0.3)',  # Horizontal grid line color
        zeroline=True,  # Show the zero line
        zerolinecolor='white',  # Color of the zero line
        autorange="reversed",
    ),
    yaxis3=dict(
        #title="Water Required (inches)",  # Y-axis for the third plot
        #title_font=dict(color='white'),  # Y-axis title color
        tickfont=dict(color='white'),  # Y-axis tick label color
        gridcolor='rgba(255, 255, 255, 0.2)',  # Horizontal grid line color
        zeroline=True,  # Show the zero line
        zerolinecolor='white',  # Color of the zero line
    ),
    
    #yaxis4=dict(
    #   title="Precipitation",  # Y-axis for the fourth plot
    #   title_font=dict(color='white'),  # Y-axis title color
    #   tickfont=dict(color='white'),  # Y-axis tick label color
    #   gridcolor='rgba(255, 255, 255, 0.2)',  # Horizontal grid line color
    #   zeroline=True,  # Show the zero line
    #   zerolinecolor='white',  # Color of the zero line
    #),

    xaxis=dict(
        tickangle=45,
        tickfont=dict(color='white'),  # X-axis tick label color
        #gridcolor='white',  # Vertical grid line color
        zeroline = True,
        zerolinecolor = 'White'
    ),
    legend=dict(
        itemsizing='trace',          # Keep legend items a constant size
        orientation='h',                # Horizontal orientation
        x=0.48,                          # Centered horizontally
        y=1.01,                          # Positioned above the plot
        xanchor='center',               # Anchor the legend horizontally to the center
        yanchor='bottom',               # Anchor the legend vertically to the bottom
        traceorder='normal',            # Default ordering of traces
        bgcolor='rgba(255, 255, 255, 0)',  # Semi-transparent background
        font=dict(
            family="sans-serif",
            size=12.7,
            color='#ffffff'
        ),
        ),
    font=dict(
        family="sans-serif",
        size=20,
        color='#000000'
    ),
    height=1000
)

    # fig.update_layout(
    # xaxis=dict(showgrid=False),  
    # xaxis2=dict(showgrid=False), 
    # xaxis3=dict(showgrid=False),  
    # xaxis4=dict(showgrid=False),  
    #     )
    
    
    

    
    # fig.update_layout(
    # yaxis=dict(showgrid=False),   # Turns off vertical grid lines for the first subplot
    # yaxis2=dict(showgrid=False),  # Turns off vertical grid lines for the second subplot
    # yaxis3=dict(showgrid=False),  # Turns off vertical grid lines for the third subplot
    # yaxis4=dict(showgrid=False),  # Turns off vertical grid lines for the fourth subplot
    #     )

    #adjust subplot height

    fig.update_layout(height=700)  # Adjust the height to your preference

    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))  # Adjust left, right, top, bottom margins



    return fig
