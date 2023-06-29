# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 11:59:33 2023

@author: Ishtiak
"""

import subprocess
from sys import platform
import os
import streamlit as st
import time

#set page config
st.set_page_config(page_title=None, page_icon=None, 
                   #layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)

#define tab names and numbers
tab1, tab2,tab3 = st.tabs(["About", "Input","Run NeTrainSim"])
# %% dataframe conversion function
#this function converts the output data to utf-8 encoded data. 
#It is important in order to download the outputs
@st.cache
def convert_df(df):
    
   return df.to_csv().encode('utf-8')
# %% Read hard-coded files

path = os.path.abspath('./Code/Module-5/NeTrainSim')#this is where the NeTrainSim program is installed. Download the file from\
    #https://github.com/AhmedAredah/NeTrainSim and install at the default directory
file = r"NeTrainSim.exe"
if platform == "linux":
    file = r"NeTrainSim"
in_path = os.path.abspath("./Data/Static")
inputFiles = os.path.abspath("./Data/Input/Module-5")
outputFiles = os.path.abspath("./Data/Output/Module-5")

# %% About page
page_title = "A-STEP: Achieving Sustainable Train Energy Pathways"
body = "A-STEP: Achieving Sustainable Train Energy Pathways"
subhead = "Multi-Train / Network Simulator (aka NeTrainSim)"

with tab1:
    #st.set_page_config(layout='wide')
    #st.set_page_config(page_title=page_title)
    st.header(body)
    st.subheader(subhead)
    # %% st.write(os.getcwd())
    # %% st.write(in_path)
    # %% st.write(out)
    # %% st.write(path)

    st.markdown(
    """The Network Multi-Train Simulator (NeTrainSim v0.0.8 beta) is a software application designed to simulate the movement and interactions of multiple trains within a graph-based network, where points are connected by links, and signals are placed only at the intersection of these links. The simulator analyzes the network and trains’ paths to identify potential collisions and resolves them on a first-come, first-served basis by adjusting the network signals state. Additionally, the simulator considers train following, train dynamics, and external resistance.

The simulator operates on a time-driven algorithm utilizing a time step as the base for the calculations. It is recommended to use a small-time step to minimize errors in the simulation results. The algorithm progresses through each time step, updating the positions and states of the trains and analyzing their interactions within the network. At the end of the simulation, a summary file is generated with the key information about the trains’ performance. The summary file includes details such as travel time, traveled distance, and consumed energy. 

The energy consumption model considers different train consists, each with its own locomotive characteristics and power type. The model accommodates various energy sources, including diesel, biodiesel, diesel-hybrid, biodiesel-hybrid, and electric trains.

NeTrainSim offers a comprehensive simulation environment for analyzing the behavior of multiple trains on a network. Its modular structure allows for the efficient handling of network calculations, train dynamics, and energy consumption calculations, providing accurate and detailed simulation results.""")

# %% Input
with tab2:
    st.title("Inputs")
    train = st.file_uploader("Upload your input Train Consist file", type=["DAT"])
    link = st.file_uploader("Upload your input Link file", type=["DAT"]) 
    node = st.file_uploader("Upload your input Node file", type=["DAT"]) 
    if st.button("Submit All Data"):
        print(train.name)
        with open(inputFiles+ r"/" + train.name,"wb") as f1:
            f1.write(train.getbuffer()) 
        with open(inputFiles+ r"/" + link.name,"wb") as f2:
            f2.write(link.getbuffer())
        with open(inputFiles+ r"/" + node.name,"wb") as f3:
            f3.write(node.getbuffer())

# %% Simulation run page
with tab3:
    st.title("Run Module")
    
    # %% @st.experimental_memo()
    def computation():
        start = time.time()
        #os.chdir(path)
        subprocess.run([path + "/" + file,
                        "-n",inputFiles+ r"/" + node.name,                        
                        "-t",inputFiles+ r"/" + train.name,
                        "-l",inputFiles+ r"/" + link.name,
                        "-e","true",
                        "-a", "true",
                        "-o",outputFiles],
                       capture_output=False)
        end = time.time()
        return start,end
    
    if 'run5m' not in st.session_state:
         st.session_state.run5m = 0  
    
    run5m = st.button('▶️ Press to run the simulation')
    if run5m:
        st.session_state.run5m = 1
    if st.session_state.run5m == 1:  
        start,end = computation()
        st.info(
           f"Run time = {round(end-start,ndigits = 2)} seconds"
        )
       
