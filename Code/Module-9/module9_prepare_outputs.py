# -*- coding: utf-8 -*-
"""
Created on Mon May  8 14:42:45 2023

@author: Ishtiak
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:07:15 2022

@author: Ishtiak Ahmed；Tongchuan Wei; Rupal Mittal
"""

# description	: The freight rail decarbonization cost model is used to estimate freight rail levelized costs and carbon intensity
#                 for alternative powertrain decarbonization technologies
# version		: 10.1
# python_version: 3.10
# status		: in progress
# updates tried in this version from v6: Completely change the visualization page. Added tooltip info for the visualization elements. It is not complete yet. Also, the options have been capitalized
# and unwanted symbols like _ have been removed.Still needs to add the carbon intensity vis plots
# requirements

import time
from functools import reduce
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt
import base64

#################################
### Input/Output and Static files in repository
#################################

config_input_path = "../Config/user_input.json"
static_input_path = "../Data/Static/"
template_input_path = "../Data/Template/"

module9_input_path = "../Data/Input/Module-9"
module9_output_path = "../Data/Output/Module-9"

def module9_economic_assessment():
    
    df1 = pd.read_csv("%s/traffic_flow_for_Mod9.csv" %module9_input_path)
    df2 = pd.read_csv("%s/train_for_Mod9.csv" %module9_input_path)
    df3 = pd.read_csv("%s/refueling_for_Mod9.csv" %module9_input_path)
    df4 = pd.read_csv("%s/energy_for_Mod9.csv" %module9_input_path)
    df5 = pd.read_csv("%s/energy_price_for_Mod9.csv" %module9_input_path)
    
    df_parameter = pd.read_csv("%s/parameters.csv" %template_input_path)
    
    dfs = [df1, df2, df3, df4, df5]
    df_final = reduce(lambda left, right: pd.merge(left, right, on=['technology', 'region', 'energy_system_scenario',
                                                                    'freight_demand_scenario', 'year']), dfs)
    np_parameter = np.array(df_parameter)
    i = np_parameter[0, 1]  # annual discount rate (percentage point)
    J = np_parameter[1, 1]  # technology lifetime (year)
    c = np_parameter[2, 1]  # contingency factor (%)

    for n in df_final.index:
        LN = df_final.loc[n, 'number_of_locomotives']  # network-level number of locomotive
        TN = df_final.loc[n, 'number_of_tender_cars']  # network-level number of tender cars
        LC = df_final.loc[n, 'cost_per_locomotive ($)']  # locomotive unit cost ($/unit)
        TC = df_final.loc[n, 'cost_per_tender ($)']  # tender car unit cost ($/unit)
        LH = df_final.loc[n, 'locomotive_hours']  # network-level locomotive operational hours (locomotive-hours)
        TH = df_final.loc[n, 'tender_hours']  # network-level tender operational hours (tender-hours)
        LHC = df_final.loc[
            n, 'cost_per_locomotive_hour ($)']  # cost per locomotive operational hours ($/locomotive-hours)
        THC = df_final.loc[n, 'cost_per_tender_hour ($)']  # cost per tender operational hours ($/tender-hours)
        FP = df_final.loc[n, 'energy_price']  # fuel or energy price ($/gallon, $/kg-H2, or $/kWh-e)
        FU = df_final.loc[n, 'train_energy_consumption']  # fuel or energy usage (gallon, kg-H2, or kWh-e)
        RN = df_final.loc[n, 'number_of_charging_stations']  # network-level number of refueling or recharging stations
        RSC = df_final.loc[n, 'cost_per_station ($)']  # refueling or recharging station unit cost ($/unit)
        OMI = df_final.loc[
            n, 'infrastructure_O&M_cost ($/year)']  # infrastructure operation & maintenance cost ($/year)
        TMT = df_final.loc[n, 'freight_ton_mile_travel']  # freignt ton-mile travel (ton-mile/year)
        LTC = (LN * LC + TN * TC + LH * LHC * J + TH * THC * J) / (1 + i) ** J / (
                (TMT * J) / (1 + i) ** J) * 100  # estimate levelized train cost (¢/ton-mile)
        df_final.loc[n, 'levelized_train_cost (cents/ton-mile)'] = LTC
        LFC = FP * FU * J / (1 + i) ** J / ((TMT * J) / (1 + i) ** J) * 100  # estimate levelized fuel cost (¢/ton-mile)
        df_final.loc[n, 'levelized_fuel_cost (cents/ton-mile)'] = LFC
        LIC = (RN * RSC + OMI * J) / (1 + i) ** J / (
                (TMT * J) / (1 + i) ** J) * 100  # estimate levelized infrastructure cost (¢/ton-mile)
        df_final.loc[n, 'levelized_infrastructure_cost (cents/ton-mile)'] = LIC
        LCC = (LTC + LFC + LIC) * c / 100  # estimate levelized contingency cost (¢/ton-mile)
        df_final.loc[n, 'levelized_contingency_cost (cents/ton-mile)'] = LCC
        TLC = LTC + LFC + LIC + LCC  # estimate total levelized cost (¢/ton-mile)
        df_final.loc[n, 'total_levelized_cost (cents/ton-mile)'] = TLC
        CO2U = df_final.loc[
            n, 'upstream_CO2_emission_factor']  # upstream CO2 emission factor (kgCO2/gallon, kgCO2/kg-H2, or kgCO2/kWh-e)
        CO2D = df_final.loc[
            n, 'downstream_CO2_emission_factor']  # downstream CO2 emission factor (kgCO2/gallon, kgCO2/kg-H2, or kgCO2/kWh-e)
        CH4U = df_final.loc[
            n, 'upstream_CH4_emission_factor']  # upstream CH4 emission factor (kgCH4/gallon, kgCH4/kg-H2, or kgCH4/kWh-e)
        CH4D = df_final.loc[
            n, 'downstream_CH4_emission_factor']  # downstream CH4 emission factor (kgCH4/gallon, kgCH4/kg-H2, or kgCH4/kWh-e)
        LCO2 = 1000 * (CO2U + CO2D) * FU * J / (1 + i) ** J / (
                (TMT * J) / (1 + i) ** J)  # estimate levelized CO2 carbon intensity (gCO2/ton-mile)
        df_final.loc[n, 'CO2_carbon_intensity (g CO2/ton-mile)'] = LCO2
        LCH4 = 1000 * (CH4U + CH4D) * FU * J / (1 + i) ** J / (
                (TMT * J) / (1 + i) ** J)  # estimate levelized CH4 carbon intensity (gCH4/ton-mile)
        df_final.loc[n, 'CH4_carbon_intensity (g CH4/ton-mile)'] = LCH4
        if df_final.loc[n, 'technology'] == 'biodiesel':
            LCO2eq = LCO2 + 27.0 * LCH4  # estimate levelized CO2-equivalent carbon intensity based on GWP-100 for CH4-non fossil from IPCC AR6
        else:
            LCO2eq = LCO2 + 29.8 * LCH4  # estimate levelized CO2-equivalent carbon intensity based on GWP-100 for CH4-fossil from IPCC AR6
        df_final.loc[n, 'CO2eq_carbon_intensity (g CO2eq/ton-mile)'] = LCO2eq

    levelized_cost = df_final.drop(df_final.columns[
                                       [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                                        26, 27, 28, 29, 35, 36, 37]], axis=1)
    carbon_intensity = df_final.drop(df_final.columns[5:35],
                                     axis=1)  # drop unnecessary columns for the carbon intensity output file
    
    levelized_cost.to_csv("%s/levelized_cost.csv" %module9_output_path)
    carbon_intensity.to_csv("%s/carbon_intensity.csv" %module9_output_path)
    
    return 0
