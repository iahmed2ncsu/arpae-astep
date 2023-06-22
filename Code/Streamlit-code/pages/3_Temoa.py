# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 11:59:33 2023

@author: Ishtiak
"""

import subprocess
import os
import streamlit as st
import time
url1 = "https://temoacloud.com/" #TEMOA WEBSITE URL
url2 = "https://github.com/TemoaProject/temoa" #TEMOA GITHUB URL
#set page config
st.set_page_config(page_title=None, page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)

st.markdown('## What is TEMOA?')
st.markdown("---")
st.markdown(
        """
        *Tools for Energy Model Optimization and Analysis (Temoa)* is an open source modeling framework for conducting\
        energy system analysis. The core component of Temoa is an energy system optimization model.\
        Such models have emerged as critical tools for technology assessment and policy analysis at scales ranging from\
        local to global. 
        """
        )
st.markdown('The tool and more detailed description are hosted in a separate webiste. Please click the link below\
            to be forwarded to the TEMOA webiste'
            )
st.markdown("##### TEMOA [Link](%s)" % url1)
st.markdown("##### TEMOA Github Repository [Link](%s)" % url2)

