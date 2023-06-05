### The following code can be invoked to run the Traffic Assignment Module"

__author__ = "Dr Rupal Mittal, Andreas Weiss"
__email__ = "Rupal.Mittal@deutschebahn.com, Andreas.AJ.Weiss@deutschebahn.com"
__status__ = "Development"

##########
### Import
##########

import subprocess
import os
import pandas as pd
import time
import streamlit as st
import sys

###################
### Paths and Files
###################
    
# Output path
module4_output_path = "./Data/Output/Module-4"

# TrafAssign
#path_trafassign = "./Module-4/TrafAssign/out/build/x64-debug"
path_trafassign = "./Code/Module-4/TrafAssign/"
file_trafassign = "TrafAssign.exe"

# Links data path
static_input_path = "./Data/Static"

file_links = "links.txt"
path_links = "%s/%s" %(static_input_path, file_links)

#file_temoa_state = "temoa_state_mapping.csv"

file_lkflows = "lkflow.txt"
path_lkflows = "%s/%s" %(path_trafassign, file_lkflows)

# file_lkflows = "lkflow_TA_PopShift_2020-v7-Mod4b.txt"
# path_lkflows = "%s/%s" %(static_input_path, file_lkflows)
#path = /app/arpae-astep
#############
### Functions
#############

def run_traffic_assignment(year):
    """
    Create lkflow, lkflows and tm_per_temoa.
    
        Keyword arguments:
            years -> Analysis years (numeric)
    
        Output:
            lkflow -> output of TrafAssign.exe, which is tonnes by link and direction
            lkflows -> tonnes to tonne-miles
            tm_per_temoa -> tonne-miles per Temoa region
            grade_per_temoa, curvature_per_temoa -> Further Outputs
    """
    start = time.time()

    ###########################################
    ### Create lkflow, lkflows and tm_per_temoa
    ###########################################
    
    ### Run TrafAssign.exe C++ code to assign net ton flows by link and direction
    working_dir = os.getcwd()
    st.write(os.getcwd())
    os.chdir(path_trafassign)
    st.write(os.getcwd())
#     files_to_be_removed = ["nodes.txt", "zones.txt", "lkflow.txt", "xtime.txt"]
#     st.write("Module4: Removing files %s from the TrafAssign folder" %files_to_be_removed)
#     for file in files_to_be_removed:
#         if os.path.exists(file):
#             os.remove(file)
    subprocess.run([f"{sys.executable}", file_trafassign], capture_output=True)
    os.chdir(working_dir)
    ### Get TrafAssign output files and convert to .csv, delimiter ","
    ### Only carried out for lkflows, remaining files not required

    lkflows = pd.read_csv(path_lkflows, sep="\t", header=None).drop(columns=0)
    lkflows.columns = ["tnc_AB (k)", "tnc_BA (k)"]

    links = pd.read_csv(path_links)

    lkflows = links.loc[:, ["MyLkID", "ST_MILES", "TEMOA"]].merge(lkflows, left_on="MyLkID", right_index=True)
    lkflows["tnc_TOT (k)"] = lkflows["tnc_AB (k)"] + lkflows["tnc_BA (k)"]
    lkflows["TMc_e (M)"] = lkflows["tnc_TOT (k)"] * lkflows["ST_MILES"] / 1000

    # Calculate Ton-Miles per Temoa region
    tm_per_temoa = lkflows.groupby("TEMOA").sum()   
       
    #######################    
    ### Grade and Curvature
    #######################
    
    ### Calculate % use miles weighted by TM by grade/curvature per Temoa region
    
    grades = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 140] # TODO: Create input parameter for grades ft/mi
    curvatures = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2 ,2.4, 2.6, 16.0] # TODO: Create input parameter for curvatures %/mi
    grade_curvature = lkflows.merge(links.loc[:, ["AB_FT_GAIN", "BA_FT_GAIN", "DoC_Avg"]], left_index=True, right_index=True)
    grade_curvature["μg_AB"] = grade_curvature["AB_FT_GAIN"]/grade_curvature["ST_MILES"]
    grade_curvature["μg_BA"] = grade_curvature["BA_FT_GAIN"]/grade_curvature["ST_MILES"]

    ### Calculate % use miles weighted by TM by grade
    
    grade_per_temoa_list = []
    for direction in ["μg_AB", "μg_BA"]:
        grade_list = []
        for grade in grades:
            temp = grade_curvature[grade_curvature[direction] <= grade].groupby("TEMOA")["TMc_e (M)"].sum()
            temp.name = grade
            grade_list.append(temp)
        grade_per_temoa = pd.DataFrame(grade_list)
        grade_per_temoa = (grade_per_temoa - grade_per_temoa.shift(1).fillna(0)) / grade_per_temoa.iloc[-1]
        grade_per_temoa = grade_per_temoa.reset_index().rename(columns={"index":"ft/mi"})
        grade_per_temoa["direction"] = direction[-2:]
        grade_per_temoa_list.append(grade_per_temoa)
    grade_per_temoa = pd.concat(grade_per_temoa_list)

    ### Calculate % use miles weighted by TM by curvature
    
    curvature_list = []
    for curvature in curvatures:
        temp = grade_curvature[grade_curvature["DoC_Avg"] <= curvature].groupby("TEMOA")["TMc_e (M)"].sum()
        temp.name = curvature
        curvature_list.append(temp)
    curvature_per_temoa = pd.DataFrame(curvature_list)
    curvature_per_temoa = (curvature_per_temoa - curvature_per_temoa.shift(1).fillna(0)) / curvature_per_temoa.iloc[-1]
    curvature_per_temoa = curvature_per_temoa.reset_index().rename(columns={"index":"avgDoC"})

    ###################
    ### Add year Column
    ###################
    
    for dataframe in [tm_per_temoa, lkflows, grade_per_temoa, curvature_per_temoa]:
        dataframe["year"] = year    
        first_column = dataframe.pop("year")
        dataframe.insert(0, "year", first_column)
    
    ################
    ### Save outputs
    ################
    
    tm_per_temoa = tm_per_temoa.drop(columns=['MyLkID', 'tnc_AB (k)', 'tnc_BA (k)']).reset_index()
    #tm_per_temoa.to_csv("%s/tm_per_temoa.csv" %module4_output_path, index=False)

    lkflows = lkflows.drop(columns=["ST_MILES", "TEMOA"])
    #lkflows.to_csv("%s/lkflows.csv" %module4_output_path , index=False)

    #grade_per_temoa.to_csv("%s/grade_bins_per_temoa.csv" %module4_output_path , index=False)
    #curvature_per_temoa.to_csv("%s/curvature_bins_per_temoa.csv" %module4_output_path , index=False)
    
    end = time.time()
    print(f"Run time for Module_4 = {round(end-start,ndigits = 2)} seconds")
    
    return 0
