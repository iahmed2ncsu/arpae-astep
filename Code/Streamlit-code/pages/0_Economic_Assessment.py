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

            
####################
### STREAMLIT SET-UP
####################

### Set Page Config
st.set_page_config(page_title="main", page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)
st.sidebar.markdown("# Economic Assessment Tool")
#st.write(os.getcwd())
###################
### Paths and Files
###################

path_config = "./Config/"
static_input_path = "./Data/Static"

### Config File
file_config_output = "%s/user_input.json" %(path_config)

### Relative Path where the Luparam Needs to be Written.
#path_trafassign = "./Module-4/TrafAssign/out/build/x64-debug"
path_trafassign = "./Code/Module-4/TrafAssign/"
file_luparams = "%s/luparams.txt" %path_trafassign

##Relative path where module-9 outputs, i.e., levelized cost and carbon intensity get written
module9_output_path = "./Data/Output/Module-9"

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
tab1, tab2,tab3, tab4,tab5,tab6 = st.tabs(["Inputs 1-3", "Inputs 4-9","Run Economic Assessment","Download Outputs",
                                           "Visualize Levelized Cost", "Visualize Carbon Intensity"])

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
    label='Choose Change in Economic Activity', options=("Baseline","Population Shift","Maritime Activity Reduction",
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

    #prcnt_default = {2025: 0.018, 2030: 0.0357, 2035 : 0.0529, 2040 : 0.0695, 2045 : 0.0851, 2050 : 0.1}
    prcnt_default = {'Year': list(range(2025, 2055, 5)), 'Proportion':[0.018,0.0357, 0.0529, 0.0695, 0.0851, 0.1]}
    st.write('Table below shows default proportions of change for the selected economic activity')
    prcnt_default_edited = st.experimental_data_editor(pd.DataFrame(prcnt_default))
    example_prcnt_default = prcnt_default_edited[(prcnt_default_edited['Year'] == 2025)]['Proportion'].to_list()[0]
    st.write(f"Example: Coal reduction proportion for 2025 = {example_prcnt_default}")
    #ff_red = pd.read_csv("%s/coal_petrolium_red.csv" %(static_input_path), header=0,index_col = 0)
    
    ff_red2 = {'Year': list(range(2025, 2055, 5)), 'Coal Reduction Proportion': [x / 100.0 for x in range(25, 55, 5)],
           'Petrolium Reduction Proportion': [x / 100.0 for x in range(25, 55, 5)]}
    st.write("Table below shows default proportions for coal and petrolium reductions. Click cell(s) and enter value(s) if\
             you need to change")
    edited_ff_red = st.experimental_data_editor(pd.DataFrame(data=ff_red2), key = 302)
    example_ffc = edited_ff_red[(edited_ff_red['Year'] == 2025)]['Petrolium Reduction Proportion'].to_list()[0]
    #example_ffc = edited_ff_red.iloc[0][int((2025 - 2025)/5)]
    st.write(f"Example: Petrolium reduction proportion for 2025 = {example_ffc}")
###################
### Module-4 Inputs
###################

with tab2:
    st.markdown('## 4. Inputs for Traffic Assignment')
    
    if 'exponent_mod4' not in st.session_state:
         st.session_state.exponent_mod4 = None
    if 'ODmax_mod4' not in st.session_state:
         st.session_state.ODmax_mod4 = None
    if 'factorup' not in st.session_state:
         st.session_state.factorup = None
    exponent_mod4 = st.slider(label = "Exponent parameter",min_value = 0.0, max_value = 2.0, value = 1.0)
    ODmax_mod4 = st.slider(label = "OD-max",min_value = 2000, max_value = 10000, value = 8000)
    factorup = st.slider(label = "Expansion factor",min_value = 1.0, max_value = 5.0, value = 3.0)
    
    if st.button("Submit Selections", key = 401):
        st.session_state.exponent_mod4 = exponent_mod4
        st.session_state.ODmax_mod4 = ODmax_mod4
        st.session_state.factorup = factorup
        
        ### Write File luparams
        with open(file_luparams, 'w', newline="") as file:
            csvwriter = csv.writer(file,delimiter='\t') # 2. create a csvwriter object
            csvwriter.writerows([[st.session_state.exponent_mod4,14000.0,0, st.session_state.ODmax_mod4]]) # 5. write the rest of the data
        #interpolate recommended value of factorup based on od-max input
        factorup_advised = 3 - (3-1.56)/(7000-2000)*(st.session_state.ODmax_mod4 - 2000) 
#        config_input['exponent_mod4'] = st.session_state.exponent_mod4
#        config_input['ODmax_mod4'] = st.session_state.ODmax_mod4
        st.markdown(f"##### Recommended value of expansion factor for the selected OD-max = {factorup_advised}")

    if st.button('Clear Selections', key = 402):
        st.session_state.exponent_mod4 = None
        st.session_state.ODmax_mod4 = None
        st.session_state.factorup = None
        
#        config_input['exponent_mod4'] = None
#        config_input['ODmax_mod4'] = None
    
    st.info(f"You chose Exponent parameter = {st.session_state.exponent_mod4}, OD-max = {st.session_state.ODmax_mod4} and\
            Expansion factor = {st.session_state.factorup}") 

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
    
    tech_frac_edited = st.experimental_data_editor(pd.DataFrame(data=tech_frac_default), key = 501)
    
    simulator_option_dictionary = {
        "sts" : "Single Train Simulator", 
        "mts" : "Multi-train Simulator"
        }
         
    if 'simulator_option' not in st.session_state:
          st.session_state.simulator_option = 'sts'
    simulator_option = st.selectbox(
          label = 'Choose an option for the train simulator', options = ("sts", "mts"),
          format_func=lambda x: simulator_option_dictionary.get(x), key = 502)
    
    if st.button("Submit Selection", key = 503):
        st.session_state.simulator_option = simulator_option
        st.write(st.session_state.simulator_option)
    
    tech_frac_df = tech_frac_edited
    sum_dist = tech_frac_df.iloc[:,[1,2,3,4,5,6]].sum(axis = 1)
    # if sum(abs(sum_dist -1) > tolerance ) != 0:
    #     st.markdown(""":red[Error: Sum of Energy Source Fractions is not 1]""")
        
    # else:
    #     st.button("Submit Selections", key = 504)
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
    if 'renewable_prices' not in st.session_state:
         st.session_state.renewable_prices = None
    if 'oil_prices' not in st.session_state:
         st.session_state.oil_prices = None
    if 'h2_sub' not in st.session_state:
         st.session_state.oil_prices = None
    
    renewable_prices = st.selectbox(
         label = 'Renewables Trajectories', options = ('Moderate', 'Conservative','Advanced'),key = 701)

    oil_prices = st.selectbox(
          label = 'Oil/Natural Gas Prices', options = ('Mid', 'Low','High'),key = 702)
    
    h2_sub = st.selectbox(
         label = 'Hydrogen Subsidies (If yes, will be applied from 2025 to 2035)', options = ('Yes', 'No'),key = 703)
    
    if st.button("Submit Selections", key = 704):
        st.session_state.renewable_prices = renewable_prices
        st.session_state.oil_prices = oil_prices
        st.session_state.h2_sub = h2_sub
    
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
    ##################
    ### IMPORT MODULES
    ##################

    for module in ["./Code/Module-3", "./Code/Module-4", "./Code/Module-5", "./Code/Module-6", "./Code/Module-7", "./Code/Module-9"]:
        sys.path.append("%s/" %module)

    import module3_freight_demand
    from module3_freight_demand import *
    import module4_run_traffic_assignment_cpp
    from module4_run_traffic_assignment_cpp import *
    import module5_single_train_simulator
    from module5_single_train_simulator import *
    import module6_calculate_energy_use_backup
    from module6_calculate_energy_use_backup import*
    import module7_func
    from module7_func import*
    import module9_prepare_inputs_backup
    from module9_prepare_inputs_backup import *
    import module9_prepare_outputs
    from module9_prepare_outputs import *
    import module9_prepare_visuals
    from module9_prepare_visuals import *
    import module9_prepare_zip
    from module9_prepare_zip import *
    
    
    st.markdown('## Press the Run button to run the Economic Assessment Tool')
    
    if 'run' not in st.session_state:
        st.session_state.run = 0
    if st.button("▶️ Run"):
        st.session_state.run = 1
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
        
        with open(file_config_output, "w+") as outfile:
         	json.dump(config_input, outfile, indent= '\t')
            
        #############
        ### YEAR LOOP
        #############            
            
        years = list(range(2025, 2035, 5))
        for year in years:
            #dynamic input for module 3
            freight_demand_fraction_change = prcnt_default_edited[(prcnt_default_edited['Year'] == year)]['Proportion'].to_list()[0]
            #prcnt_ffc = edited_ff_red[(edited_ff_red['Year'] == year)]['Coal Reduction Proportion'].to_list()[0]
            #prcnt_ffp = edited_ff_red[(edited_ff_red['Year'] == year)]['Petrolium Reduction Proportion'].to_list()[0]
            
            #ton_year = 'tons' + '_' + str(y)
            st.markdown(f'### Currently running: year = {year}')
            
            ##########################################################################################################             
            ########################################################################################################## 
            
            ############
            ### Module 3
            ############
            start = time.time()
            st.write("Running Module 3: Freight Demand Scenarios")
            coal_reduce = edited_ff_red[(edited_ff_red['Year'] == year)]['Coal Reduction Proportion'].to_list()[0]
            petro_reduce = edited_ff_red[(edited_ff_red['Year'] == year)]['Petrolium Reduction Proportion'].to_list()[0]
            net_flows = module3_freight_demand.create_total_flow(year, st.session_state.freight_demand_scenario, st.session_state.econ_scn,
                                                                 coal_reduce, petro_reduce, freight_demand_fraction_change)
            end = time.time()
            st.write(f"Module 3 is complete. Runtime = {round(end-start,2)} seconds")
            
            # ############
            ### Module 4
            ############
            start = time.time()
            st.write("Running Module 4: Traffic Assignment")
            module4_run_traffic_assignment_cpp.run_traffic_assignment(year)
            end = time.time()
            st.write(f"Module 4 is complete. Runtime = {round(end-start,2)} seconds")
            
            # # ############
            # ### Module 5
            # ############
            start = time.time()
            st.write("Running Module 5: Energy Intensity Matrix")
            #module5_energyintensity_option = input("Enter Option \n\"default\": Ecnonomic Assessment Scenario \n\"force--run\": Create the default look-up table again \n\"custom\": Enter your own AlignmentData and TrainData \n")
            
            module5_single_train_simulator.create_energy_intensity_matrix_sts("default", None, None, None, None)
            end = time.time()
            st.write(f"Module 5 Runtime = {round(end-start,2)} seconds")
            
            # ############
            # ### Module 6
            # ############
            start = time.time()
            st.write("Running Module 6: Calculate Energy Use")
            module6_calculate_energy_use_backup.calculate_energy_use(year = str(year), energy_system_scenario = energy_system_scenario_options.get(st.session_state.energy_system_scenario), 
                                                              freight_demand_scenario = st.session_state.freight_demand_scenario,
                                                              simulator_type=st.session_state.simulator_option,
                                                              factorup = st.session_state.factorup)   
            end = time.time()
            st.write(f"Module 6 is complete. Runtime = {round(end-start,2)} seconds")
            
        #     # # ############
        #     # ### Module 7
        #     # ############
        #     start = time.time()
        #     st.write("Running Module 7")
        #     energy_prices(energy_system_scenario_options.get(st.session_state.energy_system_scenario), renewable_prices, h2_sub,oil_prices)
        #     end = time.time()
        #     st.write(f"Module 7 is complete. Runtime = {round(end-start,2)} seconds")
            
            ############
            ### Module 9
            ############
            start = time.time()
            st.write("Preparing Input Files for Module 9")
            if year == 2025:
                save_mode = "overwrite"
            else:
                save_mode = "append"
            module9_prepare_inputs_backup.prepare_inputs_for_module9(str(year), energy_system_scenario_options.get(st.session_state.energy_system_scenario),\
                                                             st.session_state.freight_demand_scenario, save_mode,st.session_state.renewable_prices,\
                                                             st.session_state.oil_prices, st.session_state.h2_sub)
                
            st.write("Preparing Output Files for Module 9")            
            
        module9_prepare_outputs.module9_economic_assessment(st.session_state.discount_rate,st.session_state.tech_lifetime,st.session_state.contingency_factor)
        end = time.time()
        st.write(f"Module 9 Runtime = {round(end-start,2)} seconds")
        st.write("All Modules Finished")
        st.write("Analysis results created. Go to the results tab")


# %% Download data
with tab4:
    if st.session_state.run == 0:
        st.warning("Run the Simulation First to Download the Outputs")
    elif st.session_state.run == 1:
        module9_prepare_zip.prepare_zip()

# %% Visualize data
with tab5:
    levelized_cost = pd.read_csv("%s/levelized_cost.csv" %module9_output_path)
    if st.session_state.run == 0:
        st.warning("Run the Simulation First to Display the Outputs")
    elif st.session_state.run == 1:
        module9_prepare_visuals.visualize_level_cost(levelized_cost)
with tab6:
    carbon_intensity = pd.read_csv("%s/carbon_intensity.csv" %module9_output_path)
    if st.session_state.run == 0:
        st.warning("Run the Simulation First to Display the Outputs")
    elif st.session_state.run == 1:
        module9_prepare_visuals.visualize_carbon_intensity(carbon_intensity)



    
