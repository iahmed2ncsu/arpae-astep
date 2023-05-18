#!/usr/bin/env python
# coding: utf-8


__author__ = "Dr Rupal Mittal, Andreas Weiss"
__email__ = "Rupal.Mittal@deutschebahn.com, Andreas.AJ.Weiss@deutschebahn.com"
__status__ = "Development"

################
### Prepare inputs to run Module 9: Levelized Cost and Carbon Intensity Estimation ###
################

#Pull results of:
#- Module 6: Energy Use by Type and Temoa Region
#- Module 7: Energy Prices
#- Module 8: Infrastructure Requirements & Cost

#Preprocess, merge and concatenate data to match inputs required to run Module 9


###################
### Import Packages
###################

import os
import time
import json
#import numpy as np
import pandas as pd
#from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


#################################
### Input/Output and Static files in repository
#################################

config_input_path = "./Config/user_input.json"
static_input_path = "./Data/Static/"
template_input_path = "./Data/Template/"

module6_output_path = "./Data/Output/Module-6"
module7_output_path = "./Data/Output/Module-7"
module8_output_path = "./Data/Output/Module-8"

module9_input_path = "./Data/Input/Module-9"


###################
### Functions
###################

### Nomenclature

def replace_template_nomenclature(data):
    """    
    The output from some modules use a different nomenclature
    for the categorical variable, "technology". This template
    fixes that.
    """
    template_regions = {'CA': 'california',
                        'CEN': 'central',
                        'MID_AT': 'middle_atlantic',
                        'NE': 'north_east',
                        'NW': 'north_west',
                        'N_CEN': 'north_central',
                        'SE': 'south_east',
                        'SW': 'south_west',
                        'TX': 'texas'}
    template_technology = {'Die': 'diesel',
                           'Hyd': 'hydrogen',
                           'BioDie': 'biodiesel',
                           'Cat': 'catenary',
                           'Bat': 'battery'}

    data['technology'] = data['technology'].replace(template_technology)
    data['region'] = data['region'].replace(template_regions)

    return data


### Fit linear regression from recharging station size to energy refueled and cost

def fit_linear_regression(x_col, y_col, print_modell_coef=False, plot=False):
    """    
    The function performs linear regression given X and Y.
    """
    X = x_col.values.reshape(-1, 1)
    y = y_col.values.reshape(-1, 1)

    reg_model = LinearRegression()
    reg_model.fit(X, y)

    y_pred = reg_model.predict(X)

    if print_modell_coef:
        print("Coefficients: {}".format(reg_model.coef_))
        print("Intercept: {}".format(reg_model.intercept_))
        print("R2_score: {}".format(round(r2_score(y, y_pred), 3)))

#     if plot:
#         plt.plot(X, y, c="b", label="Original values")
#         plt.plot(X, y_pred, c="g", label="Linear Regression fit")
#         plt.text(0.8*max(X), min(y), "R2_score: {}".format(round(r2_score(y, y_pred), 3)))
#         plt.legend()
#         plt.show()

    return reg_model


### Update Module9 Templates

def update_module9_templates(year, mod6_data, mod9_data, user_input,
                             sort_cols=["energy_system_scenario", "freight_demand_scenario",
                                        "year", "region", "technology"]):
    """    
    The function updates the templates stored in Data/Static for Module 9.
    """    
    # Sort both tables to make sure order matches
    mod9_data = mod9_data.sort_values(by=sort_cols).reset_index(drop=True)
    mod6_data = mod6_data.sort_values(by=sort_cols).reset_index(drop=True)

    # Define masks based on user settings config (energy_system_scenario, freight_demand_scenario, year)
    mask_rows = (mod9_data['energy_system_scenario'] == user_input['energy_system_scenario']) & \
        (mod9_data['freight_demand_scenario'] == user_input['freight_demand_scenario']) & \
        (mod9_data['year'] == int(year))

    mask_cols = list(mod6_data.columns)
    mod9_data = mod9_data.loc[mask_rows, :].copy()
    # Update module-9 tables
    mod9_data.loc[:, mask_cols] = mod6_data.loc[:, mask_cols].values

    return mod9_data


### Update Module9 Templates with module 7

