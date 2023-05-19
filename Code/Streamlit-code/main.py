# -*- coding: utf-8 -*-
"""
Created April 2023

@author: Ishtiak Ahmed, Rupal Mittal, Andreas Weiss
"""

####################
### IMPORTS PACKAGES
####################

import os
import time
import sys
import streamlit as st
import json
import pandas as pd
pd.options.mode.chained_assignment = None  #removes a warning message
import csv
import numpy as np
from numpy import genfromtxt

##################
### IMPORT MODULES
##################

for module in ["./Code/Module-3", "./Code/Module-4", "./Code/Module-5", "./Code/Module-6", "./Code/Module-7", "./Code/Module-9"]:
    sys.path.append("%s/" %module)

#st.write(os.getcwd())
import module3_freight_demand
from module3_freight_demand import *
import module4_run_traffic_assignment_cpp
from module4_run_traffic_assignment_cpp import *
import module5_single_train_simulator
from module5_single_train_simulator import *
import module6_calculate_energy_use
from module6_calculate_energy_use import*
import module7_func
from module7_func import*
import module9_prepare_inputs
from module9_prepare_inputs import *
import module9_prepare_outputs
from module9_prepare_outputs import *

### Set Page Config
st.set_page_config(page_title=None, page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)
st.write(os.getcwd())
###################
### Paths and Files
###################

path_config = "./Config/"
static_input_path = "./Data/Static/"

### Config File
file_config_output = "%s/user_input.json" %(path_config)

### Relative Path where the Luparam Needs to be Written.
#path_trafassign = "./Module-4/TrafAssign/out/build/x64-debug"
path_trafassign = "./Code/Module-4/TrafAssign/"
file_luparams = "%s/luparams.txt" %path_trafassign

### Read Hard-Coded Input
databaseFile = "Lookup_NetSim.csv"
weightingDBFile = "%s/%s" %(static_input_path, databaseFile)
net_zones = pd.read_csv("%s/net_zones.csv" %static_input_path)              
#Price_carbonIntensity_mod7 = pd.read_csv("%s/commodityPrice_and_carbonIntensity_module7.csv" %(static_input_path)) 

###################
### Paths and Files
###################
tolerance = 1e-05

####################
### STREAMLIT BEGINS
####################

### Define Tab Names and Numbers
tab1, tab2,tab3, tab4 = st.tabs(["Inputs 1-3", "Inputs 4-7","Run Economic Assessment","Results"])

###################
### Module-1 Inputs
###################

### Create a Dictionary for the Decarbonization Options
energy_system_scenario_options = {
    None:None,
    0:"Reference/business as usual", 
    0.5 : "50% CO2 reduction by 2050", 
    1 :'100% CO2 reduction by 2050'
    }
