# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:08:51 2023

@author: Ishtiak Ahmed, Dr. Rupal Mittal, Andreas Weiss
"""

##########
### Import
##########

import pandas as pd
import numpy as np
import os
import time
import streamlit as st
import tempfile

###################
### Paths and Files
###################

static_input_path = "./Data/Static/"
module3_output_path = "./Data/Output/Module-3"

# TrafAssign
path_trafassign = "./Code/Module-4/TrafAssign/"

net_zones = pd.read_csv("%s/net_zones.csv" %static_input_path)  

#############
### Functions
#############

def demand_rearr(catg, a, ton_year, faf_rail_red,sunbelt_metro,nonsunbelt):  # sctg= commodity code, a = % increase in demand, year='tons_year'
    """Analyze population shift scenario and returns the total flow data.
    
    Keyword arguments:
    catg -- cat_group in the faf data, which will be looped over
    a -- Proportion change in population
    ton_year -- concatenation of year and economic scenario
    faf_rail_red --proportion of reduction of fossil fuels, i.e., coal and petrolium
    sunbelt_metro --faf zones corresponding to the sunbelt metropolitan areas
    nonsunbelt -- faf zones corresponding to the non-sunbelt metropolitan areas
    """
    cat_flow =  faf_rail_red[faf_rail_red['cat_grp']== catg]
    existing_flow = cat_flow.pivot_table(values=ton_year, index='dms_orig', columns= 'dms_dest',fill_value=0, aggfunc='sum')
    #index --> dest & column --> origin, the calling goes as column than row, so mat[i][j] is value in column i and row j. 
     
    #Dns = 0 #Estimated demand in non-sunbelt
    #Ds = 0 #Estimated demand in sunbelt
    df_sb = existing_flow.loc[:,sunbelt_metro] #subset dataframe for all destinations w/ sunbelt metro zones
    df_nsb = existing_flow.loc[:,nonsunbelt]
        
    Dns = df_nsb.sum().sum() #Estimated demand in non-sunbelt    
    Ds = df_sb.sum().sum() #Estimated demand in sunbelt
   # Ds_add = Ds*a #added demand to sunbelt states
    
    df_sb*= (1+a)
    
    df_nsb*= 1-(a*(Ds/Dns))
    df_final = pd.concat([df_sb, df_nsb], axis=1)
    return(df_final)


###  main function for Maritime activity reduction
def reduceMari(catg,a, ton_year,faf_rail_red):
    """Analyze maritime activity scenario and returns the total flow data.
    
    Keyword arguments:
    catg -- cat_group in the faf data, which will be looped over
    a -- Proportion change in maritime activities
    ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
    faf_rail_red --proportion of reduction of fossil fuels, i.e., coal and petrolium
    """
    cat_flow =  faf_rail_red[faf_rail_red['cat_grp_mod']== catg]
    existing_flow = cat_flow.pivot_table(values=ton_year, index='dms_orig', columns= 'dms_dest',
                                         fill_value=0, aggfunc='sum')
    
    if catg == 7.1:
        #print(catg, existing_flow.sum().sum())
        existing_flow *= (1-a)
    else: #all other commodity types will remain unchanged
        pass
    return(existing_flow)


###  All functions for agricultural shift scenario

### create dictionary to distribute demand for zones which already recieve agricultural products from North GP
def supp_1 (sctg,ton_year,south_gp,north_gp, faf_agri_nonimport,destrail): #different for each sctg type, each data year
    """Create dictionary to distribute demand for zones which already recieve agricultural products from North GP.
        
        It is a part of the agricultural shift function.
        Keyword arguments:
        sctg -- see FAF rail column sctg2 for cat_group == 1
        ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
        south_gp -- #Texas, Kansas, Oklahoma in great plain
        north_gp -- Nebraska, South & North Dakota in great plain
        faf_agri_nonimport -- non-importing agricultural prodict
        destrail -- destination rail zones ids
    """
    sctg_flow =  faf_agri_nonimport[faf_agri_nonimport['sctg2']== sctg]
    existing_flow = sctg_flow.pivot_table(values=ton_year, index='dms_orig', columns= 'dms_dest',fill_value=0, aggfunc='sum')
    dest_red=[]
    for i in south_gp:
        for j in destrail:
            try:
                flow = existing_flow.loc[i,j]
                if flow > 0:
                    if j not in dest_red: #gets the unique value of j for which there is a non-zero flow
                        dest_red.append(j)
            except:
                pass
    
    redistribut= {} #[destination][north_gp]--> flow from north_gp origin to destination
    redistribut_tot ={}
    dest_red_1 = [] #to check that the destination zones in dest_red has alternative flow of the same item from north gp
    for j in dest_red:
        k = 0
        for i in north_gp:
            try:
                flow = existing_flow.loc[i,j]
                if flow > 0:
                    if j not in redistribut:
                        redistribut[j] = {i:flow}
                    else:
                        if i not in redistribut[j]:
                            redistribut[j][i]=(flow)

                    k = k+ flow
            except:
                pass

        if j not in redistribut_tot:
            redistribut_tot[j]= (k)
        if k > 0:
            if j not in dest_red_1:
                    dest_red_1.append(j)
   
    supp_frac_dest_1 ={} #supp_frac_dest_1[desti][nouth gp origin]-->fraction of supply from that nouth gp to that destination
    for i in redistribut.keys(): #to be consistent, it should have used j instead of i
        for k in redistribut[i].keys():
            frac = redistribut[i][k]/redistribut_tot[i]
            if i not in supp_frac_dest_1:
                supp_frac_dest_1[i]={k:frac}
            else:
                if k not in supp_frac_dest_1[i]:
                     supp_frac_dest_1[i][k]=(frac)

    dest_red_2=[]
    for i in dest_red:
        if i not in dest_red_1:
            dest_red_2.append(i)
      
    return(supp_frac_dest_1,dest_red,dest_red_1,dest_red_2)


def supp_2(agr_sctg,ton_year,north_gp,faf_agri_nonimport):#different for each data year
    """Create dictionary to distribute demand for zones which does not recieve agricultural products from North GP, but will receive now.
        
        It is a part of the agricultural shift function. Deficit due to reduced supply from South will be met 
        by additional (new) supply from North. This is to make sure that agricultural production  shifts strictly
        from South GP to North GP regions.

        Keyword arguments:
        agr_sctg -- see FAF rail column sctg2 for cat_group == 1
        ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
        north_gp -- Nebraska, South & North Dakota in great plain
        faf_agri_nonimport -- non-importing agricultural prodict
    """
    supp_frac_dest_2 = {} #supp_frac_dest_2[sctg type][north_np origin] to get fraction of total supply from that origi
    #st = time.time()
    for sctg in agr_sctg: #this should also come from non-imports, as we assume shift of production within USA
        faf_agri_fromnorth = faf_agri_nonimport[(faf_agri_nonimport['dms_orig'].isin(north_gp)) & 
                                                (faf_agri_nonimport['sctg2']==sctg)]
        sum_rail = faf_agri_fromnorth.groupby(['dms_orig']).sum().reset_index()
     
        for i in sum_rail['dms_orig'].unique().tolist():
            ton_i = sum_rail[(sum_rail['dms_orig'] == i)][ton_year]
            r = float(ton_i/sum_rail[ton_year].sum())
          
            if sctg not in supp_frac_dest_2:
                supp_frac_dest_2[sctg]= {i:r}
            else:
                if i not in supp_frac_dest_2[sctg]:
                    supp_frac_dest_2[sctg][i]= (r)
    #en = time.time()
    return (supp_frac_dest_2)


def agricultural_shift(sctg,ton_year,south_gp,north_gp,a,destrail,originrail,faf_agri_nonimport):
    """Shift non-importing agricultural products from South to North.
    
    It is a part of the agricultural shift function.
    Keyword arguments:
    sctg -- see FAF rail column sctg2 for cat_group == 1
    ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
    south_gp -- #Texas, Kansas, Oklahoma in great plain
    north_gp -- Nebraska, South & North Dakota in great plain
    a -- Proportion shift in agriculture productions
    destrail --destination zone ids
    originrail --origin zone ids
    faf_agri_nonimport -- non-importing agricultural prodict
    """
    agr_sctg=[1,2,3,4,5,6,7,8,9] 
    OD_flow= pd.DataFrame(0.00,index=destrail, columns =originrail)
    
    sctg_flow =  faf_agri_nonimport[faf_agri_nonimport['sctg2']== sctg]
    existing_flow = sctg_flow.pivot_table(values=ton_year, index='dms_orig', 
                                          columns= 'dms_dest',fill_value=0, aggfunc='sum')
    modified_flow = existing_flow.copy()
    
    suppl_fact_1, dest, dest_set_1, dest_set_2 = supp_1(sctg,ton_year,south_gp,north_gp,faf_agri_nonimport,destrail)
    
    suppl_fact_2 = supp_2(agr_sctg,ton_year,north_gp,faf_agri_nonimport)
    
    
    red_dict = {}  
    #st = time.time()
    for j in dest:
        sm = 0

        for i in south_gp:
            try:
                flow = existing_flow.loc[i,j]
                if flow > 0:
                    red =  float(existing_flow.loc[i,j]*a)
                    modified_flow.loc[i,j] = existing_flow.loc [i,j] - red
                    OD_flow[i][j] = OD_flow[i][j] + modified_flow[i][j]
                    sm = sm+red
            except:
                pass
        if j not in red_dict:
            red_dict[j] = sm
    #en = time.time()

    #st = time.time()

    for j in red_dict.keys():
        total_add =float(red_dict[j])
        
        if j in dest_set_1:
            for i in north_gp:
                try:
                    add = float(total_add*suppl_fact_1[j][i])
                    modified_flow.loc[i,j] = existing_flow.loc[i,j] + add
                    OD_flow.loc[i,j] = OD_flow.loc[i,j]  + modified_flow.loc[i,j]
                    #print(j,total_add, add)
                except:
                    pass

        if j in dest_set_2:
            for i in north_gp:
                try:
                    add = float(total_add*suppl_fact_2[sctg][i]) #sctg type ==2
                    modified_flow.loc[i,j] = existing_flow.loc[i,j] + add
                    OD_flow.loc[i,j] = OD_flow.loc[i,j]  + OD_flow.loc[i,j] 
                    #print(j,total_add, add)
                except:
                    pass

    #en = time.time()
    
    #st = time.time()

    for j in destrail:
        for i in originrail:
            if i not in south_gp:
                try:
                    OD_flow.loc[i,j]  = modified_flow.loc[i,j]
                except:
                    pass
    #en = time.time()

    return(OD_flow)


def distribute_agri_import(df_agri_import, ton_year):
    """Keep the imported agricultural flow the same as before
    """
    agri_import = df_agri_import.pivot_table(values = ton_year, index='dms_orig', 
                                             columns= 'dms_dest',fill_value=0, aggfunc='sum')
    return (agri_import)


def distribute_other(catg, df_rail,ton_year):
    """keep the other categories (non-agricultural)  same as before
    """
    cat_flow =  df_rail[df_rail['cat_grp']== catg]
    existing_flow = cat_flow.pivot_table(values=ton_year, index='dms_orig', 
                                         columns= 'dms_dest',fill_value=0, aggfunc='sum')
    return (existing_flow)


###  All main functions for the agricultural reduction scenario
def supp_1_red (sctg,ton_year,south_gp,non_south_orig,faf_agri_nonimport,faf_agri_import,destrail): #different for each sctg type, each data year
    """creat dictionary to distribute demand for zones which already recieve agricultural products from North GP.
    
    Keyword arguments:
    sctg -- see FAF rail column sctg2 for cat_group == 1
    ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
    south_gp -- #Texas, Kansas, Oklahoma in great plain
    non_south_orig -- zones not in south great plain
    faf_agri_nonimport -- non-importing agricultural products
    faf_agri_import -- importing agricultural products
    destrail --destination zone ids
    """
    sctg_flow =  faf_agri_nonimport[faf_agri_nonimport['sctg2']== sctg]
    existing_flow = sctg_flow.pivot_table(values=ton_year, index='dms_orig', columns= 'dms_dest',fill_value=0, aggfunc='sum')
    
    dest_red=[]
    for i in south_gp:
        for j in destrail:
            try:
                flow = existing_flow.loc[i,j]
                if flow > 0:
                    if j not in dest_red:
                        dest_red.append(j)
            except:
                pass
    
    import_flow = faf_agri_import.pivot_table(values = ton_year, index='dms_orig', 
                                          columns= 'dms_dest',fill_value=0, aggfunc='sum')
    redistribut= {} #[destination][non_south_orig]--> flow from non_south_orig origin to destination
    redistribut_tot ={}
    #dest_red_1 = [] #to check that the destination zones in dest_red has alternative flow of the same item from north gp
    
    for j in dest_red:
        k = 0
        for i in non_south_orig:
            try:
                flow = import_flow.loc[i,j]
                if flow > 0:
                    if j not in redistribut:
                        redistribut[j] = {i:flow}
                    else:
                        if i not in redistribut[j]:
                            redistribut[j][i]=(flow)

                    k = k+ flow
            except:
                pass

        if j not in redistribut_tot:
            redistribut_tot[j]= (k)

    supp_frac_dest_1 ={} #supp_frac_dest_1[desti][nouth gp origin]-->fraction of supply from that nouth gp to that destination
    for i in redistribut.keys():
        for k in redistribut[i].keys():
            frac = redistribut[i][k]/redistribut_tot[i]
            if i not in supp_frac_dest_1:
                supp_frac_dest_1[i]={k:frac}
            else:
                if k not in supp_frac_dest_1[i]:
                     supp_frac_dest_1[i][k]=(frac)
            
    return(supp_frac_dest_1,dest_red)


### shift agri prod (non imports) from South to North
def agricultural_red(sctg,ton_year,south_gp,non_south_orig,a,destrail,originrail,faf_agri_nonimport,faf_agri_import):
    """Shift agri prod (non imports) from South to North.
    
    Keyword arguments:
    sctg -- see FAF rail column sctg2 for cat_group == 1
    ton_year -- concatenation of year and economic scenario to read the appropriate column in the faf data
    south_gp -- #Texas, Kansas, Oklahoma in great plain
    non_south_orig -- zones not in south great plain
    destrail --destination zone ids
    originrail -- origin zone ids
    faf_agri_nonimport -- non-importing agricultural products
    faf_agri_import -- importing agricultural products
    """
    OD_flow= pd.DataFrame(0.00,index=destrail, columns =originrail)
    
    sctg_flow =  faf_agri_nonimport[faf_agri_nonimport['sctg2']== sctg]
    existing_flow = sctg_flow.pivot_table(values=ton_year, index='dms_orig', 
                                          columns= 'dms_dest',fill_value=0, aggfunc='sum')
    modified_flow = existing_flow.copy()
    
    suppl_fact_1, dest = supp_1_red(sctg,ton_year,south_gp,non_south_orig,faf_agri_nonimport,faf_agri_import,destrail)
    
    
    red_dict = {}   
    for j in dest:
        sm = 0

        for i in south_gp:
            try:
                flow = existing_flow.loc[i,j]
                if flow > 0:
                    red =  float(existing_flow.loc[i,j]*a)
                    modified_flow.loc[i,j] = existing_flow.loc[i,j] - red
                    OD_flow.loc[i,j] = OD_flow.loc[i,j] + modified_flow.loc[i,j]
                    sm = sm+red
            except:
                pass
        if j not in red_dict:
            red_dict[j] = sm


    for j in red_dict.keys():
        total_add =float(red_dict[j])
 
        for i in non_south_orig:
            try:
                add = float(total_add*suppl_fact_1[j][i])
                modified_flow.loc[i,j] = existing_flow.loc[i,j] + add
                OD_flow.loc[i,j] = OD_flow.loc[i,j] + modified_flow.loc[i,j]
                #print(j,total_add, add)
            except:
                pass

    for j in destrail:
        for i in originrail:
            if i not in south_gp:
                try:
                    OD_flow.loc[i,j] = modified_flow.loc[i,j]
                except:
                    pass

    return(OD_flow)


### keeps the imported agricultural flow the same as before
def distribute_agri_import_red(df_agri_import, ton_year):
    
    agri_import = df_agri_import.pivot_table(values = ton_year, index='dms_orig', 
                                             columns= 'dms_dest',fill_value=0, aggfunc='sum')
    return (agri_import)


### keeps the other categories (non-agricultural)  same as before
def distribute_other_red(catg, df_rail, ton_year):
    cat_flow =  df_rail[df_rail['cat_grp']== catg]
    existing_flow = cat_flow.pivot_table(values=ton_year, index='dms_orig', 
                                         columns= 'dms_dest',fill_value=0, aggfunc='sum')
    return (existing_flow)


###  matrix to vector conversion
def generate_net_flows(data):

    # Preprocessing
   
    net_flows = []

    for i in range(len(net_zones)):
        o_mtx = net_zones.iloc[i, 3]
        o_pct = net_zones.iloc[i, 12]
        o_faf = net_zones.iloc[i, 2]
        for j in range(len(net_zones)):
            d_mtx = net_zones.iloc[j, 3]
            d_pct = net_zones.iloc[j, 12]
            d_faf = net_zones.iloc[j, 2]
            data_ij = data.iloc[o_mtx-1,d_mtx-1]
            #print(i, j, o_mtx, d_mtx, data_ij)
            f_mtx = data_ij * o_pct * d_pct
            if f_mtx > 1 and o_faf != d_faf:
                o_zon = net_zones.iloc[i, 0]
                o_fra = net_zones.iloc[i, 6]
                o_net = net_zones.iloc[i, 7]
                d_zon = net_zones.iloc[j, 0]
                d_fra = net_zones.iloc[j, 6]
                d_net = net_zones.iloc[j, 7]
                net_flows.append([o_zon, d_zon, o_faf, d_faf, o_net, d_net, o_fra, d_fra, f_mtx])
    df_net_flows = pd.DataFrame (net_flows, columns =
                                 ["zOrig", "zDest", "FAF_O", "FAF_D", "netNodeO",
                                  "netNodeD", "FRA_O", "FRA_D",\
            "fTons (K)"]).sort_values("fTons (K)", ascending=False)

    decimals = 6   
    df_net_flows['fTons (K)'] = df_net_flows['fTons (K)'].apply(
        lambda x: round(x, decimals)) 
    return(df_net_flows)


### Function to generate total flows
def create_total_flow(years, freight_demand_scenario, econ_scn, fossilfuel_reduction, freight_demand_fraction_change):
    """Generate total flows for each year for the given freight demand scenario.
    
    Keyword arguments:
    years -- Analysis years
    freight_demand_scenario -- e.g., population or agricultural shift or reduction in maritime or agricultural activities
    fossilfuel_reduction -- data for coal and petrolium reduction
    freight_demand_fraction_change -- change (proportion) for the given freight_demand_scenario
    """
    if econ_scn == 'Baseline (business as usual)':
        ton_year = 'tons' + '_' + str(years)
    elif econ_scn == 'Low (pessimistic)':
        ton_year = 'tons' + '_' + str(years) + '_' + str('low')
    elif econ_scn == 'High (optimistic)':
        ton_year = 'tons' + '_' + str(years) + '_' + str('high') 
        
    #define column names for the faf_rail database        
    colnames=['dms_orig', 'dms_dest', 'cat_grp', 'trade_type', 'sctg2',ton_year,'cat_grp_mod']   
    
    #read faf_rail database
    faf_rail = pd.read_csv(f'{static_input_path}FAF5.3_alltrades_byrail_7_Cat.csv',usecols=colnames)
    originrail = faf_rail['dms_orig'].unique().tolist() #all origin faf zones with rail mode
    originrail.sort()
    destrail = faf_rail['dms_dest'].unique().tolist() #all destination faf zones with rail mode
    destrail.sort()
    #sctgrail = faf_rail['sctg2'].unique().tolist() #all commodity types shipped by rail mode
    catrail = faf_rail['cat_grp'].unique().tolist() #all category types shipped by rail mode;used in scen 2,3 & 4
    agr_sctg = faf_rail[faf_rail['cat_grp']==1]['sctg2'].unique().tolist() #used in scen 3 & 4
    agr_sctg.sort() #sctg commodity types in category 1 (agricultural) #used in scen 3 & 4
    
    coal_reduce = fossilfuel_reduction.iloc[0][int((years - 2025)/5)]
    petro_reduce = fossilfuel_reduction.iloc[1][int((years - 2025)/5)]

    
    #multiply faf_rail ton_year column by 1-a, where a is the reduction in fossil fuel
    red_ff = np.where(faf_rail['cat_grp_mod'] == 3.1, (1-coal_reduce), 
                      np.where(faf_rail['cat_grp_mod'] == 3.2, (1-petro_reduce),1)
                      )
    faf_rail_red = pd.concat(
        [faf_rail[['dms_orig','dms_dest','cat_grp','trade_type','sctg2','cat_grp_mod']],
         faf_rail[ton_year].multiply(red_ff,axis=0)], axis=1
        )
    
    #faf zones corresponding to the sunbelt metropolitan areas
    #This input is only for pop shift
    sunbelt_metro = [11,50,41,42,61,62,63,64,65,81,122,123,124,131,132,201,202,221,222,223,280,371,372,373,350,321,401,402,451,
                     452,471,472,473,481,482,483,484,485,486,487,488,491] #used in scen 1
    nonsunbelt = list(set(destrail) - set(sunbelt_metro)) #non sunbelt zone numbers
    
    
    #the next four lines are only for Agricultural shift and reduction (sc = 3 & 4) except  2nd line is not used for sc = 4
    
    South_GP = [481,482,483,484,485,486,487,488,489,491,499,201,202,203,401,402,409] #Texas, Kansas, Oklahoma in great plain
    North_GP = [311,319,360,380] #Nebraska, South & North Dakota in great plain
    
    
    #required dataframe. becomes too clumsy if I define these inside the function
    faf_agri_nonimport = faf_rail_red[(faf_rail_red['cat_grp'] == 1) & (faf_rail_red['trade_type'] != 2)]
    faf_agri_import = faf_rail_red[(faf_rail_red['cat_grp'] == 1) & (faf_rail_red['trade_type'] == 2)] 
    
    #the following for loop is only for sc = 4
    Non_South_Orig = []
    for i in originrail:
        if i not in South_GP:
            if i not in Non_South_Orig:
                Non_South_Orig.append(i)
    #create an empty dataframe to store the total flow output
    total_flow = pd.DataFrame(0.00,columns =originrail,index=destrail) #empty matrix, will hold the total flow for all categories            
    
    #Run function for population shift scenario
    if freight_demand_scenario == "Population Shift":
        for i in catrail:
            OD_flow = demand_rearr(i, freight_demand_fraction_change, ton_year,faf_rail_red,sunbelt_metro,nonsunbelt) #sctg and %change can be inlcuded as tuple if we have different % for different commodity
            total_flow = total_flow + OD_flow
            del (OD_flow)
            
    #Run function for maritime activity reduction scenario
    elif freight_demand_scenario == "Maritime Activity Reduction":
        for i in faf_rail_red['cat_grp_mod'].unique().tolist():
            OD_flow = reduceMari(i, freight_demand_fraction_change, ton_year,faf_rail_red)
            total_flow = total_flow + OD_flow
            del (OD_flow)        
                
    #Run function for Agriculatural shift           
    elif freight_demand_scenario == "Agricultural Shift":
        total_flow_agri = pd.DataFrame(0.00,index=destrail, columns =originrail)
        
        for i in catrail:
            if i ==1:
                for sctg in agr_sctg:
                    flow = agricultural_shift(sctg, ton_year,South_GP,North_GP,freight_demand_fraction_change,destrail,originrail,faf_agri_nonimport)
                    total_flow_agri = total_flow_agri+flow
                import_flow = distribute_agri_import(faf_agri_import, ton_year)
                total_flow_agri=total_flow_agri+import_flow
                total_flow=total_flow + total_flow_agri

            if i !=1:
                flow = distribute_other(i,faf_rail_red,ton_year)
                total_flow = total_flow + flow
                
     #Run function for Agriculatural reduction           
    elif freight_demand_scenario == "Agricultural Reduction":
        total_flow_agri = pd.DataFrame(0.00,index=destrail, columns =originrail)
        for i in catrail:
            if i ==1:
                for sctg in agr_sctg:
                    flow = agricultural_red(sctg, ton_year,South_GP,Non_South_Orig,freight_demand_fraction_change,destrail,originrail,faf_agri_nonimport,faf_agri_import)
                    total_flow_agri = total_flow_agri+flow
                import_flow = distribute_agri_import_red(faf_agri_import, ton_year)
                total_flow_agri=total_flow_agri+import_flow
                total_flow=total_flow + total_flow_agri

            if i !=1:
                flow = distribute_other_red(i,faf_rail_red,ton_year)
                total_flow = total_flow + flow
    
    net_flows = generate_net_flows(total_flow)
    with tempfile.NamedTemporaryFile(mode="w+",delete=False,dir= './Data/Output/Module-3',suffix='.txt'):
        net_flows.to_csv("odflows.txt", sep="\t", header=None, index=False)
    #net_flows.to_csv("%s/odflows.txt" %(path_trafassign), sep="\t", header=None, index=False)
    #end = time.time()
    return net_flows
    #return total_flow