def update_module7_templates(year, mod6_data, mod9_data, user_input, 
                             sort_cols=["energy_system_scenario", "freight_demand_scenario",
                                        "year", "region", "technology"]):
    """    
    The function updates the templates stored in Data/Template in conjunction
    with results from Module 7 for Module 9.
    """ 
    # Sort both tables to make sure order matches
    mod9_data = mod9_data.sort_values(by=sort_cols).reset_index(drop=True)
    mod6_data = mod6_data.sort_values(by=sort_cols).reset_index(drop=True)

    # Define masks based on user settings config (energy_system_scenario, freight_demand_scenario, year)
    mask_rows9 = (mod9_data['energy_system_scenario'] == user_input['energy_system_scenario']) & \
        (mod9_data['freight_demand_scenario'] == user_input['freight_demand_scenario']) & \
        (mod9_data['year'] == int(year)) & \
        (mod9_data['technology'].isin(mod6_data["technology"].unique()))

    mask_rows7 = (mod6_data['energy_system_scenario'] == user_input['energy_system_scenario']) & \
        (mod6_data['freight_demand_scenario'] == user_input['freight_demand_scenario']) & \
        (mod6_data['year'] == int(year)) & \
        (mod6_data['technology'].isin(mod9_data["technology"].unique()))

    mask_cols = list(mod9_data.columns)
    # Update module-9 tables
    mod6_data.loc[mask_rows7, mask_cols] = mod9_data.loc[mask_rows9, mask_cols].values

    return mod6_data


### Update Module9 Templates with module 8 data (cost_per_station ($) and infrastructure_M_cost ($/year) for battery and hydrogen)

def update_module8_templates(year, mod8_data, mod9_data, user_input,
                             sort_cols=["energy_system_scenario", "freight_demand_scenario",
                                        "year", "region", "technology"]):
    """    
    The function updates the templates stored in Data/Template in conjunction
    with results from Module 8 for Module 9.
    """ 
    # Sort both tables to make sure order matches
    mod9_data = mod9_data.sort_values(by=sort_cols).reset_index(drop=True)
    mod8_data = mod8_data.sort_values(by=sort_cols).reset_index(drop=True)

    # Define masks based on user settings config (energy_system_scenario, freight_demand_scenario, year)
    mask_rows9 = (mod9_data['energy_system_scenario'] == user_input['energy_system_scenario']) & \
        (mod9_data['freight_demand_scenario'] == user_input['freight_demand_scenario']) & \
        (mod9_data['year'] == int(year)) & \
        (mod9_data['technology'].isin(mod8_data["technology"].unique()))

    mask_cols = list(mod8_data.columns)
    # Update module-9 tables
    mod9_data.loc[mask_rows9, mask_cols] = mod8_data.loc[:, mask_cols].values

    return mod9_data


def prepare_inputs_for_module9(year, save_mode="append", print_summary=False):
    """    
    The function prepares the five inputs files needed for Module 9.
    
        Input: files from Module-6, Module-7 and Module-8 along with template
               files in Data/Template 
    """ 
    start = time.time()

    ################################
    ### Config file with user inputs
    ################################

    with open(config_input_path, encoding="utf-8") as json_file:
        config = json.load(json_file)


    ##############################
    ### Load Module 6 output files
    ##############################

    traffic_flow_for_Mod9 = pd.read_csv("%s/traffic_flow_for_Mod9.csv" %module6_output_path)
    train_for_Mod9 = pd.read_csv("%s/train_for_Mod9.csv" %module6_output_path)
    refueling_for_Mod9 = pd.read_csv("%s/refueling_for_Mod9.csv" %module6_output_path)
    energy_for_Mod9 = pd.read_csv("%s/energy_for_Mod9.csv" %module6_output_path)


    #############################################################################
    ### Change nomenclature for region and technology to match Module 9 templates
    #############################################################################
    
    traffic_flow_for_Mod9 = replace_template_nomenclature(traffic_flow_for_Mod9)
    train_for_Mod9 = replace_template_nomenclature(train_for_Mod9)
    refueling_for_Mod9 = replace_template_nomenclature(refueling_for_Mod9)
    energy_for_Mod9 = replace_template_nomenclature(energy_for_Mod9)


    #############################################
    ### Load and preprocess Module 7 output files
    #############################################

    df_module7 = pd.read_csv("%s/commodityPrice_and_carbonIntensity_module7.csv" %module7_output_path)
    df_module7 = df_module7.iloc[:, 1:]
    
    df_module7["freight_demand_scenario"]=config["freight_demand_scenario"]
    df_module7 = df_module7[(df_module7["renewables_prices"] == "Moderate") & (df_module7["hydrogen_subsidies"] == "No") ]
    if "reduction" in config["energy_system_scenario"]:
        df_module7 = df_module7[(df_module7["oil_prices"] == "Low")]
    else:
        df_module7 = df_module7[(df_module7["oil_prices"] == "Mid")]
    