with tab1:
    if 'energy_system_scenario' not in st.session_state:
         st.session_state.energy_system_scenario = None
    st.markdown('## 1. Choose a decarbonization pathway')
    energy_system_scenario = st.selectbox("",
                         (0, 0.5, 1),format_func=lambda x: energy_system_scenario_options.get(x))
    
    if st.button("Submit Selections"):
        st.session_state.energy_system_scenario = energy_system_scenario
        # config_input['energy_system_scenario'] = energy_system_scenario_options.get(st.session_state.energy_system_scenario)
    if st.button('Clear Selections'):
        st.session_state.energy_system_scenario = 0
        #config_input['energy_system_scenario'] = None

    ###################
    ### Module-2 Inputs
    ###################

    st.header("2. Inputs for Economic Scenarios and Activities")

    ### User Input Parameters
    
    ### Choose a Scenario for Economic Growth
    if 'econ_scn' not in st.session_state:
         st.session_state.econ_scn = None
    
    econ_scn = st.selectbox(
        label='Economic scenario', options=('Low (pessimistic)', 'High (optimistic)', 'Baseline (business as usual)'), key=2, 
        format_func=lambda x: str(x) + " economic growth", help = "For more details, see https://faf.ornl.gov/faf5/Documentation.aspx")
        
    
    ### Choose a Scenario for Economic Activity Change
    if 'freight_demand_scenario' not in st.session_state:
         st.session_state.freight_demand_scenario = None
    
    freight_demand_scenario = st.selectbox(
    label='Choose Change in Economic Activity', options=("Population Shift","Maritime Activity Reduction",
                                        "Agricultural Shift",
                                        "Agricultural Reduction"), key=4)
    
    if st.button("Submit Selections", key = 201):
        st.session_state.econ_scn = econ_scn
        st.session_state.freight_demand_scenario = freight_demand_scenario
        # config_input['econ_scn'] = st.session_state.econ_scn
        # config_input['freight_demand_scenario'] = st.session_state.freight_demand_scenario
    if st.button('Clear Selections',key = 202):
        st.session_state.econ_scn = None
        st.session_state.freight_demand_scenario = None
        # config_input['econ_scn'] = None
        # config_input['freight_demand_scenario'] = None

    ###################
    ### Module-3 Inputs
    ###################
    
    temoa_region =  pd.read_csv("%s/temoa_faf.csv" %(static_input_path))
    net_zones = pd.read_csv("%s/net_zones.csv" %(static_input_path))
    st.markdown('## 3. Inputs on Freight Demands')

    prcnt_default = {2025: 0.018, 2030: 0.0357, 2035 : 0.0529, 2040 : 0.0695, 2045 : 0.0851, 2050 : 0.1}
    st.write('Table below shows default proportions for coal and petrolium reductions. Click cell(s)\
             and enter value(s) if you need to change')
    #st.experimental_data_editor(pd.DataFrame(prcnt_default, index= ["Proportion"]))
        
    ff_red = pd.read_csv("%s/coal_petrolium_red.csv" %(static_input_path), header=0,index_col = 0)
    
#    ff_red = {'Year': list(range(2025, 2055, 5)), 'Coal Reduction Proportion': [x / 100.0 for x in range(25, 55, 5)],
#           'Petrolium Reduction Proportion': [x / 100.0 for x in range(25, 55, 5)]}
    st.write("Table below shows default proportions for coal and petrolium reductions. Click cell(s) and enter value(s) if\
             you need to change")
    #edited_df = st.experimental_data_editor(pd.DataFrame(data=ff_red), key = 302)
    
###################
### Module-4 Inputs
###################

with tab2:
    st.markdown('## 4. Inputs for Traffic Assignment')
    
    if 'exponent_mod4' not in st.session_state:
         st.session_state.exponent_mod4 = 0
    if 'ODmax_mod4' not in st.session_state:
         st.session_state.ODmax_mod4 = 0
    exponent_mod4 = st.slider(label = "Exponent parameter",min_value = 0.0, max_value = 2.0, value = 1.0)
    ODmax_mod4 = st.slider(label = "OD-max",min_value = 2000, max_value = 10000, value = 8000)
    
    if st.button("Submit Selections", key = 401):
        st.session_state.exponent_mod4 = exponent_mod4
        st.session_state.ODmax_mod4 = ODmax_mod4

        ### Write File luparams
        with open(file_luparams, 'w', newline="") as file:
            csvwriter = csv.writer(file,delimiter='\t') # 2. create a csvwriter object
            csvwriter.writerows([[st.session_state.exponent_mod4,14000.0,0, st.session_state.ODmax_mod4]]) # 5. write the rest of the data
#        config_input['exponent_mod4'] = st.session_state.exponent_mod4
#        config_input['ODmax_mod4'] = st.session_state.ODmax_mod4

    if st.button('Clear Selections', key = 402):
        st.session_state.exponent_mod4 = 0
        st.session_state.ODmax_mod4 = 0
