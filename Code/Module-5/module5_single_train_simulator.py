#!/usr/bin/env python
# coding: utf-8

##########
### Import
##########

import os
from sys import platform
import pandas as pd
import subprocess
import streamlit as st

###################
### Paths and Files
###################

# SingleTrainSimulator
path_sts = "./Code/Module-5/SingleTrainSimulator-1/"

if platform == "win32":
    file_sts = "SingleTrainSimulator-1.exe"
else:
    file_sts = "linux/SingleTrainSim"

#file_sts = "SingleTrainSimulator-1.exe"

module5_input_path = "./Data/Input/Module-5"
module5_output_path = "./Data/Output/Module-5" 

module5_input_winpath = "./Data/Input/Module-5"
winpath_sts = "./Code/Module-5/SingleTrainSimulator-1"

#############
### Functions
#############

def run_cmd(args_list):
    """
    run linux commands (copy, put, get, mv -> see examples below)
    """
    print('Running system command: {0}'.format(' '.join(args_list)))
    proc = subprocess.Popen(args_list, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_output, s_err = proc.communicate()
    s_return =  proc.returncode
    return s_return, s_output, s_err

###################################
### Run the Single Train Simulator
###################################

def run_sts(choice,reg,tech):
    """
    run the single train simulator
    """
    st.write("Running the STS")
    print(choice,reg,tech)

    # Save the working directory
    working_dir = os.getcwd()
    
    # Change the path to STS
    os.chdir(path_sts)

    # Change RunSpecs.csv
    file = open("./RunSpecs.csv", "w")
    file.write("Region,Tech,Detail(Y/N)\n")
    if choice=="single":
        file.write(reg+","+tech+","+"1")
    else:
        file.write(reg+","+tech+","+"0")
    file.close()
    
    # Run the Single-Train-Simulator
    subprocess.run([file_sts], capture_output=True)
    
    # Change the path back to workdir
    os.chdir(working_dir)

###########################################################
### Run the STS based on the option input - 3 possibilities
###########################################################

def create_energy_intensity_matrix_sts(option, uploaded_alignment_data, uploaded_train_data, region, technology):

    """
    This function creates energy_intensity matrices for single or multiple runs of the STS
    
        options:"default", "single" or "many"

                "default" refers to doing nothing, where it is called by EcoTool
                
                "single" refers to the scenario where the user gives one AlignmentData.txt and one TrainData.txt  
                
                "many" refers to where the user wants to create an entire new look-up matrix (162 rows) 
                 of energy intensity corresponding to 9 Temoa regions (AlignmentData.txt), 6 Technologies 
                 and 3 Train-Lengths (TrainData.txt) [9*6*3 = 162]
                
                The output are columns: Reg, Tech, TrnLen, eTrn, BatAtEnd, eDie, eBio, eHyd, eBat, eCat, eRcv
    """
    print(option)
    print(region)
    print(technology)

    if option=="default":
        print("Energy intensity matrix for the economic assessment scenario already exists. Not computing anything.")
       
    elif option=="single":
        
        st.write("Simulating single train and alignment.")
        st.write("Uploading alignment data")
        df_alignment = pd.read_csv(uploaded_alignment_data)
        df_alignment.to_csv("%s/AlignmentData.csv" %(path_sts), index=None)
        
        st.write("Uploading train data")
        df_train = pd.read_csv(uploaded_train_data)
        df_train.to_csv("%s/TrainData.csv" %(path_sts), index=None)
        
        df_energyint = run_sts(option,region,technology)
       
    elif option=="many":
            
        ###########
        ### Mapping
        ###########
        
        P_nc = [0.3, 0.6, 0.1] # Percentage share of tonmiles for train lengths 50, 100, 150

        tech_dict = {1: "Diesel",
                     2: "BioDie",
                     3: "DieHyb",
                     4: "BioHyb",
                     5: "HydHyb",
                     6: "Battery",
                     7: "Mixed",
                     8: "Other"}

        region_dict = {1: "CA",
                       2: "CEN",
                       3: "MID_AT",
                       4: "N_CEN",
                       5: "NE",
                       6: "NW",
                       7: "SE",
                       8: "SW",
                       9: "TX",
                      10: "US",   
                      11: "OTHER"}   

        #########
        ### Loops
        #########    
        
        df_result = None

        region = 0 
        
        for region in range (1, 10):

            alignmentdata_file = "AlignmentData_%d.txt" %(region)
            (ret, out, err)= run_cmd(["copy", "%s\\%s" %(module5_input_winpath, alignmentdata_file), "%s\\AlignmentData.txt" %(winpath_sts)])

            for tech in range(1, 7):
                for train_length in range(1, 4):
                    print(region, tech, train_length)
                    traindata_file = "TrainData_%d%d.txt" %(tech, train_length)

                    (ret, out, err)= run_cmd(["copy", "%s\\%s" %(module5_input_winpath, traindata_file), "%s\\TrainData.txt" %(winpath_sts)])
                    df_energyint = run_sts(option,region,tech)
                    df_energyint["Reg"]=region_dict[region]
                    df_energyint["Tech"]=tech_dict[tech]
                    df_energyint["trnLen"] = train_length_dict[train_length]

                    df_result = pd.concat([df_result, df_energyint])

        df_result = df_result[["Reg", "Tech", "trnLen", "eDie", "eBio", "eHyd", "eBat", "eCat"]]
        df_result.to_csv("%s/EnergyIntensity_Matrix_STS_wTrnLn.csv" %(module5_output_path), index=False)
        
        ### Combine the Trainlengths
        energy_intensity = pd.read_csv("%s/EnergyIntensity_Matrix_STS_wTrnLn.csv" %(module5_output_path))

        energy_intensity_grouped = pd.DataFrame()
        for i, group in energy_intensity.groupby(["Reg", "Tech"]):
            index_cols = group.iloc[0, :2]
            data_cols = group.iloc[:, 3:]
            data_cols = data_cols.T * P_nc
            data_cols = data_cols.sum(axis=1)
            energy_intensity_grouped = pd.concat([energy_intensity_grouped, pd.concat([index_cols, data_cols])], axis=1)

        energy_intensity_grouped = energy_intensity_grouped.T.reset_index(drop=True)#.drop(columns=["ebtMin", "eTrn", "eRcv"])
        energy_intensity_grouped = energy_intensity_grouped.rename(columns={"eDie": "Diesel", "eBio": "BioDie", "eHyd": "Hyd", \
                                                                    "eBat": "Bat", "eCat": "Cat"})#[["Reg", "Tech", "Diesel", "BioDie", "Hyd", "Cat", "Bat"]]

        energy_intensity_grouped.to_csv("%s/EnergyIntensity_Matrix_STS_many.csv " %(module5_output_path), index=False)


