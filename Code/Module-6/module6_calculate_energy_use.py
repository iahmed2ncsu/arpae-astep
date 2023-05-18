#!/usr/bin/env python
# coding: utf-8

##########
### Import
##########

import time
import numpy as np
import pandas as pd


###################
### Paths and Files
###################

static_input_path = "../Data/Static"
config_input_path = "../Config/"

module4_output_path = "../Data/Output/Module-4"
module5_output_path = "../Data/Output/Module-5"
module6_output_path = "../Data/Output/Module-6"


########################################
### Populate config based on user inputs
########################################

import json
config_file_path = "%s/user_input.json" %config_input_path
with open(config_file_path, encoding="utf-8") as json_file:
    config = json.load(json_file)
#config["year"] = int(config["year"])

#############
### Functions
#############

### Distance Function

def distance(pt1_lat, pt2_lat, pt1_lon, pt2_lon, use_approx=False):
    """
    Given two geographical coordinates with latitudes and longitudes,
    the function returns the distance in nautical miles.
    """

    if use_approx:
        c = 60 * ((pt2_lon - pt1_lon) ** 2 + (pt1_lat - pt2_lat) ** 2) ** 0.5
    else:
        # Radius of the earth, in meters.
        #R = 6371000

        # Radius of the earth, in nautical miles
        R = 3440

        rlat1 = pt1_lat * (np.pi/180)
        rlat2 = pt2_lat * (np.pi/180)

        dlat = rlat2 - rlat1
        dlon = (pt2_lon - pt1_lon)*(np.pi/180)

        a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(rlat1) * np.cos(rlat2) * np.sin(dlon/2) * np.sin(dlon/2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)) * R

    return c


### Nomenclature

def fix_tech_nomenclature(data):
    """
    The output from some modules use a different nomenclature
    for the categorical variable, "techonology". This template
    fixes that.
    """
    template_technology = {'Die': 'diesel',
                           'Hyd': 'hydrogen',
                           'BioDie': 'biodiesel',
                           'Cat': 'catenary',
                           'Bat': 'battery'}

    data["E_Source"] = data["E_Source"].replace(template_technology)
    return data


def calculate_energy_use(year):
    """
    This function converts traffic (tonne-miles) into energy.
    
        Input:
            tech_fraction -> Energy distribution acquired from the 
                                   config file (user-input)
            P_nc = [0.3, 0.6, 0.1] -> Train distribution for STS. 
                                 For MTS, this should be [1] 
                                 (to-be-implemented)
                                 
    The first part of this function converts tonne-miles from links
    to yards using vectorization (the logic was derived from a VBA code).
    The second part converts tonne-miles into energy. The main output is 
    tonne-miles and energy per yard (charging station), state and 
    temoa region.
    
    The output from some modules use a different nomenclature
    for the categorical variable, "technology". This template
    fixes that.
    """

    start = time.time()

    #################################
    ### Input/Output and Static files

    params = pd.read_csv("%s/params.csv" %static_input_path)
    links = pd.read_csv("%s/links.csv" %static_input_path)
    lkflows = pd.read_csv("%s/lkflows.csv" %module4_output_path)
    yards = pd.read_csv("%s/yards.csv" %static_input_path)

    energy_intensity_matrix = pd.read_csv("%s/EnergyIntensity_Matrix.csv" %module5_output_path)

    #################################
    ### Remove yards (charging stations) not to be included
    yards = yards[yards["include"] == True].drop(columns="include").reset_index(drop=True)

    #################################
    ### Scalar and Vector Assignments

    df_theta = params[params[params.columns[0]]=="theta"]
    theta = df_theta[df_theta.columns[1]]
    theta = float(theta/400)
    factorup = float(params.iloc[14, 5])

    #nLink = len(links)
    lkLon = np.array(links["AvgLon"])
    lkLat = np.array(links["AvgLat"])
    lkTM = np.array(lkflows["TMc_e (M)"])

    #nYard = len(yards)
    ydLon = np.array(yards["Lon"])
    ydLat = np.array(yards["Lat"])


    #################
    ### Vectorization
    #################
    
    distance_ly = distance( lkLat[:, None], ydLat[None, :], lkLon[:, None], ydLon[None, :] )
    c_ly = np.exp(-theta * distance_ly)
    csum_l = np.sum(c_ly, axis=1)
    cnorm_ly = c_ly/csum_l[:, None]
    yTM_y = np.sum(cnorm_ly * lkTM[:, None], axis=0)


    ################################################################
    ### Calculate overall energy intensity per Temoa and energy type
    ################################################################
    
    energy_intensity = energy_intensity_matrix.copy()

    P_nc = [0.3, 0.6, 0.1] # Percentage share of tonmiles for train lengths 50, 100, 150