#        config_input['exponent_mod4'] = None
#        config_input['ODmax_mod4'] = None
    
    st.info(f"You chose Exponent parameter = {st.session_state.exponent_mod4} and OD-max = {st.session_state.ODmax_mod4}") 

    ###################
    ### Module-5 Inputs
    ###################

    st.markdown('## 5. Inputs for Train Simulator')
    
    ### Read Region Dictionary
    reg_dic = {
        "CA":1,"CEN":2,"MID_AT":3,"N_CEN":4,"NE":5,"NW":6,"SE":7,"SW":8,"TX":9
        }
    
    ### Technology Distribution
    tech_frac_default = pd.DataFrame(
        {'Year': list(range(2025, 2055, 5)), 
                  'Diesel': [0.50,0.40,0.30,0.10,0.10,0.0],'Battery': [0.30,0.40,0.40,0.40,0.40,0.40],
                  'Hydrogen Hybrid':[0.20,0.20,0.20,0.20,0.20,0.40],'Diesel Hybrid':[0.0,0.0,0.10,0.10,0.10,0.0],
                  'Biodiesel': [0.0,0.0,0.0,0.10,0.10,0.0],'Biodiesel Hybrid': [0.0,0.0,0.0,0.10,0.10,0.20]
                  }
        )
    st.write("Table below shows default proportions for coal and petrolium reductions. Click and enter value(s) if\
             you need to change")
    # tech_frac_df = st.experimental_data_editor(tech_frac_default, key = 501)
    tech_frac_df = tech_frac_default
    sum_dist = tech_frac_df.iloc[:,[1,2,3,4,5,6]].sum(axis = 1)
    if sum(abs(sum_dist -1) > tolerance ) != 0:
        st.markdown(""":red[Error: Sum of Energy Source Fractions is not 1]""")
        
    else:
        st.button("Submit Selections", key = 502)
    tech_frac_df = tech_frac_df.set_index(["Year"]) 
    tech_frac_dic = tech_frac_df.to_dict('index')   
    # config_input['tech_fraction'] = tech_frac_dic
    
    ### Fix the nomenclature for technology
    fix_tech_fraction_nomenclature = {'Diesel': 'Diesel',
                       'Hydrogen Hybrid': 'HydHyb',
                       'Biodiesel': 'BioDie',
                       'Battery': 'Bat',
                       'Diesel Hybrid': 'DieHyb',
                       'Biodiesel Hybrid': 'BioHyb'}
    
    df_tmp = pd.DataFrame.from_dict(tech_frac_dic)
    df_tmp = df_tmp.rename(index=fix_tech_fraction_nomenclature)
    tech_frac_dic = df_tmp.to_dict()

    ###################
    ### Module-7 Inputs
    ###################
    
    st.markdown('## 7. Inputs for Energy Prices')
    st.write("Renewables Trajectories")
    renewable_prices = st.selectbox(
         label = '', options = ('Moderate', 'Conservative','Advanced'),key = 701)
    
    st.write("Oil/Natural Gas Prices")
    oil_prices = st.selectbox(
          label = '', options = ('Mid', 'Low','High'),key = 702)
    
    st.write("Hydrogen Subsidies (If yes, will be applied from 2025 to 2035")
    h2_sub = st.selectbox(
         label = '', options = ('Yes', 'No'),key = 703)
    
    ###################
    ### Module-9 Inputs
    ###################
    st.markdown('## 9. Inputs for Cost Analysis')
    #st.write("Annual discount rate (percentage point)")
    if 'discount_rate' not in st.session_state:
         st.session_state.discount_rate = None
    if 'tech_lifetime' not in st.session_state:
          st.session_state.tech_lifetime = None
    if 'contingency_factor' not in st.session_state:
          st.session_state.contingency_factor = None
    discount_rate = st.slider(label = "Annual discount rate (percentage point)",min_value = 0.02, max_value = 0.1, value = 0.1)
    tech_lifetime = st.slider(label = "Technology lifetime (year)",min_value = 10, max_value = 30, value = 30)
    contingency_factor = st.slider(label = "Contingency factor (%)",min_value = 5, max_value = 50, value = 20)

    if st.button("Submit Selections", key = 901):
        st.session_state.discount_rate = discount_rate
        st.session_state.tech_lifetime = tech_lifetime
        st.session_state.contingency_factor = contingency_factor

