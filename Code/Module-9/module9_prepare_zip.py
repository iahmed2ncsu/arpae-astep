# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 06:03:18 2023

@author: Ishtiak
"""

import io
import zipfile
import streamlit as st
import pandas as pd
import tarfile
import sys

# %% dataframe conversion function
# this function converts the output data to utf-8 encoded data. It is important to download the outputs
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

def prepare_zip():
    #################################
    ### Input/Output and Static files in repository
    #################################

    config_input_path = "./Config/user_input.json"
    static_input_path = "./Data/Static/"

    module4_output_path = "./Data/Output/Module-4"
    module6_output_path = "./Data/Output/Module-6"
    module7_output_path = "./Data/Output/Module-7"
    module8_output_path = "./Data/Output/Module-8"
    module9_output_path = "./Data/Output/Module-9"
    module9_input_path = "./Data/Input/Module-9"
    
    
    #################################
    ### Read files
    #################################
    levelized_cost_df = convert_df(pd.read_csv("%s/levelized_cost.csv" %module9_output_path))
    carbon_intensity_df = convert_df(pd.read_csv("%s/carbon_intensity.csv" %module9_output_path))
    lkflows_df = convert_df(pd.read_csv("%s/lkflows.csv" %module4_output_path))
    tm_per_temoa_df = convert_df(pd.read_csv("%s/tm_per_temoa.csv" %module4_output_path))
    curvature_bins_per_temoa_df = convert_df(pd.read_csv("%s/curvature_bins_per_temoa.csv" %module4_output_path))
    grade_bins_per_temoa_df = convert_df(pd.read_csv("%s/grade_bins_per_temoa.csv" %module4_output_path))
    energy_region_histogram_Hydrogen_df = convert_df(pd.read_csv("%s/energy_region_histogram_Hydrogen.csv" %module6_output_path))
    tm_energy_per_charging_station_df = convert_df(pd.read_csv("%s/tm_energy_per_charging_station.csv" %module6_output_path))
    fleet_size_hrs_df = convert_df(pd.read_csv("%s/fleet_size_hrs.csv" %module6_output_path))
    energy_region_histogram_Battery_df = convert_df(pd.read_csv("%s/energy_region_histogram_Battery.csv" %module6_output_path))
    tm_energy_per_state_df = convert_df(pd.read_csv("%s/tm_energy_per_state.csv" %module6_output_path))
    tm_energy_per_temoa_df = convert_df(pd.read_csv("%s/tm_energy_per_temoa.csv" %module6_output_path))
    energy_for_Mod9_df = convert_df(pd.read_csv("%s/energy_for_Mod9.csv" %module9_input_path))
    energy_price_for_Mod9_df = convert_df(pd.read_csv("%s/energy_price_for_Mod9.csv" %module9_input_path))
    refueling_for_Mod9_df = convert_df(pd.read_csv("%s/refueling_for_Mod9.csv" %module9_input_path))
    traffic_flow_for_Mod9_df = convert_df(pd.read_csv("%s/traffic_flow_for_Mod9.csv" %module9_input_path))
    train_for_Mod9_df = convert_df(pd.read_csv("%s/train_for_Mod9.csv" %module9_input_path))

    
    #################################
    ### Zip files
    #################################
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in [
            ("levelized_cost.csv", io.BytesIO(levelized_cost_df)), 
            ("carbon_intensity.csv", io.BytesIO(carbon_intensity_df)),
            ("lkflows.csv", io.BytesIO(lkflows_df)),
            ("tm_per_temoa.csv", io.BytesIO(tm_per_temoa_df)),
            ("curvature_bins_per_temoa.csv", io.BytesIO(curvature_bins_per_temoa_df)),
            ("grade_bins_per_temoa.csv", io.BytesIO(grade_bins_per_temoa_df)),
            ("energy_region_histogram_Hydrogen.csv", io.BytesIO(energy_region_histogram_Hydrogen_df)),
            ("tm_energy_per_charging_station.csv", io.BytesIO(tm_energy_per_charging_station_df)),
            ("fleet_size_hrs.csv", io.BytesIO(fleet_size_hrs_df)),
            ("energy_region_histogram_Battery.csv", io.BytesIO(energy_region_histogram_Battery_df)),
            ("tm_energy_per_state.csv", io.BytesIO(tm_energy_per_state_df)),
            ("tm_energy_per_temoa.csv", io.BytesIO(tm_energy_per_temoa_df)),
            ("energy_for_Mod9.csv", io.BytesIO(energy_for_Mod9_df)),
            ("energy_price_for_Mod9.csv", io.BytesIO(energy_price_for_Mod9_df)),
            ("refueling_for_Mod9.csv", io.BytesIO(refueling_for_Mod9_df)),
            ("traffic_flow_for_Mod9.csv", io.BytesIO(traffic_flow_for_Mod9_df)),
            ("train_for_Mod9.csv", io.BytesIO(train_for_Mod9_df)),
            
        ]:
            zip_file.writestr(file_name, data.getvalue())
    #################################
    ### Download zipped files
    #################################
    left_col, right_col = st.columns([2, 1])
    
    with right_col:
        st.download_button(
            "⬇️Download csv", 
            file_name="data.zip",
            mime = "application/zip",
            data=zip_buffer
        )
    left_col.markdown(
        """
        ### Output Description

        Click the button on the right to download all the outputs in a zipped folder. A short description of each output is given below:
        - **levelized_cost.csv:** An output from Module 9. Get description from Tongchuan
        - **carbon_intensity.csv:** An output from Module 9. Get description from Tongchuan
        - **lkflows.csv:**  An output from Module 4. Get description from George
        - **tm_per_temoa.csv:** An output from Module 4. Get description from George
        - **curvature_bins_per_temoa.csv:** An output from Module 4. Get description from George
        - **grade_bins_per_temoa.csv:** An output from Module 4. Get description from George 
        - **energy_region_histogram_Hydrogen.csv:** An output from Module 6. Get description from George 
        - **tm_energy_per_charging_station.csv:** An output from Module 6. Get description from George 
        - **fleet_size_hrs.csv:** An output from Module 6. Get description from George 
        - **energy_region_histogram_Battery.csv:** An output from Module 7. Get description from Adi 
        - **refueling_for_Mod9.csv:** An output from Module 8. Get description from Derek 
        - **traffic_flow_for_Mod9.csv:** An output from Module 8. Get description from Derek 
        - **train_for_Mod9.csv:** An output from Module 8. Get description from Derek 
        """
    )
    
    