#     tech_fraction = {"Diesel": 0.05,
#                      "BioDie": 0.05,
#                      "DieHyb": 0.15,
#                      "BioHyb": 0.10,
#                      "HydHyb": 0.40,
#                      "Bat": 0.25}
    
    tech_fraction = config["tech_fraction"][year]

    ############################
    ### Energy Intensity Grouped
    ############################
    
    ### Sum over the different train lengths in the energy density matrix
    
    energy_intensity_grouped = pd.DataFrame()
    for i, group in energy_intensity.groupby(["Reg", "Tech"]):
        index_cols = group.iloc[0, :2]
        data_cols = group.iloc[:, 3:]
        data_cols = data_cols.T * P_nc
        data_cols = data_cols.sum(axis=1)
        energy_intensity_grouped = pd.concat([energy_intensity_grouped, pd.concat([index_cols, data_cols])], axis=1)

    energy_intensity_grouped = energy_intensity_grouped.T.reset_index(drop=True).drop(columns=["ebtMin", "eTrn", "eRcv"])
    energy_intensity_grouped = energy_intensity_grouped.rename(columns={"eDie": "Diesel",
                                                                        "eBio": "BioDie",
                                                                        "eHyd": "Hyd",
                                                                        "eBat": "Bat",
                                                                        "eCat": "Cat"})


    #############################################################################
    ### The effect of "Diesel", "BioDie", "DieHyb", "BioHyb", "HydHyb", "Bat" on
    ### output techs "Diesel", "Biodiesel", "Hydrogen", "Cat", "Bat"
    #############################################################################

    regions = energy_intensity_grouped["Reg"].unique()

    reg=np.array([])
    diesel=np.array([])
    biodiesel=np.array([])
    hydrogen=np.array([])
    grid=np.array([])
    bat=np.array([])
    for reg_val in regions:
        df = energy_intensity_grouped[energy_intensity_grouped["Reg"]==reg_val]

        reg = np.append(reg, reg_val)
        diesel_val = df[df["Tech"]=="Diesel"]["Diesel"].item()*tech_fraction["Diesel"] \
                   + df[df["Tech"]=="DieHyb"]["Diesel"].item()*tech_fraction["DieHyb"]
        diesel = np.append(diesel, diesel_val)

        biodiesel_val = df[df["Tech"]=="BioDie"]["BioDie"].item()*tech_fraction["BioDie"] \
                      + df[df["Tech"]=="BioHyb"]["BioDie"].item()*tech_fraction["BioHyb"]
        biodiesel = np.append(biodiesel, biodiesel_val)

        hydrogen_val = df[df["Tech"]=="HydHyb"]["Hyd"].item()*tech_fraction["HydHyb"]
        hydrogen = np.append(hydrogen, hydrogen_val)

        grid_val = df[df["Tech"]=="Bat"]["Bat"].item()*tech_fraction["Bat"] \
                 + df[df["Tech"]=="DieHyb"]["Cat"].item()*tech_fraction["DieHyb"] \
                 + df[df["Tech"]=="BioHyb"]["Cat"].item()*tech_fraction["BioHyb"] \
                 + df[df["Tech"]=="HydHyb"]["Cat"].item()*tech_fraction["HydHyb"] \
                 + df[df["Tech"]=="Bat"]["Cat"].item()*tech_fraction["Bat"]
        grid = np.append(grid, grid_val)

        bat_val = df[df["Tech"]=="DieHyb"]["Bat"].item()*tech_fraction["DieHyb"] \
                + df[df["Tech"]=="BioHyb"]["Bat"].item()*tech_fraction["BioHyb"] \
                + df[df["Tech"]=="HydHyb"]["Bat"].item()*tech_fraction["HydHyb"] \
                + df[df["Tech"]=="Bat"]["Bat"].item()*tech_fraction["Bat"]
        bat = np.append(bat, bat_val)

    EI_region = pd.DataFrame(data={"Region": reg, "Die": diesel, "BioDie": biodiesel,
                                   "Hyd": hydrogen, "Cat": grid, "Bat": bat})


    ###########################
    ### Energy Conversion Units
    ###########################

    # unit_conversion: e.g. MWh per Gallon of fuel
    # magic factor (efficiency): Used for Diesel/Biodiesel,
    # unit_after: Unit after conversion

    energy_sources ={
        "Die": {"unit_conversion": 0.0407, "magic_factor": 0.39, "unit_prefix": 1E+06, "unit_after": "MGal"},
        "BioDie": {"unit_conversion": 0.0366, "magic_factor": 0.39, "unit_prefix": 1E+06, "unit_after": "MGal"},
        "Cat": {"unit_conversion": 1, "magic_factor": 0.98, "unit_prefix": 1E+03, "unit_after": "GWh"},
        "Hyd": {"unit_conversion": 0.0333, "magic_factor": 0.5, "unit_prefix": 1E+06, "unit_after": "MkgH2"}, #Why not kg? 0.0333 MWh/kg preliminary
        "Bat": {"unit_conversion": 1, "magic_factor": 0.98, "unit_prefix": 1E+03, "unit_after": "GWh"},
    }
    for energy in energy_sources:
        energy_sources[energy]["denominator"] =  (energy_sources[energy]["unit_conversion"] \
                                                  * energy_sources[energy]["magic_factor"] \
                                                  * energy_sources[energy]["unit_prefix"])

    ###############################
    ### TonMiles and Energy by Yard
    ###############################
    
    tm_energy_per_yard = yards.copy()
    tm_energy_per_yard = tm_energy_per_yard.merge(links.loc[:, ["State", "TEMOA"]].drop_duplicates(), on="State").rename(columns={"TEMOA": "Region"})
    tm_energy_per_yard["SimTM (M)"] = yTM_y
    tm_energy_per_yard["RTM (M)"] = tm_energy_per_yard["SimTM (M)"] * factorup
    tm_energy_per_yard["GTM (M)"] = tm_energy_per_yard["RTM (M)"] * 1.3
    for energy in energy_sources:
        tm_energy_per_yard["%s (%s)" %(energy, energy_sources[energy]["unit_after"])] = \
        tm_energy_per_yard.apply(lambda x: x["GTM (M)"] * EI_region[EI_region["Region"]==x["Region"]][energy].item()/energy_sources[energy]["denominator"], axis=1)

    tm_energy_per_yard["Hyd (GWh)"] = tm_energy_per_yard["Hyd (MkgH2)"] * 1e+06 * energy_sources['Hyd']['unit_conversion']/1000
    tm_energy_per_yard["HydMWh/Day"] = tm_energy_per_yard["Hyd (GWh)"] * 1000 /365.
    tm_energy_per_yard["BatMWh/Day"] = tm_energy_per_yard["Bat (GWh)"] * 1000 /365.


    ###############################
    ### Add energy consumption (GJ) at th well (compared to at the tank)
    ### TODO: Add conversion factor from energy at tank to energy at well, currently using dummy values
    ###############################

    at_well_str = "at_the_well"
    energy_sources_at_well ={
        "Die": {"unit_conversion": 0, "unit_before": "MGal", "unit_after": "GJ"}, #"unit_conversion": 0.0407, "magic_factor": 0.39, "unit_prefix": 1E+06, "unit_after": "MGal"
        "BioDie": {"unit_conversion": 0, "unit_before": "MGal", "unit_after": "GJ"},
        "Cat": {"unit_conversion": 0, "unit_before": "GWh", "unit_after": "GJ"},
        "Hyd": {"unit_conversion": 0, "unit_before": "MkgH2", "unit_after": "GJ"},
        "Bat": {"unit_conversion": 0, "unit_before": "GWh", "unit_after": "GJ"},
    }

    for energy in energy_sources_at_well:
        tm_energy_per_yard["%s %s (%s)" %(energy, at_well_str, energy_sources_at_well[energy]["unit_after"])] = \
        tm_energy_per_yard["%s (%s)" %(energy, energy_sources_at_well[energy]["unit_before"])] * energy_sources_at_well[energy]["unit_conversion"]


    ######################################################################
    ### Create histogram of charging station size for battery and hydrogen
    ### Calculate number of recharging stations per size bin
    ######################################################################
    
    mhw_day_bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
    # TODO: Create input parameter for MWh/day


    ### Histogram for Hydrogen
    hydrogen_bins = []
    for i, mhw_day_bin in enumerate(mhw_day_bins):
        if i == 0:
            pass
        #if i == 1:
        #    break
        else:
            temp = tm_energy_per_yard[(tm_energy_per_yard["HydMWh/Day"] >= mhw_day_bins[i-1]) &\
                                     (tm_energy_per_yard["HydMWh/Day"] < mhw_day_bin)].groupby("Region")["HydMWh/Day"].count()
            temp.name = mhw_day_bin
            hydrogen_bins.append(temp)
    hydrogen_bins = pd.DataFrame(hydrogen_bins).fillna(0)
    hydrogen_bins.index.names = ["HydMWh/Day"]
    hydrogen_bins = pd.concat([hydrogen_bins], keys=[year], names=['year'])
    hydrogen_bins.to_csv("%s/energy_region_histogram_Hydrogen.csv" %(module6_output_path))

    ### Histogram for Battery
    battery_bins = []
    for i, mhw_day_bin in enumerate(mhw_day_bins):
        if i == 0:
            pass
        #if i == 1:
        #    break
        else:
            temp = tm_energy_per_yard[(tm_energy_per_yard["BatMWh/Day"] >= mhw_day_bins[i-1]) &\
                                      (tm_energy_per_yard["BatMWh/Day"] < mhw_day_bin)].groupby("Region")["BatMWh/Day"].count()
            temp.name = mhw_day_bin
            battery_bins.append(temp)
    battery_bins = pd.DataFrame(battery_bins).fillna(0)
    battery_bins.index.names = ["BatMWh/Day"]
    battery_bins = pd.concat([battery_bins], keys=[year], names=['year'])
    battery_bins.to_csv("%s/energy_region_histogram_Battery.csv" %(module6_output_path))

    #########################
    ### Histogram for Battery
    #########################

    #df = tm_energy_per_yard
    #low = int(np.floor(df["BatMWh/Day"].min()))
    #high = int(np.ceil(df["BatMWh/Day"].max()))
    #hist_bins = [i*1 for i in range(low, high)]
    #df["bins"] = pd.cut(df["BatMWh/Day"], bins=hist_bins)
    #df_bin = df.groupby(["Region", "bins"]).agg({"BatMWh/Day": pd.Series.count})
    #df_hist_bat = df_bin.pivot_table(index=["Region"], columns=['bins'], values="BatMWh/Day").reset_index().T
    #df_hist_bat.to_csv("%s/energy_region_histogram_Battery.csv" %(module6_output_path))


    ##########################
    ### Histogram for Hydrogen
    ##########################
    #df = tm_energy_per_yard.copy()
    #low = int(np.floor(df["HydMWh/Day"].min()))
    #high = int(np.ceil(df["HydMWh/Day"].max()))
    #hist_bins = [i*1 for i in range(low, high, 10)]
    #df["bins"] = pd.cut(df["HydMWh/Day"], bins=hist_bins)
    #df_bin = df.groupby(["Region", "bins"]).agg({"HydMWh/Day": pd.Series.count})
    #df_hist_hyd = df_bin.pivot_table(index=["Region"], columns=['bins'], values="HydMWh/Day").reset_index().T
    #df_hist_hyd.to_csv("%s/energy_region_histogram_Hydrogen.csv" %(module6_output_path))


    #############################
    ### Revenue TonMiles by State
    #############################

    lk_flows_per_state = links.loc[:, ["State", "TEMOA"]].merge(lkflows.loc[:, ["TMc_e (M)"]], left_index=True, right_index=True)
    tm_energy_per_state = pd.DataFrame(lk_flows_per_state.groupby("State")["TMc_e (M)"].sum()) * factorup
    tm_energy_per_state.columns = ["RTM_lkEst(M)"]

    tm_yd_per_state = pd.DataFrame(tm_energy_per_yard.groupby("State")["GTM (M)"].sum())
    tm_yd_per_state.columns = ["RTM_YdEst(M)"]
    tm_energy_per_state = tm_energy_per_state.merge(tm_yd_per_state, left_index=True, right_index=True, how="left").fillna(0).round(4)


    ###############################################
    ### Revenue TonMiles and Energy by Temoa Region
    ###############################################

    tm_energy_per_temoa = tm_energy_per_state.reset_index().merge(links.loc[:, ["State", "TEMOA"]], on="State", how="left").drop_duplicates()
    tm_energy_per_temoa = tm_energy_per_temoa.loc[:, ["TEMOA", "RTM_lkEst(M)", "RTM_YdEst(M)"]].groupby("TEMOA").sum()
    tm_energy_per_temoa.columns = ["rtm(Lk)(M)", "rtm(rCh)(M)"]

    tm_energy_grouped = tm_energy_per_yard.loc[:, ['Region', 'Die (MGal)', 'BioDie (MGal)', 'Cat (GWh)', 'Hyd (MkgH2)', 'Bat (GWh)',
                                                   'Die at_the_well (GJ)', 'BioDie at_the_well (GJ)', 'Cat at_the_well (GJ)',
                                                   'Hyd at_the_well (GJ)', 'Bat at_the_well (GJ)']].groupby("Region").sum()
    tm_energy_per_temoa = tm_energy_per_temoa.merge(tm_energy_grouped, left_index=True, right_index=True)


    #######################################################################################################
    ### Calculate TrainMiles, LocoMiles, TenderMiles in million miles, LocoHr and TenderHr in million hours
    #######################################################################################################

    ### Average Train Characteristics
    avg_train_characteristics = {"net_tons_train": 10708.2,
                                 "no_of_locos": 7,
                                 "no_of_tenders": 8,
                                 "avg_train_speed": 25} #mph

    tm_energy_per_temoa["TrnMi (M)"] = tm_energy_per_temoa["rtm(Lk)(M)"] / avg_train_characteristics["net_tons_train"]
    tm_energy_per_temoa["LocoMi (M)"] = tm_energy_per_temoa["TrnMi (M)"] * avg_train_characteristics["no_of_locos"]
    tm_energy_per_temoa["TndrMi (M)"] = tm_energy_per_temoa["TrnMi (M)"] * avg_train_characteristics["no_of_tenders"]
    tm_energy_per_temoa["LocoHr"] = tm_energy_per_temoa["LocoMi (M)"] * avg_train_characteristics["avg_train_speed"] # thousand hours
    tm_energy_per_temoa["TndrHr"] = tm_energy_per_temoa["TndrMi (M)"] * avg_train_characteristics["avg_train_speed"] # thousand hours


    ########################################################################################
    ### Calculate number of  & total hours of operation/year for Locos/Tender (for Module 9)
    ########################################################################################

    # Assuming 65 RTM (million) per year per loco, Following TA_PopShift_2020-v8, Sheet Mod 9
    # Calculated from RailData.xslx
    annual_mileage = 65 #(mil-RTM)

    ei_region_total = EI_region.copy().set_index("Region")
    ei_region_total["Tot"] = ei_region_total.sum(axis=1)

    energy_types = ["Die", "BioDie", "Hyd", "Cat", "Bat"]

    RTM_B = []
    for energy_type in energy_types:
        temp = tm_energy_per_temoa["rtm(Lk)(M)"] * ei_region_total[energy_type] / ei_region_total["Tot"] / 1000
        temp.name = energy_type
        RTM_B.append(temp)
    RTM_B = pd.DataFrame(RTM_B).T
    #RTM_B.sum(axis=1)*1000 # Mil-RTM for all techs

    # Calculate number of locos

    fleet_size_loco = RTM_B.copy()
    fleet_size_loco["Die"] = 1000 * RTM_B.sum(axis=1) * (tech_fraction["Diesel"] + tech_fraction["DieHyb"]) / annual_mileage
    fleet_size_loco["BioDie"] = 1000 * RTM_B.sum(axis=1) * (tech_fraction["BioDie"] + tech_fraction["BioHyb"]) / annual_mileage
    fleet_size_loco["Hyd"] = 1000 * RTM_B.sum(axis=1) * (tech_fraction["HydHyb"]) / annual_mileage
    fleet_size_loco["Cat"] = 0
    fleet_size_loco["Bat"] = 1000 * RTM_B.sum(axis=1) * (tech_fraction["Bat"]) / annual_mileage
    #fleet_size_loco


    # Calculate hours of locos
    # N_locos per region per tech * locohrs per region / N_locos for all techs
    fleet_hours_loco = fleet_size_loco.mul(tm_energy_per_temoa["LocoHr"], axis=0)
    fleet_hours_loco = fleet_hours_loco.div(fleet_size_loco.sum(axis=1), axis=0)
    fleet_hours_loco = fleet_hours_loco * 1000 # thousand hours to hours


    # Calculate number of tenders
    fleet_size_tender = fleet_size_loco.copy()
