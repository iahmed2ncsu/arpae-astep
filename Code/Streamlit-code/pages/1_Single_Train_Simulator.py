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
tab1, tab2,tab3 = st.tabs(["About", "Input","Run Single Train Simulator"])

