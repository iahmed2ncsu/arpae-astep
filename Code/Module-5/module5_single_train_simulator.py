#!/usr/bin/env python
# coding: utf-8

##########
### Import
##########

import os
import numpy as np
import pandas as pd
import subprocess
import streamlit as st

###################
### Paths and Files
###################

# SingleTrainSimulator
path_sts = "../Code/Module-5/SingleTrainSimulator-1/bin/Debug/net6.0/"
file_sts = "SingleTrainSimulator-1.exe"

module5_inputdata_path = "../Data/Input/Module-5"
module5_outputdata_path = "../Data/Output/Module-5" 

#############
### Functions
#############

def run_cmd(args_list):
    """
    run linux commands (copy, put, get, mv -> see examples below)
    """
    
    proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    s_output, s_err = proc.communicate()
    s_return =  proc.returncode
    return s_return, s_output, s_err

def run_sts():
    """
    run the single train simulator
    """
    working_dir = os.getcwd()
    
    # Change the path to STS
    os.chdir(path_sts)

    subprocess.run([file_sts], capture_output=True)
    os.chdir(working_dir)
    
    # Change the path back to workdir
    df_output = pd.read_csv("%s/EnergyInt.txt" %path_sts)
    line = df_output.iloc[0][0]
    column_values = list(line.split())
    column_names = df_output.keys()[0]
    column_names = list(column_names.split())
#     column_names = ["Reg", "Tech", "TrnLen", "TotWrk", "BatAtEnd", "Diesel", "Biodiesel", "Catenary", "Hydrogen", "Battery",\
#                          "Recovered"]
    df_energyint = pd.DataFrame(np.array([column_values]), columns=column_names)

    return(df_energyint)

#######################################################
### Loop through alignment data (9) and Train Data (18)
#######################################################

def create_energy_intensity_matrix_sts(option="default"):

    """
    This function creates the energy_intensity matrix for a given choice of Temoa region, Technology and Train-Length
    
        option: "default" or "custom"
                
                "default" refers to the look-up matrix (162 rows) of energy intensity corresponding to 
                9 Temoa regions (AlignmentData.txt), 6 Technologies and 3 Train-Lengths (TrainData.txt) [9*6*3 = 162]
                
                "custom" refers to the scenario where the user wishes to give their own AlignmentData.txt and TrainData.txt  
                
                The output are columns: Reg, Tech, TrnLen, eTrn, ebtMin, eDie, eBio, eHyd, eBat, eCat, eRcv
    """
    if option=="default":
        print("Energy intensity matrix for the economic assessment scenario already exists. Not computing anything.")
    
    elif option=="force-run":
    
        ###########
        ### Mapping
        ###########

        tech_dict = {1: "Diesel",
                     2: "BioDie",
                     3: "DieHyb",
                     4: "BioHyb",
                     5: "HydHyb",
                     6: "Bat"}

        train_length_dict = {1: "50 Cars",
                  2: "100 Cars",
                  3: "150 Cars"}

        region_dict = {1: "CA",
                    2: "CEN",
                    3: "MID_AT",
                    4: "N_CEN",
                    5: "NE",
                    6: "NW",
                    7: "SE",
                    8: "SW",
                    9: "TX"}   

        #########
        ### Loops
        #########    
        df_result = None

        region = 0 
        for region in range (1, 10):

            alignmentdata_file = r"AlignmentData_%d.txt" %(region)
            (ret, out, err)= run_cmd(["cp", "%s/%s" %(module5_inputdata_path, alignmentdata_file), "%s/AlignmentData.txt" %(path_sts)])
            print(region)

            for tech in range(1, 7):
                for train_length in range(1, 4):

                    traindata_file = r"TrainData_%d%d.txt" %(tech, train_length)

                    (ret, out, err)= run_cmd(["cp", "%s/%s" %(module5_inputdata_path, traindata_file), "%s/TrainData.txt" %(path_sts)])

                    #print("AlignmentData_%d.txt" %(region), "%s/%s" %(module5_inputdata_path, traindata_file), "%s/TrainData.txt" %(path_sts))

                    df_energyint = run_sts()
                    df_energyint["Reg"]=region_dict[region]
                    df_energyint["Tech"]=tech_dict[tech]
                    df_energyint["TrnLen"] = train_length_dict[train_length]

                    df_result = pd.concat([df_result, df_energyint])

        df_result.to_csv("%s/EnergyIntensity_Matrix.csv " %(module5_outputdata_path), index=False)

    elif option=="custom":
        
        uploaded_alignment_data = st.file_uploader("Enter Alignment Data \n Please copy and paste the following as the header and provide columns that adhere to it: \nDist(mi)        SpdLim(mph)     Grade(%)        Curve(Doc)      Catenary(Y/N)")
        df_alignment = pd.read_csv(uploaded_alignment_data)
        df_alignment.to_csv("%s/AlignmentData.txt" %(path_sts))
        
        uploaded_train_data = st.file_uploader("Enter Train Data \n Please copy and paste the following as the header and provide columns that adhere to it: \nUnit No \"Type (1,11)\"   Weight(ton)     Len(ft) Axles(n)        aRes    bRes    cRes    eInit(Mwh)      teMax (kips)    ptMax (kw)        catMax (kw)     batMax (kw)     auxMax (kw)     rbMax (kw)      dbMax (kw)")
        df_train = pd.read_csv(uploaded_train_data)
        df_train.to_csv("%s/TrainData.txt" %(path_sts))
        
        df_energyint = run_sts()
        
        df_energyint["Reg"]= input("Enter Region")
        df_energyint["Tech"]= input("Enter Technology")
        df_energyint["TrnLen"] =input("Enter TrainLength (default 1)")

        df_result = df_energyint

        df_result.to_csv("%s/EnergyIntensity_Matrix_Custom.csv " %(module5_outputdata_path), index=False)
        
    