#    fleet_size_tender["Die"] = 9/7 * fleet_size_loco["Die"] * (tech_fraction["DieHyb"] / (tech_fraction["Diesel"] + tech_fraction["DieHyb"]))
#    fleet_size_tender["BioDie"] = 9/7 * fleet_size_loco["BioDie"] * (tech_fraction["BioHyb"] / (tech_fraction["BioDie"] + tech_fraction["BioHyb"]))
    fleet_size_tender["Die"] = 9/7 * 1000 * RTM_B.sum(axis=1) * tech_fraction["DieHyb"] / annual_mileage
    fleet_size_tender["BioDie"] = 9/7 * 1000 * RTM_B.sum(axis=1) * tech_fraction["BioHyb"] / annual_mileage
    fleet_size_tender["Hyd"] = 9/7 * fleet_size_loco["Hyd"]
    fleet_size_tender["Cat"] = 0
    fleet_size_tender["Bat"] = 9/7 * fleet_size_loco["Bat"]


    # Calculate hours of tenders
    fleet_hours_tender = fleet_size_tender.mul(tm_energy_per_temoa["TndrHr"], axis=0)
    fleet_hours_tender = fleet_hours_tender.div(fleet_size_tender.sum(axis=1), axis=0)
    fleet_hours_tender = fleet_hours_tender * 1000 # thousand hours to hours


    ###############################################
    ### Create a Dataframe with hours, size, RMT _B
    ###############################################


    ### Melt all input dataframes down to columns
    fleet_size_loco_melt = fleet_size_loco.reset_index().melt(value_vars=energy_types,
                                                              id_vars="TEMOA",
                                                              var_name="E_Source",
                                                              value_name="nLoco").rename(columns={"TEMOA": "Region"})
    fleet_hours_loco_melt = fleet_hours_loco.reset_index().melt(value_vars=energy_types,
                                                                id_vars="TEMOA",
                                                                var_name="E_Source",
                                                                value_name="LocoHr").rename(columns={"TEMOA": "Region"})
    fleet_size_tender_melt = fleet_size_tender.reset_index().melt(value_vars=energy_types,
                                                                  id_vars="TEMOA",
                                                                  var_name="E_Source",
                                                                  value_name="nTndr").rename(columns={"TEMOA": "Region"})
    fleet_hours_tender_melt = fleet_hours_tender.reset_index().melt(value_vars=energy_types,
                                                                    id_vars="TEMOA",
                                                                    var_name="E_Source",
                                                                    value_name="TndrHr").rename(columns={"TEMOA": "Region"})
    RTM_B_melt = RTM_B.reset_index().melt(value_vars=energy_types,
                                          id_vars="TEMOA",
                                          var_name="E_Source",
                                          value_name="RTM (B)").rename(columns={"TEMOA": "Region"})

    ### Merge

    fleet_size_hrs = fleet_size_loco_melt\
                    .merge(fleet_hours_loco_melt, on=["Region", "E_Source"], how="inner")\
                    .merge(fleet_size_tender_melt, on=["Region", "E_Source"], how="inner")\
                    .merge(fleet_hours_tender_melt, on=["Region", "E_Source"], how="inner")\
                    .merge(RTM_B_melt, on=["Region", "E_Source"], how="inner")
    fleet_size_hrs=fix_tech_nomenclature(fleet_size_hrs)

    ### Grouping

    fleet_size_hrs = fleet_size_hrs.sort_values(by=["Region"])
    array1 = list(fleet_size_hrs["Region"])

    data = np.array(fleet_size_hrs[['E_Source', 'nLoco', 'LocoHr', 'nTndr', 'TndrHr', 'RTM (B)']])
    fleet_size_hrs_sorted = pd.DataFrame(data=data, index=array1)
    fleet_size_hrs_sorted.columns = ['E_Source', 'nLoco', 'LocoHr', 'nTndr', 'TndrHr', 'RTM (B)']
    fleet_size_hrs_sorted.index.name = "Region"


    #####################
    #### traffic_flow.csv
    #####################

    # Static/Config file inputs
    # **Module 6 output**

    # energy_system_scenario   freight_demand_scenario   year   region   technology   **freight_ton_mile_travel**


    # Assuming revenue TM, Following TA_PopShift_2020-v8, Sheet Mod 9
    traffic_flows_for_Mod9 = RTM_B.copy()
    traffic_flows_for_Mod9 = traffic_flows_for_Mod9.reset_index().melt(value_vars=energy_types, id_vars="TEMOA",
                                                                       var_name="technology", value_name="freight_ton_mile_travel")
    traffic_flows_for_Mod9.rename(columns={"TEMOA": "region"}, inplace=True)
    traffic_flows_for_Mod9["freight_ton_mile_travel"] = traffic_flows_for_Mod9["freight_ton_mile_travel"] * 1e+9 #billion TM to TM

    #for key, value in config.items():
    #    traffic_flows_for_Mod9[key] = value
    traffic_flows_for_Mod9["energy_system_scenario"] = config["energy_system_scenario"]
    traffic_flows_for_Mod9["freight_demand_scenario"] = config["freight_demand_scenario"]
    traffic_flows_for_Mod9["year"] = year

    # rearrange columns
    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology', 'freight_ton_mile_travel']
    traffic_flows_for_Mod9 = traffic_flows_for_Mod9[cols]


    ##############
    #### train.csv
    ##############

    # Static/Config file inputs
    # **Module 6 output**
    #
    # energy_system_scenario   freight_demand_scenario   year   region   technology
    # **number_of_locomotives**   **number_of_tender_cars**   **locomotive_hours**   **tender_hours**
    # cost_per_locomotive   cost_per_tender   cost_per_locomotive_hour   cost_per_tender_hours

    # Following TA_PopShift_2020-v8, Sheet Mod 9
    train_for_Mod9 = fleet_size_loco.copy()
    train_for_Mod9 = train_for_Mod9.reset_index().melt(id_vars="TEMOA", value_vars=energy_types,
                                                       var_name="technology", value_name="number_of_locomotives")
    for name, df in zip(["number_of_tender_cars", "locomotive_hours", "tender_hours"],
                        [fleet_size_tender, fleet_hours_loco, fleet_hours_tender]):
        temp = df.reset_index().melt(value_vars=energy_types, id_vars="TEMOA",
                                     var_name="technology", value_name=name)
        train_for_Mod9 = train_for_Mod9.merge(temp, on=["TEMOA", "technology"])
    train_for_Mod9.rename(columns={"TEMOA": "region"}, inplace=True)

    #for key, value in config.items():
    #    train_for_Mod9[key] = value
    train_for_Mod9["energy_system_scenario"] = config["energy_system_scenario"]
    train_for_Mod9["freight_demand_scenario"] = config["freight_demand_scenario"]
    train_for_Mod9["year"] = year

    # rearrange columns
    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
            "number_of_locomotives", "number_of_tender_cars", "locomotive_hours", "tender_hours"]
    train_for_Mod9 = train_for_Mod9[cols]

    # Add static columns (empty for now - needs to be discussed with Module 9)
    #cols = ["cost_per_locomotive ($)", "cost_per_tender ($)", "cost_per_locomotive_hour ($)", "cost_per_tender_hour ($)"]
    #for col in cols:
    #    train_for_Mod9[col] = np.nan


    #################
    ### refueling.csv
    #################

    # Static/Config file inputs
    # **Module 6 output**
    # **Module 8 output**
    #
    # energy_system_scenario   freight_demand_scenario   year   region   technology
    # **number_of_charging_stations**   **operational_refueling_energy_use (GJ)**   **energy_refueled_to_tenders&locomotives (GJ)**
    # *cost_per_station*   *infrastructure_O&M_cost*

    # Following TA_PopShift_2020-v8, Sheet Mod 9
    # Assuming operational_refueling_energy_use (GJ) = energy_refueled_to_tenders&locomotives (GJ)
    # number_of_charging_stations, operational_refueling_energy_use (GJ) only for Hydrogen, Battery (E-Mail Tongchuan ARPA-e project: cost module input data display, 20/03/2023 16:53)


    #### Calculate energy for reach Temoa/Technology in GJ (required for Module 9)

    cols_GJ = {"Die (MGal)": "Die",
               "BioDie (MGal)": "BioDie",
               "Cat (GWh)": "Cat",
               "Hyd (MkgH2)":"Hyd",
               "Bat (GWh)": "Bat"}

    tm_energy_per_temoa_GJ = tm_energy_per_temoa.copy()
    tm_energy_per_temoa_GJ["Die (MGal)"] = tm_energy_per_temoa_GJ["Die (MGal)"] / energy_sources["Die"]["unit_conversion"] # MGal to GWh
    tm_energy_per_temoa_GJ["BioDie (MGal)"] = tm_energy_per_temoa_GJ["BioDie (MGal)"] / energy_sources["BioDie"]["unit_conversion"] # MGal to GWh

    tm_energy_per_temoa_GJ.loc[:, list(cols_GJ.keys())] = tm_energy_per_temoa_GJ.loc[:, list(cols_GJ.keys())] * 3600 #GWh to GJ
    tm_energy_per_temoa_GJ = tm_energy_per_temoa_GJ.rename(columns=cols_GJ)

    no_of_charging_stations = tm_energy_per_yard.groupby("Region")["Yard"].count()


    refueling_for_Mod9 = tm_energy_per_temoa_GJ.copy()
    refueling_for_Mod9 = refueling_for_Mod9.reset_index().melt(value_vars=energy_types, id_vars="TEMOA",
                                                               var_name="technology",
                                                               value_name="energy_refueled_to_tenders&locomotives (GJ)")
    refueling_for_Mod9 = refueling_for_Mod9.merge(no_of_charging_stations, left_on="TEMOA", right_index=True)
    refueling_for_Mod9.rename(columns={"TEMOA": "region", "Yard": "number_of_charging_stations"}, inplace=True)
    refueling_for_Mod9["operational_refueling_energy_use (GJ)"] = refueling_for_Mod9["energy_refueled_to_tenders&locomotives (GJ)"]

    # Set technologies to static = 0 for Die, BioDie, Cat
    mask = refueling_for_Mod9["technology"].isin(["Die", "BioDie", "Cat"])
    refueling_for_Mod9.loc[mask, ["number_of_charging_stations", "operational_refueling_energy_use (GJ)",
                                  "energy_refueled_to_tenders&locomotives (GJ)"]] = 0

    # Add columns from user_input
    #for key, value in config.items():
    #    refueling_for_Mod9[key] = value
    refueling_for_Mod9["energy_system_scenario"] = config["energy_system_scenario"]
    refueling_for_Mod9["freight_demand_scenario"] = config["freight_demand_scenario"]
    refueling_for_Mod9["year"] = year

    # rearrange columns
    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
           "number_of_charging_stations", "operational_refueling_energy_use (GJ)", "energy_refueled_to_tenders&locomotives (GJ)"]
    refueling_for_Mod9 = refueling_for_Mod9[cols]

    # Add static columns (empty for now - needs to be discussed with Module 9)
    #cols = ["cost_per_station ($)", "infrastructure_O&M_cost ($/year)"]
    #for col in cols:
    #    refueling_for_Mod9[col] = np.nan


    ##############
    ### energy.csv
    ##############

    # Static/Config file inputs
    # **Module 6 output**
    # **Module 7 output**
    #
    # energy_system_scenario   freight_demand_scenario   year   region   technology
    # **train_energy_consumption**   **train_energy_consumption_unit**
    # energy_consumption_at_the_well (GJ)
    # *upstream_CO2_emission_factor*
    # downstream_CO2_emission_factor   CO2_emission_factor_unit   upstream_CH4_emission_factor   downstream_CH4_emission_factor
    # CH4_emission_factor_unit


    cols_energy_dict = {'Die': "gallon",
                        'BioDie': "gallon",
                        'Cat': "kWh",
                        'Hyd': "kgH2",
                        'Bat': "kWh"}

    energy_for_Mod9 = tm_energy_per_temoa.copy()
    energy_for_Mod9 = energy_for_Mod9.iloc[:, 2:7]
    energy_for_Mod9.columns = [x.split(" ")[0] for x in energy_for_Mod9.columns]

    # Convert GWh to kWh and MGal to Gal
    energy_for_Mod9 = energy_for_Mod9 * 1e+6

    energy_for_Mod9 = energy_for_Mod9.reset_index().melt(value_vars=energy_types, id_vars="TEMOA",
                                                         var_name="technology", value_name="train_energy_consumption")
    energy_for_Mod9.rename(columns={"TEMOA": "region"}, inplace=True)

    energy_for_Mod9["train_energy_consumption_unit"] = energy_for_Mod9["technology"]
    energy_for_Mod9['train_energy_consumption_unit'] = energy_for_Mod9['train_energy_consumption_unit'].replace(cols_energy_dict)

    # Add energy consumption at the well
    energy_at_the_well_for_Mod9 = tm_energy_per_temoa.copy()
    energy_at_the_well_for_Mod9 = energy_at_the_well_for_Mod9.iloc[:, 7:12]
    energy_at_the_well_for_Mod9.columns = [x.split(" ")[0] for x in energy_at_the_well_for_Mod9.columns]

    energy_at_the_well_for_Mod9 = energy_at_the_well_for_Mod9.reset_index().melt(value_vars=energy_types, id_vars="TEMOA",
                                                                                 var_name="technology", value_name="energy_consumption_at_the_well (GJ)")
    energy_at_the_well_for_Mod9.rename(columns={"TEMOA": "region"}, inplace=True)

    energy_for_Mod9 = energy_for_Mod9.merge(energy_at_the_well_for_Mod9, on=["region", "technology"])

    # Add columns from user_input
    #for key, value in config.items():
    #    energy_for_Mod9[key] = value
    energy_for_Mod9["energy_system_scenario"] = config["energy_system_scenario"]
    energy_for_Mod9["freight_demand_scenario"] = config["freight_demand_scenario"]
    energy_for_Mod9["year"] = year

    # rearrange columns
    cols = ['energy_system_scenario', 'freight_demand_scenario', 'year', 'region', 'technology',
           "train_energy_consumption", "train_energy_consumption_unit", "energy_consumption_at_the_well (GJ)"]
    energy_for_Mod9 = energy_for_Mod9[cols]

    # Add static columns (empty for now - needs to be discussed with Module 9)
    #cols = ["energy_consumption_at_the_well (GJ)", "upstream_CO2_emission_factor", "downstream_CO2_emission_factor",
    #        "CO2_emission_factor_unit", "upstream_CH4_emission_factor", "downstream_CH4_emission_factor",
    #        "CH4_emission_factor_unit"]
    #for col in cols:
    #    energy_for_Mod9[col] = np.nan

    
    ###################
    ### Add year Column
    ###################
    
    for dataframe in [tm_energy_per_yard, tm_energy_per_state, tm_energy_per_temoa, fleet_size_hrs_sorted]:
        dataframe["year"] = year
        first_column = dataframe.pop("year")
        dataframe.insert(0, "year", first_column)

    ###########################################
    ### Save Module 6 output files for Module 9
    ###########################################
    
    traffic_flows_for_Mod9.to_csv("%s/traffic_flow_for_Mod9.csv" %module6_output_path, index=False)
    train_for_Mod9.to_csv("%s/train_for_Mod9.csv" %module6_output_path, index=False)
    refueling_for_Mod9.to_csv("%s/refueling_for_Mod9.csv" %module6_output_path, index=False)
    energy_for_Mod9.to_csv("%s/energy_for_Mod9.csv" %module6_output_path, index=False)


    ##############################
    ### Save Module 6 output files
    ##############################
    
    tm_energy_per_yard.to_csv("%s/tm_energy_per_charging_station.csv" %module6_output_path, index=False)
    tm_energy_per_state.to_csv("%s/tm_energy_per_state.csv" %module6_output_path, index=True)
    tm_energy_per_temoa.to_csv("%s/tm_energy_per_temoa.csv" %module6_output_path, index=True)
    fleet_size_hrs_sorted.to_csv("%s/fleet_size_hrs.csv" %module6_output_path, index=True)

    end = time.time()
    print(f"Run time for Module_6 = {round(end-start,ndigits = 2)} seconds")

    return 0