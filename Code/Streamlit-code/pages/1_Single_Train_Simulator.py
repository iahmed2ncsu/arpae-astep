# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 11:59:33 2023

@author: Ishtiak
"""

import subprocess
import os
import streamlit as st
import time
import sys
import pandas as pd

##################
### IMPORT MODULES
##################

sys.path.append("./Code/Module-5")
import module5_single_train_simulator
from module5_single_train_simulator import *

###################
### Paths and Files
###################
module5_output_path = "./Data/Output/Module-5"
# %% dataframe conversion function
# this function converts the output data to utf-8 encoded data. It is important to download the outputs
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# %%set page config
st.set_page_config(page_title=None, page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)

###define dictionaries for UI
#region dictionary
region_ui_dict = {"CA":"California",
            "CEN":"Central",
            "MID_AT": "Mid-Atlantic",
            "N_CEN":"North-Central",
            "NE":"North-East",
            "NW":"North-West",
            "SE":"South-East",
            "SW":"South-West",
            "TX":"Texas"}
#technology dictionary
tech_ui_dict = {"Diesel":"Diesel",
             "BioDie": "Biodiesel",
             "DieHyb": "Diesel-hbrid",
             "BioHyb": "Biodiesel-hybrid",
             "HydHyb": "Hydrogen-hybrid",
             "Bat": "Battery"}

#define tab names and numbers
tab1, tab2,tab3 = st.tabs(["About", "Input","Run Single Train Simulator"])
# %% About page

page_title = "A-STEP: Achieving Sustainable Train Energy Pathways"
body = "A-STEP: Achieving Sustainable Train Energy Pathways"
subhead = "Single Train Simulator"\

with tab1:
    #st.set_page_config(layout='wide')
    #st.set_page_config(page_title=page_title)
    st.header(body)
    st.subheader(subhead)

    st.markdown(
    """The single train simulator (STS) allows analysts to study the movement of trains across alignments. It provides estimates of energy intensity (EI), or MWh/net-ton-mile, as affected by the propulsion technology employed, the train configuration, and the alignment. It can model a variety propulsion types like hydrogen, batteries, biodiesel, and overhead catenary. These can be combined as desired. It uses time as the basis for the simulation. It models the delivery of energy from the fuel source to the wheel-rail interface via the intermediate DC bus. It reports temporal trends in speed, acceleration, tractive effort, throttle position, power delivery, braking effort, energy recapture, maximum draw bar force, and many other metrics.

Each locomotive, tender, and car is modeled as a separate “entity”. Each one has a net and tare weight and Davis equation parameter values. The locomotives have a maximum power output, an adhesion coefficient, and an efficiency coefficient that translates power at the rail to power draw from the energy source. The tenders have an energy storage capacity.

Every second, the train’s current speed is compared with a desired speed, and if acceleration is appropriate, the throttle position is increased so a net, positive acceleration is applied. If the deceleration is needed, or constant speed should be maintained, the throttle position is adjusted, or the brakes are applied, or both. In the case of braking, regenerative braking is used first, followed by dynamic braking, and then friction braking. To prevent over-speeding, a backward-moving simulation (from end to start) is conducted first to downward adjust the maximum allowable speeds. A forward-moving simulation is then conducted (from beginning to end of the alignment) to create a second-by-second history of the train traversing the alignment, recording tractive effort, resistance, power demand, energy recovery, energy use, and other metrics.

Any combination of six locomotive types may be simulated: diesel, biodiesel, diesel hybrid, biodiesel hybrid, hydrogen fuel cell, and battery; as well as two types of tenders: battery and hydrogen fuel cell. Moreover, power can be drawn from an external source, like catenary, if it is available. 

The STS divides the propulsion process into two subprocesses. The first uses kinematics-based equations to calculate second-by-second forces at the wheel-rail interface, representing propulsion or braking. Then, using efficiency tables, it predicts the corresponding instantaneous energy consumption — that is, the power draw or demand— at the DC bus. The second subprocess relates power on the DC bus to the on-board energy source through a second set of efficiency tables. There are separate efficiency tables for each locomotive type (to repeat, diesel, biodiesel, diesel hybrid, biodiesel hybrid, hydrogen fuel cell, and battery). Moreover, when catenary exists, it is used as the energy source, and an additional efficiency table is employed.""")

with tab2:
    if 'uploaded_alignment_data' not in st.session_state:
          st.session_state.uploaded_alignment_data = None
    if 'uploaded_train_data' not in st.session_state:
          st.session_state.uploaded_train_data = None
    if 'uploaded_alignment_data' not in st.session_state:
          st.session_state.uploaded_alignment_data = None
         
    st.markdown('#### Upload train and alignment data in appropriate formats')
    st.markdown('#####  For more info about the formats, please check the user manual')
    uploaded_alignment_data = st.file_uploader("Upload custom alignment data in a csv file")
    if uploaded_alignment_data is not None:
        st.session_state.uploaded_alignment_data = uploaded_alignment_data
    uploaded_train_data = st.file_uploader("Upload custom train data in a csv file")
    if uploaded_train_data is not None:
         st.session_state.uploaded_train_data = uploaded_train_data
    
    ### Choose a region
    if 'region' not in st.session_state:
         st.session_state.region = None 
    region = st.selectbox(
        label='Region', options=('CA','CEN','MID_AT','N_CEN','NE','NW','SE','SW','TX'), format_func=lambda x: region_ui_dict.get(x),
        key='sts_3' 
        )
    ### Choose a technology
    if 'technology' not in st.session_state:
         st.session_state.technology = None 
    technology = st.selectbox(
        label='Technology', options=('Bat','BioDie','BioHyb','DieHyb','Diesel','HydHyb'), format_func=lambda x: tech_ui_dict.get(x),
        key='sts_5' 
        )
    ### Choose number of train cars
    if 'car_number' not in st.session_state:
         st.session_state.car_number = None 
    car_number = st.selectbox(
        label='Number of cars', options=(50,100,150), key='sts_6' 
        )
    
    if st.button("Submit Inputs", key = 'sts_7'):
        st.session_state.region = region
        st.session_state.technology = technology
        st.session_state.car_number = car_number
with tab3:    
    @st.experimental_memo()
    def computation():
        df_result = module5_single_train_simulator.create_energy_intensity_matrix_sts("custom", st.session_state.uploaded_alignment_data, 
                                                                          st.session_state.uploaded_train_data,st.session_state.region,
                                                                          st.session_state.technology, st.session_state.car_number)
        return df_result
        
        
    if 'run_sts' not in st.session_state:
         st.session_state.run_sts = 0
    if uploaded_train_data  is None or uploaded_alignment_data is None or st.session_state.region is None or\
        st.session_state.technology is None or st.session_state.car_number is None:
        st.warning("Upload all necessary data first.")
    else:
        run_sts = st.button('▶️ Press to run the simulation')
        if run_sts:
            st.session_state.run_sts = 1
        if st.session_state.run_sts == 1:
            start = time.time()
            computation()
            df_result = pd.read_csv("%s/EnergyIntensity_Matrix_Custom.csv " %(module5_output_path))
            end = time.time()
            st.info(
               f"Run time = {round(end-start,ndigits = 2)} seconds"
            )
            st.download_button(
                "Download Energy Intensity Matrix",
                convert_df(df_result),
                "EnergyIntensity_Matrix_Custom.csv",
                "text/csv",
                key='dl_sts'
            )

   