###########################
### Run Economic Assessment 
###########################

with tab3:
    st.markdown('## Run Module')

    if st.button("Submit All Inputs"):
        config_input ={"energy_system_scenario": energy_system_scenario_options.get(st.session_state.energy_system_scenario), 
                         "freight_demand_scenario": st.session_state.freight_demand_scenario, 
                         "year": "2025", 
                         "econ_scn": st.session_state.econ_scn,
                         "analy_yr": 2025, 
                         "prcnt": 0.018, 
                         "prcnt_ffc": 0.0, 
                         "prcnt_ffp": 0.0
                         }
        config_input["tech_fraction"] = tech_frac_dic
        st.write(config_input)
        with open(file_config_output, "w") as outfile:
         	json.dump(config_input, outfile, indent= '\t')
        
        years = list(range(2025, 2030, 5))
        for year in years:
            #dynamic input for module 3
            #prcnt_ffc = edited_df[(edited_df['Year'] == analy_yr)]['Coal Reduction Proportion'].to_list()[0]
            #prcnt_ffp = edited_df[(edited_df['Year'] == analy_yr)]['Petrolium Reduction Proportion'].to_list()[0]
            #ton_year = 'tons' + '_' + str(y)
            st.write(year)
            
            ##########################################################################################################             
            ########################################################################################################## 
            
            ############
            ### Module 3
            ############
            
            st.write("Running Module 3: Freight Demand Scenarios")
            net_flows = module3_freight_demand.create_total_flow(year, freight_demand_scenario, econ_scn, ff_red, 0.0175)
            
            ############
            ### Module 4
            ############
    
            st.write("Running Module 4: Traffic Assignment")
            module4_run_traffic_assignment_cpp.run_traffic_assignment(year)
    
            ############
            ### Module 5
            ############
    
            st.write("Running Module 5: Energy Intensity Matrix")
            #module5_energyintensity_option = input("Enter Option \n\"default\": Ecnonomic Assessment Scenario \n\"force--run\": Create the default look-up table again \n\"custom\": Enter your own AlignmentData and TrainData \n")
            module5_energyintensity_option="default"
            module5_single_train_simulator.create_energy_intensity_matrix_sts(option=module5_energyintensity_option)
    
            ############
            ### Module 6
            ############
    
            st.write("Running Module 6: Calculate Energy Use")
            module6_calculate_energy_use.calculate_energy_use(str(year))  

            ############
            ### Module 7
            ############
            st.write("Running Module 7")
            energy_prices(energy_system_scenario_options.get(st.session_state.energy_system_scenario), renewable_prices, h2_sub,oil_prices)

            ############
            ### Module 9
            ############
            
            st.write("Preparing Input Files for Module 9")
            module9_prepare_inputs.prepare_inputs_for_module9(str(year), save_mode="overwrite", print_summary=True)
                
            st.write("Preparing Output Files for Module 9")
            module9_prepare_outputs.module9_economic_assessment(st.session_state.discount_rate, 
                                                                st.session_state.tech_lifetime,st.session_state.contingency_factor)
            
            st.write("All Modules Finished")
            
        #     ##########################################################################################################             
        #     ########################################################################################################## 
        
        
#         ############
#         ### Module 9
#         ############
#         st.write("Running Module 9")
#         #read outputs from previous modules
        
#         module9_economic_assessment()
        
# %% Visualize n download data
# with tab4:
#     st.markdown('## Download and Visualize Data')
    
