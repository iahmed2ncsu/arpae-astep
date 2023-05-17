# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 11:59:33 2023

@author: Ishtiak
"""

import subprocess
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

path = os.path.abspath('../../Code/Module-5/NeTrainSim')#this is where the NeTrainSim program is installed. Download the file from\
    #https://github.com/AhmedAredah/NeTrainSim and install at the default directory
file = r"NeTrainSim.exe"
in_path = os.path.abspath("../../Data/Static")
out = os.path.abspath("../../Data/Output/Module-5")
# %% About page
#page_title = "A-STEP: Achieving Sustainable Train Energy Pathways"
body = "A-STEP: Achieving Sustainable Train Energy Pathways"
subhead = "Module 5m: Network Simulator (aka NeTrainSim)"

with tab1:
    #st.set_page_config(page_title=page_title)
    st.header(body)
    st.subheader(subhead)
    st.write(os.getcwd())
    st.write(in_path)
    st.write(out)
    st.write(path)

# %% Input
with tab2:
    st.title("Inputs")
    train = st.file_uploader("Upload your input Train Consist file", type=["DAT"])
    link = st.file_uploader("Upload your input Link file", type=["DAT"]) 
    node = st.file_uploader("Upload your input Node file", type=["DAT"]) 
    if st.button("Submit All Data"):
        with open(out+ r"/" + train.name,"wb") as f1:
            f1.write(train.getbuffer()) 
        with open(out+ r"/" + link.name,"wb") as f2:
            f2.write(link.getbuffer())
        with open(out+ r"/" + node.name,"wb") as f3:
            f3.write(node.getbuffer())

# %% Simulation run page
with tab3:
    st.title("Run Module")
    
    @st.experimental_memo()
    def computation():
        start = time.time()
        #os.chdir(path)
        subprocess.run([path + "/" + file,
                        "-n",out+ r"/" + node.name+ r".dat",                        
                        "-t",out+ r"/" + train.name+ r".dat",
                        "-l",out+ r"/" + link.name+ r".dat",
                        "-e","true",
                        "-o",out],
                       capture_output=True)
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
       
