# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 19:14:46 2022

@author: Ishtiak
"""

import streamlit as st
from PIL import Image
import os

#st.markdown("# Welcome page")

page_title = "A-STEP: Achieving Sustainable Train Energy Pathways"
body = " Multi-decadal Decarbonization Pathways for U.S. Freight Rail"

st.set_page_config(layout = 'wide')
st.sidebar.markdown("# Welcome page")
st.header(body)

direct = "Code/Streamlit-code/"
#Read hard-coded image files
image1 = Image.open(f"{direct}astep_image.png")
image2 = Image.open(f"{direct}logo.png")
image3 = Image.open(f"{direct}blockDiagram.png")
#st.image(image2)
col1,col2 = st.columns((1,2.5))

col1.image(image1, use_column_width=True)
col2.markdown('## A-STEP')
col2.markdown("### 🚆 Achieving Sustainable Train Energy Pathways")
col2.markdown("#### Sponsored by ARPA-e")
#col2.markdown("### Prepared by:")

st.markdown("---")

st.markdown(
    """
    ### Introduction
    *A-STEP* is a first-of-its-kind, integrated, open-source software tool aimed at guiding freight rail 
    decarbonization decision-making. It starts from energy pathways and economic forecasts and progresses 
    through traffic assignment, energy intensity analysis, recharging facility assessment, and cost 
    estimation to produce results that can help with decarbonization feasibility assessments. 
    Technological evolution and least-cost capacity expansion form the basis for estimating levelized costs 
    for this energy sourcing transformation, enabling the assessment of benefits and costs for decarbonization options."""
)
left_col, right_col = st.columns([1.5, 1])
right_col.image(image3, output_format="PNG")

left_col.markdown(
    """
    ### Module Description

    The figure on the right shows the logic and data flow for A-STEP. To the left, is a dropdown main menu for navigating to 
    each module:

    - **Welcome Page:** We are here!
    - **Economic Assessment Tool:** A pipeline consisting of nine modules as listed below:
        - **Module 1 - Decarbonization Pathway:** To select an economy-wide decarbonization energy pathway.
        - **Module 2 - Economic Scenario:** To select an economic scenario, like high economic growth in combination 
        with population migration to the southeastern and southwestern areas of the US.
        - **Module 3 - Freight Demands:** Estimates freight demands consistent with the above assumptions.
        - **Module 4 - Traffic Assignment:** Assigns the origin-to-destination tonnage flows from Step 3 to links (by direction)
        on the national rail network.
        - **Module 5 - Train Simulator:** Simulates of train movements, using either or both a single train simulator and a network, 
        multi-train simulator, provide estimates of energy intensity (MWh/ton-mile) for the regions of the US
        - **Module 6 - Energy Use by Types and Regions:** Combines energy intensities with the regional traffic activity from Step 4 
        to create estimates of energy use by type for each of the regions. It also produces estimates of charging station energy demands
        by location (presently nearly 800 railroad yards and intermodal terminals).
        - **Module 7 - Energy Prices:** Provides relationships between energy demand (MWh/day) and energy price ($/MWh) for each of the regions based on 
        the decarbonization pathway being studied.
        - **Module 8 - Recharging Facilities:** Takes the energy demands from Module 6 (the charging station energy demands), the pricing from Module 7, 
        and the pass-through rail activity from Module 4 to develop estimates of the recharging facility requirements needed 
        (recharge facilities sizes by location and energy type, and locomotive and energy tender fleet sizes).
        - **Module 9 - Probabilistic Costs:** Estimates costs, for the recharging facility investments identified in Module 8, the unit costs from Module 7,
        and the incremental changes in rail system configuration, like locomotive investments and conversions from Module 4,
        to develop total and levelized costs for the decarbonization / economic future combination being examined.
    - **Single Train Simulator:** Standalone version of a single train simulator.
    - **Multi-train Simulator:** Standalone version of a single train simulator.
    - **TEMOA:** Standalone Tools for Energy Model Optimization and Analysis (Link).
    - **Recharging Facility Assessment:** Standalone Recharging Facility Assessment tool.
    """
)