#    df_module7 = df_module7[df_module7["freight_demand_scenario"]=="Agricultural Reduction"]
    
    ### Fixing Inconsistent Nomenclature
#     energy_price_module7['technology'] = energy_price_module7['technology'].replace({"electricity": "battery"})
#     energy_price_module7['energy_system_scenario'] = energy_price_module7['energy_system_scenario'].replace({"business_as_usual": "Reference/business as usual"})
#     energy_price_module7['freight_demand_scenario'] = energy_price_module7['freight_demand_scenario'].replace({"population_shift": "Population Shift"})
#     carbon_intensity_module7['technology'] = carbon_intensity_module7['technology'].replace({'electricity': 'battery'})
#     carbon_intensity_module7['energy_system_scenario'] = carbon_intensity_module7['energy_system_scenario'].replace({"business_as_usual": "Reference/business as usual"})
#     carbon_intensity_module7['freight_demand_scenario'] = carbon_intensity_module7['freight_demand_scenario'].replace({"population_shift": "Population Shift"})

    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
            'energy_price', 'energy_price_unit']
    energy_price_module7 = df_module7[cols]
    energy_price_module7['technology'] = energy_price_module7['technology'].str.lower()

    energy_price_units = {'$/Gallon': '$/gallon',
                          '$/kg': '$/kgH2',
                          '$/kWh': '$/kWh'}
    energy_price_module7['energy_price_unit'] = energy_price_module7['energy_price_unit'].replace(energy_price_units)

    # Define masks based on user settings config (energy_system_scenario, freight_demand_scenario, year)
    mask_rows = (energy_price_module7['energy_system_scenario'] == config['energy_system_scenario']) & \
        (energy_price_module7['year'] == int(year))
    energy_price_module7 = energy_price_module7.loc[mask_rows, :].reset_index(drop=True)

    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
        'upstream_CO2_emission_factor', 'CO2_emission_factor_unit']
    carbon_intensity_module7 = df_module7[cols]

    emission_factor_units = {'kg_of_CO2/kg_of_H2': 'kgCO2/kgH2',
                         'kg of CO2/kWh of electricity': 'kgCO2/kWh'}
    carbon_intensity_module7['CO2_emission_factor_unit'] = carbon_intensity_module7['CO2_emission_factor_unit'].replace(emission_factor_units)


    # Add static columns (empty for now - needs to be discussed with Module 9)
    #cols = ["energy_consumption_at_the_well (GJ)", "upstream_CO2_emission_factor", "downstream_CO2_emission_factor",
    #        "CO2_emission_factor_unit", "upstream_CH4_emission_factor", "downstream_CH4_emission_factor",
    #        "CH4_emission_factor_unit"]
    #for col in cols:
    #    energy_for_Mod9[col] = np.nan


    ############################################
    ### Load and preprocess Module 8 output file
    ############################################

    refueling_module8 = pd.read_csv("%s/refueling_bat_and_H2_data.csv" %module8_output_path)
    refueling_station_sizes = pd.read_csv("%s/tm_energy_per_charging_station.csv" %module6_output_path)

    refueling_station_sizes = refueling_station_sizes.loc[:, ['Region', 'HydMWh/Day', 'BatMWh/Day']]

    ##############################################################################
    ### Fit linear regression on module 8 outputs
    # Input: Refueling/Recharging station size in MWh/day for hydrogen and battery
    # Target: cost_per_station in $ (Station capital cost), infrastructure_M_cost in $/year (operating cost) depending on station size
    # Fit regression based on ouutput from module-8: refueling_module8

    # TODO: Turn print/plot off
    ##############################################################################

    refueling_module8_bat = refueling_module8[refueling_module8["technology"] == "battery"]
    print("Bat station_energy_use_per_day (MWh/day) - cost_per_station ($):")
    reg_bat_capcst = fit_linear_regression(x_col=refueling_module8_bat["station_energy_use_per_day (MWh/day)"],
                                           y_col=refueling_module8_bat["cost_per_station ($)"],
                                           print_modell_coef=False, plot=False)
    print("Bat station_energy_use_per_day (MWh/day) - infrastructure_M_cost ($/year):")
    reg_bat_opcst = fit_linear_regression(x_col=refueling_module8_bat["station_energy_use_per_day (MWh/day)"],
                                           y_col=refueling_module8_bat["infrastructure_M_cost ($/year)"],
                                           print_modell_coef=False, plot=False)
    print("Bat station_energy_use_per_day (MWh/day) - operational_refueling_energy_use (GJ):")
    reg_bat_e_operational = fit_linear_regression(x_col=refueling_module8_bat["station_energy_use_per_day (MWh/day)"],
                                                  y_col=refueling_module8_bat["operational_refueling_energy_use (GJ)"],
                                                  print_modell_coef=False, plot=False)
    print("Bat station_energy_use_per_day (MWh/day) - energy_refueled_to_tenders&locomotives (GJ):")
    reg_bat_e_refueled = fit_linear_regression(x_col=refueling_module8_bat["station_energy_use_per_day (MWh/day)"],
                                               y_col=refueling_module8_bat["energy_refueled_to_tenders&locomotives (GJ)"],
                                               print_modell_coef=False, plot=False)


    refueling_module8_hyd = refueling_module8[refueling_module8["technology"] == "hydrogen"]
    print("Hyd station_energy_use_per_day (MWh/day) - cost_per_station ($):")
    reg_hyd_capcst = fit_linear_regression(x_col=refueling_module8_hyd["station_energy_use_per_day (MWh/day)"],
                                           y_col=refueling_module8_hyd["cost_per_station ($)"],
                                           print_modell_coef=False, plot=False)
    print("Hyd station_energy_use_per_day (MWh/day) - infrastructure_M_cost ($/year):")
    reg_hyd_opcst = fit_linear_regression(x_col=refueling_module8_hyd["station_energy_use_per_day (MWh/day)"],
                                           y_col=refueling_module8_hyd["infrastructure_M_cost ($/year)"],
                                           print_modell_coef=False, plot=False)
    print("Hyd station_energy_use_per_day (MWh/day) - operational_refueling_energy_use (GJ):")
    reg_hyd_e_operational = fit_linear_regression(x_col=refueling_module8_hyd["station_energy_use_per_day (MWh/day)"],
                                                  y_col=refueling_module8_hyd["operational_refueling_energy_use (GJ)"],
                                                  print_modell_coef=False, plot=False)
    print("Hyd station_energy_use_per_day (MWh/day) - energy_refueled_to_tenders&locomotives (GJ):")
    reg_hyd_e_refueled = fit_linear_regression(x_col=refueling_module8_hyd["station_energy_use_per_day (MWh/day)"],
                                               y_col=refueling_module8_hyd["energy_refueled_to_tenders&locomotives (GJ)"],
                                               print_modell_coef=False, plot=False)


    refueling_station_sizes["cost_per_station ($) bat"] = reg_bat_capcst.predict(refueling_station_sizes["BatMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["infrastructure_M_cost ($/year) bat"] = reg_bat_opcst.predict(refueling_station_sizes["BatMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["operational_refueling_energy_use (GJ) bat"] = reg_bat_e_operational.predict(refueling_station_sizes["BatMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["energy_refueled_to_tenders&locomotives (GJ) bat"] = reg_bat_e_refueled.predict(refueling_station_sizes["BatMWh/Day"].values.reshape(-1, 1))

    refueling_station_sizes["cost_per_station ($) hyd"] = reg_hyd_capcst.predict(refueling_station_sizes["HydMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["infrastructure_M_cost ($/year) hyd"] = reg_hyd_opcst.predict(refueling_station_sizes["HydMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["operational_refueling_energy_use (GJ) hyd"] = reg_hyd_e_operational.predict(refueling_station_sizes["HydMWh/Day"].values.reshape(-1, 1))
    refueling_station_sizes["energy_refueled_to_tenders&locomotives (GJ) hyd"] = reg_hyd_e_refueled.predict(refueling_station_sizes["HydMWh/Day"].values.reshape(-1, 1))

    refueling_station_per_temoa = refueling_station_sizes.groupby("Region").sum()


    # Process data to shape to fit Module 9 input
    cols_cost = ["cost_per_station ($) bat", "cost_per_station ($) hyd"]
    cols_om = ["infrastructure_M_cost ($/year) bat", "infrastructure_M_cost ($/year) hyd"]
    cols_e_op = ["operational_refueling_energy_use (GJ) bat", "operational_refueling_energy_use (GJ) hyd"]
    cols_e_ref = ["energy_refueled_to_tenders&locomotives (GJ) bat", "energy_refueled_to_tenders&locomotives (GJ) hyd"]

    refueling_station_per_temoa_melt = refueling_station_per_temoa.loc[:, cols_cost].reset_index().melt(value_vars=cols_cost, id_vars="Region",
                                                                                                        var_name="technology",
                                                                                                        value_name="cost_per_station ($)")
    refueling_station_per_temoa_melt['technology'] = refueling_station_per_temoa_melt['technology'].str.split(' ').str[-1]

    temp1 = refueling_station_per_temoa.loc[:, cols_om].reset_index().melt(value_vars=cols_om, id_vars="Region",
                                                                           var_name="technology",
                                                                           value_name="infrastructure_M_cost ($/year)")
    temp1['technology'] = temp1['technology'].str.split(' ').str[-1]
    temp2 = refueling_station_per_temoa.loc[:, cols_e_op].reset_index().melt(value_vars=cols_e_op, id_vars="Region",
                                                                             var_name="technology",
                                                                             value_name="operational_refueling_energy_use (GJ)")
    temp2['technology'] = temp1['technology'].str.split(' ').str[-1]
    temp3 = refueling_station_per_temoa.loc[:, cols_e_ref].reset_index().melt(value_vars=cols_e_ref, id_vars="Region",
                                                                             var_name="technology",
                                                                             value_name="energy_refueled_to_tenders&locomotives (GJ)")
    temp3['technology'] = temp3['technology'].str.split(' ').str[-1]


    refueling_station_per_temoa_melt = refueling_station_per_temoa_melt.merge(temp1, on=["Region", "technology"])
    refueling_station_per_temoa_melt = refueling_station_per_temoa_melt.merge(temp2, on=["Region", "technology"])
    refueling_station_per_temoa_melt = refueling_station_per_temoa_melt.merge(temp3, on=["Region", "technology"])

    technology_names = {"bat": "battery", "hyd": "hydrogen"}
    refueling_station_per_temoa_melt['technology'] = refueling_station_per_temoa_melt['technology'].replace(technology_names)
    refueling_station_per_temoa_melt = refueling_station_per_temoa_melt.rename(columns={"Region": "region",
                                                                                        "infrastructure_M_cost ($/year)": "infrastructure_O&M_cost ($/year)"})

    # Add columns from user_input
    for key, value in config.items():
        if key in ['energy_system_scenario', 'freight_demand_scenario', 'year']:
            refueling_station_per_temoa_melt[key] = value

    # rearrange columns
    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
            'cost_per_station ($)', 'infrastructure_O&M_cost ($/year)',
            'operational_refueling_energy_use (GJ)', 'energy_refueled_to_tenders&locomotives (GJ)']
    refueling_station_per_temoa_melt = refueling_station_per_temoa_melt[cols]

    refueling_station_per_temoa_melt = replace_template_nomenclature(refueling_station_per_temoa_melt)

    ################################################################
    ### Load module 9 templates and update info of current iteration
    ################################################################
    
    traffic_flow = pd.read_csv("%s/traffic_flow.csv" %template_input_path)
    train = pd.read_csv("%s/train.csv" %template_input_path)
    refueling = pd.read_csv("%s/refueling.csv" %template_input_path)
    energy = pd.read_csv("%s/energy.csv" %template_input_path)
    #energy_price = pd.read_csv("%s/energy.csv" %template_input_path)

    # TODO: Names of freight_demand_scenario and possibly energy_system_scenario do not match between config and templates
    # TODO: Fix FutureWarning

    ### Update Module9 templates with module 6
    traffic_flow_updated = update_module9_templates(year, mod6_data=traffic_flow_for_Mod9,
                                                    mod9_data=traffic_flow,
                                                    user_input=config)

    train_updated = update_module9_templates(year, mod6_data=train_for_Mod9,
                                             mod9_data=train,
                                             user_input=config)

    refueling_updated = update_module9_templates(year, mod6_data=refueling_for_Mod9,
                                                 mod9_data=refueling,
                                                 user_input=config)

    energy_updated = update_module9_templates(year, mod6_data=energy_for_Mod9,
                                              mod9_data=energy,
                                              user_input=config)

    ### Update Module9 templates with module 7
    energy_updated = update_module7_templates(year, mod6_data=energy_updated,
                                              mod9_data=carbon_intensity_module7,
                                              user_input=config)

    ### Update Module9 Templates with module 8 data (cost_per_station ($) and infrastructure_M_cost ($/year) for battery and hydrogen)
    energy_price_updated = energy_price_module7.copy()

    refueling_updated = update_module8_templates(year, refueling_station_per_temoa_melt,
                                                 refueling_updated,
                                                 user_input=config)


    ##################################
    ### Save output files for Module 9
    ##################################

    # debug: Output files are not saved
    # append: Check if output files exist in module9_input_path,
    #         for each file: if exist -> append, if does not exist -> create new
    # overwrite: Save output and overwrite existing files

    # Updated files:
    if print_summary:
        print("Updated files for:")
        print('energy_system_scenario: ' + config['energy_system_scenario'])
        print('freight_demand_scenario: ' + config['freight_demand_scenario'])
        print('year: ' + year + '\n')
        print("traffic_flow_updated: " + str(traffic_flow_updated.shape))
        print("train_updated: " + str(train_updated.shape))
        print("refueling_updated: " + str(refueling_updated.shape))
        print("energy_updated: " + str(energy_updated.shape))
        print("energy_price_updated: " + str(energy_price_updated.shape) + '\n')

        print("File save mode: " + save_mode)


    if save_mode == "debug":
        pass

    if save_mode == "append":
        if os.path.isdir(module9_input_path):
            pass
        else:
            os.makedirs(module9_input_path)

        traffic_flow_updated.to_csv("%s/traffic_flow_for_Mod9.csv" %module9_input_path, mode='a', index=False,
                                    header=not os.path.exists("%s/traffic_flow_for_Mod9.csv" %module9_input_path))
        train_updated.to_csv("%s/train_for_Mod9.csv" %module9_input_path, mode='a', index=False,
                             header=not os.path.exists("%s/train_for_Mod9.csv" %module9_input_path))
        refueling_updated.to_csv("%s/refueling_for_Mod9.csv" %module9_input_path, mode='a', index=False,
                                 header=not os.path.exists("%s/refueling_for_Mod9.csv" %module9_input_path))
        energy_updated.to_csv("%s/energy_for_Mod9.csv" %module9_input_path, mode='a', index=False,
                              header=not os.path.exists("%s/energy_for_Mod9.csv" %module9_input_path))
        energy_price_updated.to_csv("%s/energy_price_for_Mod9.csv" %module9_input_path, mode='a', index=False,
                                    header=not os.path.exists("%s/energy_price_for_Mod9.csv" %module9_input_path))

    if save_mode == "overwrite":
        traffic_flow_updated.to_csv("%s/traffic_flow_for_Mod9.csv" %module9_input_path, index=False)
        train_updated.to_csv("%s/train_for_Mod9.csv" %module9_input_path, index=False)
        refueling_updated.to_csv("%s/refueling_for_Mod9.csv" %module9_input_path, index=False)
        energy_updated.to_csv("%s/energy_for_Mod9.csv" %module9_input_path, index=False)
        energy_price_updated.to_csv("%s/energy_price_for_Mod9.csv" %module9_input_path, index=False)


    end = time.time()
    print(f"Run time to prepare input files for Module_9 = {round(end-start,ndigits = 2)} seconds")

    return 0


#prepare_inputs_for_module9(year, save_mode="append", print_summary=True)
