# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:07:15 2022

@author: Ishtiak；Tongchuan
"""

# description	: The freight rail decarbonization cost model is used to estimate freight rail levelized costs and carbon intensity
#                 for alternative powertrain decarbonization technologies
# version		: 10.1
# python_version: 3.10
# status		: in progress
# updates tried in this version from v6: Completely change the visualization page. Added tooltip info for the visualization elements. It is not complete yet. Also, the options have been capitalized
# and unwanted symbols like _ have been removed.Still needs to add the carbon intensity vis plots
# requirements
from functools import reduce
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

#################################
### Input/Output and Static files in repository
#################################

module9_input_path = "./Data/Input/Module-9"
df1 = pd.read_csv("%s/traffic_flow_for_Mod9.csv" %module9_input_path)
df2 = pd.read_csv("%s/train_for_Mod9.csv" %module9_input_path)
df3 = pd.read_csv("%s/refueling_for_Mod9.csv" %module9_input_path)
df4 = pd.read_csv("%s/energy_for_Mod9.csv" %module9_input_path)
df5 = pd.read_csv("%s/energy_price_for_Mod9.csv" %module9_input_path)
# %% dataframe conversion function
# this function converts the output data to utf-8 encoded data. It is important to download the outputs
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# %% visualization function
def bar_ploth(df, yaxis, ylab):
    # the output is in wide data format. Tidy it to long
    df_long = pd.melt(df, id_vars=yaxis, value_vars=["levelized_fuel_cost (cents/ton-mile)",
                                                     'levelized_infrastructure_cost (cents/ton-mile)',
                                                     'levelized_contingency_cost (cents/ton-mile)',
                                                     'levelized_train_cost (cents/ton-mile)'])
    fig = px.bar(df_long, y=yaxis,
                 x='value',
                 color='variable',
                 labels={'value': "Levelized Cost (cents/ton-mile)", yaxis: ylab},
                 title=f"Levelized Cost Variation by {ylab} (Figure)")
    # to change the legend key, first create a dictionary of the existing and the desired names
    newnames = {'levelized_fuel_cost (cents/ton-mile)': 'Fuel',
                'levelized_infrastructure_cost (cents/ton-mile)': 'Infrastructure',
                'levelized_contingency_cost (cents/ton-mile)': "Contingency",
                'levelized_train_cost (cents/ton-mile)': 'Train'}
    # the following
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                          legendgroup=newnames[t.name],
                                          hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])
                                          )
                       )

    st.plotly_chart(fig, use_container_width=True)


# vertical bar plot
def bar_plotv(df, yaxis, ylab):
    # the output is in wide data format. Tidy it to long
    df_long = pd.melt(df, id_vars=yaxis, value_vars=["levelized_fuel_cost (cents/ton-mile)",
                                                     'levelized_infrastructure_cost (cents/ton-mile)',
                                                     'levelized_contingency_cost (cents/ton-mile)',
                                                     'levelized_train_cost (cents/ton-mile)'])
    fig = px.bar(df_long, x=yaxis,
                 y='value',
                 color='variable',
                 labels={'value': "Levelized Cost (cents/ton-mile)", yaxis: ylab},
                 title=f"Levelized Cost Variation by {ylab} (Figure)")
    # to change the legend key, first create a dictionary of the existing and the desired names
    newnames = {'levelized_fuel_cost (cents/ton-mile)': 'Fuel',
                'levelized_infrastructure_cost (cents/ton-mile)': 'Infrastructure',
                'levelized_contingency_cost (cents/ton-mile)': "Contingency",
                'levelized_train_cost (cents/ton-mile)': 'Train'}
    # the following
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                          legendgroup=newnames[t.name],
                                          hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])
                                          )
                       )
    # Manually set the tick values for the axis
    fig.update_layout(xaxis={'tickmode': 'array', 'tickvals': df[yaxis].unique()})
    st.plotly_chart(fig, use_container_width=True)


# this function takes the region/yearly/techno carbon intensity, yaxis value, and the desired
# y axis title for the output visualization page.
# horizontal bar plot
def C_bar_ploth(df, yaxis, ylab):
    # the output is in wide data format. Tidy it to long
    df_long = pd.melt(df, id_vars=yaxis, value_vars=["CO2_carbon_intensity (g CO2/ton-mile)",
                                                     'CH4_carbon_intensity (g CH4/ton-mile)'])
    fig = px.bar(df_long, y=yaxis,
                 x='value',
                 color='variable',
                 labels={'value': "Carbon Intensity (g CO2 eq/ton-mile)", yaxis: ylab},
                 title=f"Carbon Intensity Variation by {ylab} (Figure)")
    # to change the legend key, first create a dictionary of the existing and the desired names
    newnames = {'CO2_carbon_intensity (g CO2/ton-mile)': 'CO2', 'CH4_carbon_intensity (g CH4/ton-mile)': 'CH4'}
    # the following
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                          legendgroup=newnames[t.name],
                                          hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])
                                          )
                       )

    st.plotly_chart(fig, use_container_width=True)


# vertical bar plot
def C_bar_plotv(df, yaxis, ylab):
    # the output is in wide data format. Tidy it to long
    df_long = pd.melt(df, id_vars=yaxis, value_vars=["CO2_carbon_intensity (g CO2/ton-mile)",
                                                     'CH4_carbon_intensity (g CH4/ton-mile)'])
    fig = px.bar(df_long, x=yaxis,
                 y='value',
                 color='variable',
                 labels={'value': "Carbon Intensity (g CO2 eq/ton-mile)", yaxis: ylab},
                 title=f"Carbon Intensity Variation by {ylab} (Figure)")
    # to change the legend key, first create a dictionary of the existing and the desired names
    newnames = {'CO2_carbon_intensity (g CO2/ton-mile)': 'CO2', 'CH4_carbon_intensity (g CH4/ton-mile)': 'CH4'}
    # the following
    fig.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                          legendgroup=newnames[t.name],
                                          hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])
                                          )
                       )
    # Manually set the tick values for the axis
    fig.update_layout(xaxis={'tickmode': 'array', 'tickvals': df[yaxis].unique()})
    st.plotly_chart(fig, use_container_width=True)
    
# define triangular distribution
def triangle_distribution(minimum, mode, maximum, size):
    if minimum == maximum:
        return minimum
    else:
        return np.random.triangular(minimum, mode, maximum, size)
# Set the number of Monte Carlo simulations
n_sims = 10000


# %%levelized cost function
def visualize_level_cost(levelized_cost):
    st.title("Visualize levelized cost outputs")
    col1, col2 = st.columns(2)
    if st.session_state.run == 0:
        st.warning("Run the Simulation First to Display Outputs")
    elif st.session_state.run == 1:
        with col1:
            st.subheader("Plot levelized cost outputs")
            option_costplot = st.selectbox(label="Choose a graph", options=("None", "Cost by Regions", "Cost by Technologies", "Cost by Years"))
            levelized_cost['year'] = levelized_cost['year'].astype(str)
            st.write(levelized_cost)
            if option_costplot == "Cost by Regions":
                # inputs for the first plot: Region vs cost
                # ener_sc1 = st.selectbox('Select energy system scenario',
                #                         options=levelized_cost.energy_system_scenario.unique(), help="Dummy tooltip",
                #                         key=11, format_func=lambda x: (x.replace('_', ' ')).title())
                # freight_sc1 = st.selectbox('Select freight demand scenario',
                #                            options=levelized_cost.freight_demand_scenario.unique(),
                #                            help="Dummy tooltip", key=12,
                #                            format_func=lambda x: (x.replace('_', ' ')).title())
                tech_sc1 = st.selectbox('Select power train technology', options=levelized_cost.technology.unique(),
                                        help="Dummy tooltip", key=13,
                                        format_func=lambda x: (x.replace('_', ' ')).title())
                year_sc1 = st.selectbox('Select year', options=levelized_cost.year.unique(), help="Dummy tooltip",
                                        key=14)
                region_cost = levelized_cost[
                    #(levelized_cost.energy_system_scenario == ener_sc1) &  # select energy system scenario
                    #(levelized_cost.freight_demand_scenario == freight_sc1) &  # select freight demand scenario
                    (levelized_cost.technology == tech_sc1) &  # select technology
                    (levelized_cost.year == year_sc1)  # select year
                    ]
                bar_ploth(region_cost, "region", "Regions")
                # st.write("Levelized Cost Variation by Regions (Table)")
                # st.write(region_cost)
                
            elif option_costplot == "Cost by Technologies":
                # inputs for the second plot: cost vs technology
                # ener_sc2 = st.selectbox('Select energy system scenario',
                #                         options=levelized_cost.energy_system_scenario.unique(), help="Dummy tooltip",
                #                         key=21, format_func=lambda x: (x.replace('_', ' ')).title())
                # freight_sc2 = st.selectbox('Select freight demand scenario',
                #                            options=levelized_cost.freight_demand_scenario.unique(),
                #                            help="Dummy tooltip", key=22,
                #                            format_func=lambda x: (x.replace('_', ' ')).title())
                reg_sc2 = st.selectbox('Select region', options=levelized_cost.region.unique(), help="Dummy tooltip",
                                       key=23, format_func=lambda x: (x.replace('_', ' ')).title())
                year_sc2 = st.selectbox('Select year', options=levelized_cost.year.unique(), help="Dummy tooltip",
                                        key=24)
                tech_cost = levelized_cost[
                    #(levelized_cost.energy_system_scenario == ener_sc2) &  # select energy system scenario
                    #(levelized_cost.freight_demand_scenario == freight_sc2) &  # select freight demand scenario
                    (levelized_cost.region == reg_sc2) &  # select region
                    (levelized_cost.year == year_sc2)  # select year
                    ]
                bar_plotv(tech_cost, 'technology', "Technology")
                
            elif option_costplot == "Cost by Years":
                # inputs for the third plot: cost vs Years
                # ener_sc3 = st.selectbox('Select energy system scenario',
                #                         options=levelized_cost.energy_system_scenario.unique(),
                #                         help="Business As Usual means no new federal policies \n\n50% reduction by 2050 means___\n\nNet zero by 2050 means__",
                #                         key=31, format_func=lambda x: (x.replace('_', ' ')).title())
                # # the last part, i.e., format function is to remove underscores and capitalize for the display options
                # freight_sc3 = st.selectbox('Select freight demand scenario',
                #                            options=levelized_cost.freight_demand_scenario.unique(),
                #                            help="Dummy tooltip", key=32,
                #                            format_func=lambda x: (x.replace('_', ' ')).title())
                reg_sc3 = st.selectbox('Select region', options=levelized_cost.region.unique(), help="Dummy tooltip",
                                       key=33, format_func=lambda x: (x.replace('_', ' ')).title())
                tech_sc3 = st.selectbox('Select power train technology', options=levelized_cost.technology.unique(),
                                        help="Dummy tooltip", key=34,
                                        format_func=lambda x: (x.replace('_', ' ')).title())
                year_cost = levelized_cost[
                    #(levelized_cost.energy_system_scenario == ener_sc3) &  # select energy system scenario
                    #(levelized_cost.freight_demand_scenario == freight_sc3) &  # select freight demand scenario
                    (levelized_cost.technology == tech_sc3) &  # select technology
                    (levelized_cost.region == reg_sc3)  # select region
                    ]
                year_cost['year'] = year_cost['year'].astype('category')  # for numerical y axis, convert to factor
                bar_plotv(year_cost, 'year', "Year")
                

# %%carbon intensity function
def visualize_carbon_intensity(carbon_intensity):
    st.subheader("Plot carbon intensity outputs")
    if st.session_state.run == 0:
        st.warning("Run the Simulation First to Display Outputs")
    elif st.session_state.run == 1:
        option_CIplot = st.selectbox(label="Choose a graph", options=("None", "Carbon intensity by Regions", "Carbon intensity by Technologies", "Carbon intensity by Years"))
        carbon_intensity['year'] = carbon_intensity['year'].astype(str)
        st.write(carbon_intensity)
        for n in carbon_intensity.index:
            LCH4 = carbon_intensity.loc[n, 'CH4_carbon_intensity (g CH4/ton-mile)']  # CH4 carbon intensity (g CH4/ton-mile)
            if carbon_intensity.loc[n, 'technology'] == 'biodiesel':
                LCH4_CO2eq = 27.0 * LCH4  # CH4 carbon intensity in terms of CO2eq (g CO2eq/ton-mile) for non-fossil sources
            else:
                LCH4_CO2eq = 29.8 * LCH4  # CH4 carbon intensity in terms of CO2eq (g CO2eq/ton-mile) for fossil sources
            carbon_intensity.loc[n, 'CH4_carbon_intensity (g CH4/ton-mile)'] = LCH4_CO2eq
        if option_CIplot == "Carbon intensity by Regions":
            # inputs for the first plot: Region vs cost
            # co2_ener_sc1 = st.selectbox('Select energy system scenario',
            #                             options=carbon_intensity.energy_system_scenario.unique(),
            #                             help="Dummy tooltip", key="C11",
            #                             format_func=lambda x: (x.replace('_', ' ')).title())
            # co2_freight_sc1 = st.selectbox('Select freight demand scenario',
            #                                options=carbon_intensity.freight_demand_scenario.unique(),
            #                                help="Dummy tooltip", key="C12",
            #                                format_func=lambda x: (x.replace('_', ' ')).title())
            co2_tech_sc1 = st.selectbox('Select power train technology',
                                        options=carbon_intensity.technology.unique(),
                                        help="Dummy tooltip", key="C13",
                                        format_func=lambda x: (x.replace('_', ' ')).title())
            co2_year_sc1 = st.selectbox('Select year', options=carbon_intensity.year.unique(),
                                        help="Dummy tooltip", key="C14")
            # calculations for creating the plot
            region_CI = carbon_intensity[
                #(carbon_intensity.energy_system_scenario == co2_ener_sc1) &  # select an energy system scenario
                #(carbon_intensity.freight_demand_scenario == co2_freight_sc1) &  # select a freight demand scenario
                (carbon_intensity.technology == co2_tech_sc1) &  # select a technology
                (carbon_intensity.year == co2_year_sc1)  # select a year
                ]
            C_bar_ploth(region_CI, "region", "Regions")
    
        elif option_CIplot == "Carbon intensity by Technologies":
            # inputs for the second plot: cost vs technology
    
            # co2_ener_sc2 = st.selectbox('Select energy system scenario',
            #                             options=carbon_intensity.energy_system_scenario.unique(),
            #                             help="Dummy tooltip", key="C21",
            #                             format_func=lambda x: (x.replace('_', ' ')).title())
            # co2_freight_sc2 = st.selectbox('Select freight demand scenario',
            #                                options=carbon_intensity.freight_demand_scenario.unique(),
            #                                help="Dummy tooltip", key="C22",
            #                                format_func=lambda x: (x.replace('_', ' ')).title())
            co2_reg_sc2 = st.selectbox('Select region', options=carbon_intensity.region.unique(),
                                       help="Dummy tooltip", key="C23",
                                       format_func=lambda x: (x.replace('_', ' ')).title())
            co2_year_sc2 = st.selectbox('Select year', options=carbon_intensity.year.unique(),
                                        help="Dummy tooltip", key="C24")
    
            tech_CI = carbon_intensity[
                #(carbon_intensity.energy_system_scenario == co2_ener_sc2) &  # select energy system scenario
                #(carbon_intensity.freight_demand_scenario == co2_freight_sc2) &  # select freight demand scenario
                (carbon_intensity.region == co2_reg_sc2) &  # select region
                (carbon_intensity.year == co2_year_sc2)  # select year
                ]
            C_bar_plotv(tech_CI, 'technology', "Technology")
           
    
        elif option_CIplot == "Carbon intensity by Years":
            # inputs for the third plot: cost vs Years
    
            # co2_ener_sc3 = st.selectbox('Select energy system scenario',
            #                             options=carbon_intensity.energy_system_scenario.unique(),
            #                             help="Business As Usual means no new federal policies \n\n50% reduction by 2050 means___\n\nNet zero by 2050 means__",
            #                             key="C31", format_func=lambda x: (x.replace('_', ' ')).title())
            # # the last part, i.e., format function is to remove underscores and capitalize for the display options
            # co2_freight_sc3 = st.selectbox('Select freight demand scenario',
            #                                options=carbon_intensity.freight_demand_scenario.unique(),
            #                                help="Dummy tooltip", key="C32",
            #                                format_func=lambda x: (x.replace('_', ' ')).title())
            co2_reg_sc3 = st.selectbox('Select region', options=carbon_intensity.region.unique(),
                                       help="Dummy tooltip", key="C33",
                                       format_func=lambda x: (x.replace('_', ' ')).title())
            co2_tech_sc3 = st.selectbox('Select power train technology',
                                        options=carbon_intensity.technology.unique(),
                                        help="Dummy tooltip", key="C34",
                                        format_func=lambda x: (x.replace('_', ' ')).title())
    
            year_CI = carbon_intensity[
                #(carbon_intensity.energy_system_scenario == co2_ener_sc3) &  # select energy system scenario
                #(carbon_intensity.freight_demand_scenario == co2_freight_sc3) &  # select freight demand scenario
                (carbon_intensity.technology == co2_tech_sc3) &  # select technology
                (carbon_intensity.region == co2_reg_sc3)  # select region
                # (df_cost.year == 2025)  # select year
                ]
            year_CI['year'] = year_CI['year'].astype('category')  # for numerical y axis, convert to factor
            C_bar_plotv(year_CI, 'year', "Year")