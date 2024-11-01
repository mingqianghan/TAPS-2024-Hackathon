import numpy as np

class DefinePlot:
    def __init__(self, plot_data, plot_date):
        self.plot_id = plot_data['Plot #']
        self.plot_date = plot_date
        self.top_left_y = plot_data['top_left_y']
        self.top_left_x = plot_data['top_left_x']
        self.bottom_right_y = plot_data['bottom_right_y']
        self.bottom_right_x = plot_data['bottom_right_x']
        self.water_stress_with_NAN = plot_data['plot_water_index']
        self.water_stress = self.fill_nan()  # Call the method to fill NaNs
        self.mean_water_stress = plot_data['Mean_Water_Stress']
        self.planting_date = plot_data['Planting']
        self.field_id = plot_data['TRT']
        self.v9 = plot_data['V9']
        self.v12 = plot_data['V12']
        self.VT_R1 = plot_data['VT/R1']
        self.R2 = plot_data['R2']  # Changed from list to direct assignment
        self.present_waterdemand = 0
        self._plot_graph = None  # Attribute to hold the plot graph
        self.plot_water_required = None
        self.Block_Id = plot_data['Block_ID']
        self.plot_Area = plot_data['Area']
        self.total_irrigation = None
        self.irrigationGraph = None
        self.present_waterContent = None
        self.Total_CurrentApplied_Water = None
        self.IrrigationApplied = None
        self.PrecipitationApplied = None
        self.RecomendationStatement = None

        
        # Initialize water_content
        self.water_content = 0
        
        # Calculate max water stress
        self.max = np.max(self.water_stress)

    def fill_nan(self):
        # Calculate the mean of the array, ignoring NaN values
        mean_water_stress = np.nanmean(self.water_stress_with_NAN)

        # Replace NaN values with the calculated mean
        filled_array = np.where(np.isnan(self.water_stress_with_NAN), mean_water_stress, self.water_stress_with_NAN)
        return filled_array

    # Getter methods
    def get_plot_id(self):
        return self.plot_id

    def get_water_stress(self):
        return self.water_stress

    def get_mean_water_stress(self):
        return self.mean_water_stress
    
    def get_plot_date(self):
        return self.plot_date

    def get_planting_date(self):
        return self.planting_date

    def get_v9(self):
        return self.v9

    def get_v12(self):
        return self.v12

    def get_vt_r1(self):
        return self.VT_R1

    def get_r2(self):
        return self.R2

    def get_present_water_demand(self):
        return self.present_waterdemand

    def get_water_content(self):
        return self.water_content

    def get_plot_graph(self):
        return self._plot_graph
    
    def get_block_id(self):
        return self.Block_Id

    def get_plot_area(self):
        return self.plot_Area
    
    def get_waterRequired(self):
        return self.plot_water_required
    
    def get_TreatmentID(self):
        return self.field_id
    
    def get_Total_irrigation(self):
        return self.total_irrigation
    
    def getIrrigationGraph(self):
        return self.irrigationGraph
    
    def getPresentWater_Content(self):
        return self.present_waterContent
    
    def getTotal_CurrentApplied_Water(self):
        return self.Total_CurrentApplied_Water
    
    def getPrecipitationApplied(self):
        return self.PrecipitationApplied

    def getIrrigationApplied(self):
        return self.IrrigationApplied
    
    def getRecomendationStatement(self):
        return self.RecomendationStatement
    
    def getPlotDate(self):
        return self.plot_date
    

    # Setter methods
    def set_plot_id(self, plot_id):
        self.plot_id = plot_id

    def set_water_content(self, water_content):
        self.water_content = water_content

    def set_plot_date(self, date):
        self.plot_date = date

    def set_planting_date(self, planting_date):
        self.planting_date = planting_date

    def set_v9(self, v9):
        self.v9 = v9

    def set_v12(self, v12):
        self.v12 = v12

    def set_vt_r1(self, vt_r1):
        self.VT_R1 = vt_r1

    def set_r2(self, r2):
        self.R2 = r2

    def set_present_water_demand(self, water_demand):
        self.present_waterdemand = water_demand

    def set_plot_graph(self, graph):
        self._plot_graph = graph

    def set_block_id(self, block_id):
        self.Block_Id = block_id

    def set_plot_area(self, plot_area):
        self.plot_Area = plot_area

    def set_waterRequired(self,waterRequired):
        self.plot_water_required = waterRequired

    def set_treatmentID(self,TreatmentID):
        self.field_id = TreatmentID

    def set_Total_irrigation(self,Total_irrigation):
        self.total_irrigation = Total_irrigation

    def setIrrigationGraph(self,Irrigation_graph):
        self.irrigationGraph = Irrigation_graph

    def setPresentWaterContent(self,PresentWaterContent):
        self.present_waterContent = PresentWaterContent

    def setTotal_CurrentApplied_Water(self,Total_CurrentApplied_Water):
        self.Total_CurrentApplied_Water = Total_CurrentApplied_Water


    def setPrecipitationApplied(self, water_applied_precipitation):
        self.PrecipitationApplied = water_applied_precipitation

    def setIrrigationApplied(self,water_applied_irrigation):
        self.IrrigationApplied = water_applied_irrigation

    def setRecomendationStatment(self,Recomendation):
        self.RecomendationStatement = Recomendation

    def setPlotDate(self,date):
        self.plot_date = date
        


