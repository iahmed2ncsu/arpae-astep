# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 13:32:08 2023

@author: Ishtiak
"""

import streamlit as st
import numpy as np
import math as m
import pandas as pd
import calendar
from calendar import monthrange
import plotly.express as px

# %% functions
@st.cache_data
def convert_df(df):
    # Caches the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

# user input sliders for monthly distribution
def month_sliders(keylist):
    st.markdown(""" ### Monthly distribution by %""")
    MoY = [0]*12
    MoY[0] = st.slider('January',min_value=0,max_value=100,step=1,value=6,key=keylist[0])
    MoY[1] = st.slider('February',min_value=0,max_value=100,step=1,value=8,key=keylist[1])
    MoY[2] = st.slider('March',min_value=0,max_value=100,step=1,value=12,key=keylist[2])
    MoY[3] = st.slider('April',min_value=0,max_value=100,step=1,value=8,key=keylist[3])
    MoY[4] = st.slider('May',min_value=0,max_value=100,step=1,value=9,key=keylist[4])
    MoY[5] = st.slider('June',min_value=0,max_value=100,step=1,value=8,key=keylist[5])
    MoY[6] = st.slider('July',min_value=0,max_value=100,step=1,value=9,key=keylist[6])
    MoY[7] = st.slider('August',min_value=0,max_value=100,step=1,value=7,key=keylist[7])
    MoY[8] = st.slider('September',min_value=0,max_value=100,step=1,value=9,key=keylist[8])
    MoY[9] = st.slider('October',min_value=0,max_value=100,step=1,value=12,key=keylist[9])
    MoY[10] = st.slider('November',min_value=0,max_value=100,step=1,value=7,key=keylist[10])
    MoY[11] = st.slider('December',min_value=0,max_value=100,step=1,value=5,key=keylist[11])
    if sum(MoY) != 100:
        st.header('Please verify your values sum to 100%') 
    return MoY

# user input sliders for weekday distributions
def day_sliders(keylist):
    st.markdown(""" ### Weekday distribution by %""")
    DoW = [0]*12
    DoW[0] = st.slider('Sunday',min_value=0,max_value=100,step=1,value=10,key=keylist[0])
    DoW[1] = st.slider('Monday',min_value=0,max_value=100,step=1,value=13,key=keylist[1])
    DoW[2] = st.slider('Tuesday',min_value=0,max_value=100,step=1,value=15,key=keylist[2])
    DoW[3] = st.slider('Wednesday',min_value=0,max_value=100,step=1,value=15,key=keylist[3])
    DoW[4] = st.slider('Thursday',min_value=0,max_value=100,step=1,value=22,key=keylist[4])
    DoW[5] = st.slider('Friday',min_value=0,max_value=100,step=1,value=15,key=keylist[5])
    DoW[6] = st.slider('Saturday',min_value=0,max_value=100,step=1,value=10,key=keylist[6])
    if sum(DoW) != 100:
        st.header('Please verify your entered values sum to 100%')
    return DoW

# user input sliders for hourly distributions
def hour_sliders(keylist):
    st.markdown(""" ### Hourly distribution by %""")
    HoD = [0]*24
    HoD[0] = HoD[1] = HoD[2] = st.slider('0:00 - 3:00',min_value=0,max_value=100,step=1,value=5,key=keylist[0])/3
    HoD[3] = HoD[4] = HoD[5] = st.slider('3:00 - 6:00',min_value=0,max_value=100,step=1,value=5,key=keylist[1])/3
    HoD[6] = HoD[7] = HoD[8] = st.slider('6:00 - 9:00',min_value=0,max_value=100,step=1,value=20,key=keylist[2])/3
    HoD[9] = HoD[10] = HoD[11] = st.slider('9:00 - 12:00',min_value=0,max_value=100,step=1,value=20,key=keylist[3])/3
    HoD[12] = HoD[13] = HoD[14] = st.slider('12:00 - 15:00',min_value=0,max_value=100,step=1,value=15,key=keylist[4])/3
    HoD[15] = HoD[16] = HoD[17] = st.slider('15:00 - 18:00',min_value=0,max_value=100,step=1,value=15,key=keylist[5])/3
    HoD[18] = HoD[19] = HoD[20] = st.slider('18:00 - 21:00',min_value=0,max_value=100,step=1,value=10,key=keylist[6])/3
    HoD[21] = HoD[22] = HoD[23] = st.slider('21:00 - 24:00',min_value=0,max_value=100,step=1,value=10,key=keylist[7])/3
    if round(sum(HoD)) != 100:
        st.header('Please verify your entered values sum to 100%') 
    return HoD

# train arrival/departure distribution for each hour of the year
def distribution(year:int,trns:int,MoY:list,DoW:list,HoD:list):
    distr = []
    for month in range(0,12):
        for day in range(0,monthrange(year,month+1)[1]):
            if day == 0: # if it's the first day of the month
                wkday = monthrange(year,month+1)[0] # initialize the weekday
            else: # else if not the first day of the month
                if wkday > 6: # if yesterday was Saturday (last day of the week)
                    wkday = 0 # reset the weekday back to Sunday (first day of the week)
            D = DoW[wkday]/len([1 for i in calendar.monthcalendar(year,month+1) if i[6] != wkday]) # distribution for weekday
            for hour in range(0,24):
                distr.append(trns*(MoY[month]/100)*(D/100)*(HoD[hour]/100))
            wkday += 1 # set to next weekday before repeating loop
    distr = [x*(trns/sum(distr)) for x in distr]
    return distr

@st.cache_data
def gen_np_seed(mu,cv):
    return np.random.randint(99999)
# Produce demand profile with desired time interval from list of sequential charging events
def generate_demand_profile(events,interval):
    a = int(8760*(60/interval))
    b = int(60/interval)
    demand = [0]*a
    for start,end in events:
        start_int = int(start*b)
        end_int = int(end*b)
        for i in range(start_int, end_int):
            if i < len(demand):
                demand[i] += 1
    return demand
    
# Averages the demand profile to a larger time interval
def average_demand_profile(inputlist,newinterval,oldinterval):
    outputlist = []
    a = int(newinterval/oldinterval)
    for i in range(0, len(inputlist),a):
        average = sum(inputlist[i:i+a])/a
        outputlist.append(average)
    return outputlist
@st.cache_data
def bes(level):
    p = []
    e = []
    for i in range(len(dfdmnd)):
        if dfdmnd.iloc[i,1] > (level*avgdmnd):
            if len(e) > 0:
                p.append((dfdmnd.iloc[i,1]-(level*avgdmnd))/chgeff/onebeseff) # power out plus losses
                e.append((dfdmnd.iloc[i,1]-(level*avgdmnd))/4/chgeff/onebeseff+e[i-1]) # energy out plus losses
            else:
                p.append((dfdmnd.iloc[i,1]-(level*avgdmnd))/chgeff/onebeseff) # power out plus losses
                e.append((dfdmnd.iloc[i,1]-(level*avgdmnd))/4/chgeff/onebeseff) # energy out plus losses
        elif dfdmnd.iloc[i,1] < (level*avgdmnd):
            if len(e) > 0:
                if e[i-1] > 0:
                    chg = -min((level*avgdmnd-dfdmnd.iloc[i,1]),e[i-1]*4)
                    p.append(chg/onebeseff)
                    e.append(chg/4*onebeseff+e[i-1])
                else:
                    p.append(0)
                    e.append(0)
            else:
                p.append(0)
                e.append(0)
        else:
            if len(e) > 0:
                p.append(0)
                e.append(e[i-1])
            else:
                p.append(0)
                e.append(0)
    return p, e
# Lemmon, E. W., Huber, M. L., & Leachman, J. W. (2008).
# Revised Standardized Equation for Hydrogen Gas Densities for Fuel Consumption Applications.
# Journal of Research of the National Institute of Standards and Technology, 113(6), 341-350.
# https://doi.org/10.6028/jres.113.028
def H2density(T,P):
    # Equation constants
    a = [0.05888460,-0.06136111,-0.002650473,0.002731125,0.001802374,
        -0.001150707,0.9588528e-4,-0.1109040e-6,0.1264403e-9]
    b = [1.325,1.87,2.5,2.8,2.938,3.14,3.37,3.75,4.0]
    c = [1.0,1.0,2.0,2.0,2.42,2.63,3.0,4.0,5.0]
    T = T+273.15 # Celsius -> Kelvin
    P = P*0.1 # bar -> MPa
    # Molar gas constant
    R = 8.314472 # J/mol/K
    # Molar mass of H2 gas
    M = 2.01588 # g/mol H2
    # Calculate compressibility factor
    sum = 0.0
    for i in range(0,9):
        A = (100/T)**b[i]
        B = P**c[i]
        sum += a[i]*A*B
    Z = 1 + sum
    rho_molL = P*1e3/(Z*R*T)
    rho_kgm3 = rho_molL*M
    return [rho_molL, rho_kgm3, Z]


# %% Streamlit page configuration
version = 4.2
#set page config
st.set_page_config(page_title=None, page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="auto", menu_items=None)

#define tab names and numbers

tab1, tab2, tab3, tab4, tab5 = st.tabs(["About", "Train Schedule","Demand Profile", "Battery-electric", "Hydrogen"])
# %% About page

page_title = "A-STEP: Achieving Sustainable Train Energy Pathways"
body = "A-STEP: Achieving Sustainable Train Energy Pathways"
subhead = "Module 8: Infrastructure Requirements"

with tab1:
    #st.set_page_config(layout='wide')
    #st.set_page_config(page_title=page_title)
    st.header(body)
    st.subheader(subhead)

# %% Train Schedule page  
with tab2:
    tab21,tab22,tab23,tab24 = st.tabs(["Arrival Parameters", "Departure Parameters", "Arrival/Departure Distribution","Arrival/Departure Schedule"])
    with tab21:
        st.title(':train: Tender Arrival/Departure Schedule Generator :clock5:')
   
        year = st.slider('Year',min_value=2020,max_value=2050,step=1,value=2030,key='a')
        design = st.radio('Technology',['Electric','Hydrogen'])
        if design == 'Electric':
            tndrnrg = st.number_input('Energy per battery tender, MWh',value=10,key='b')
            GWhyr = st.number_input('Target GWh/year',value=70,key='c')
        elif design == 'Hydrogen':
            tndrkgH2 = st.number_input('Hydrogen per hydrogen tender, kgH2',value=800,key = 'd')
            tndrnrg = tndrkgH2*0.0333
            GWhyr = st.number_input('Target GWh/year',value=190,key = 'e')
        arrtndrs = st.number_input('Tenders per train',value=2,key='f')
        st.metric('Suggested train arrivals per year',value=round(GWhyr/(tndrnrg*arrtndrs/1e3)))
        arrtrns = st.number_input('Train arrivals per year',value=round(GWhyr/(tndrnrg*arrtndrs/1e3)),max_value=17520,key='g')
    
        col1, col2, col3 = st.columns(3)
        with col1:
            AMoY = month_sliders(range(3,15))
            #st.write(AMoY)
    
        with col2:
            ADoW = day_sliders(range(16,23))
            #st.write(ADoW)
    
        with col3:
            AHoD = hour_sliders(range(24,32))
            #st.write(AHoD)
    with tab22:
        st.title(':train: Tender Arrival/Departure Schedule Generator :clock5:')
        st.metric('Year',year)
        deptrns = st.number_input('Train departures per year',value=round(GWhyr/(tndrnrg*arrtndrs/1e3)),max_value=17520,key = 'h')
        deptndrs = st.number_input('Tenders per train',step=1,value=2,key = 'i')
        col1, col2, col3 = st.columns(3)
    
        with col1:
            DMoY = month_sliders(range(32,44))
            #st.write(DMoY)
    
        with col2:
            DDoW = day_sliders(range(44,51))
            #st.write(DDoW)
    
        with col3:
            DHoD = hour_sliders(range(51,59))
            #st.write(DHoD)
    with tab23:
        st.title(':train: Tender Arrival/Departure Schedule Generator :clock5:')
        arrivals = distribution(year,arrtrns,AMoY,ADoW,AHoD)
        departures = distribution(year,deptrns,DMoY,DDoW,DHoD)
        col1, col2 = st.columns(2)
    
        with col1:
            st.header('Hourly Train Arrival Distribution')
            st.bar_chart(arrivals)
            st.metric('Total Train Arrivals',round(sum(arrivals)))
            st.metric('Total Hours',len(arrivals))
    
        with col2:
            st.header('Hourly Train Departure Distribution')
            st.bar_chart(departures)
            st.metric('Total Train Arrivals',round(sum(departures)))
            st.metric('Total Hours',len(arrivals))
    
        # random.normal(mu, sigma, size=None)
        # mu is the mean of the distribution
        # sigma is the standard deviation of the distribution (must be non-negative)
        # optional input. defines how many samples are drawn, defaults to single value return
    with tab24:
        st.title(':train: Tender Arrival/Departure Schedule Generator :clock5:')
        col1, col2, col3 = st.columns(3)
    
        with col1:
            mu = st.slider('Remaining fuel in arriving tenders, Mean (0.8 = 80%)',0.0,0.8,0.2)
            cv = st.slider('Remaining fuel in arriving tenders, Coefficient of Variation',0.0,0.5,0.15)
    
        np.random.seed(gen_np_seed(mu,cv)) # Thanks Derek
    
        with col2:
            st.header('Generated Arrival Schedule')
            arrschdl = []
    
            for hr in range(len(arrivals)):
                for oct in range(0,8):
                    prob = arrivals[hr]/8
                    if np.random.rand() <= prob:
                        arrtime = hr + 0.125*np.random.rand() + 0.125*oct
                        arrschdl.append(arrtime)
    
            dfarr = pd.DataFrame({'arrival time':arrschdl,'tenders':arrtndrs,
                'fuel remaining':[min(max(x,0),1) for x in np.random.normal(mu,mu*cv,len(arrschdl))]})
            dfarr = dfarr.round(2)
            st.dataframe(dfarr)
            st.metric('Total Train Arrivals',len(dfarr))
    
            csvarr = convert_df(dfarr)
            st.download_button(
                'Download arrival schedule as CSV',
                csvarr,
                'arrival_schedule.csv',
                'text/csv'
            )
    
        with col1:
            dfhist  = dfarr.loc[:,'fuel remaining']
            fig = px.histogram(dfhist,x='fuel remaining')
            fig.update_layout(xaxis_range=[0,1])
            st.header('Fuel Remaining in Arriving Tenders')
            st.plotly_chart(fig,use_container_width=True)
    
        with col3:
            st.header('Generated Departure Schedule')
            depschdl = []
    
            for hr in range(len(departures)):
                for oct in range(0,8):
                    prob = departures[hr]/8
                    if np.random.rand() <= prob:
                        deptime = hr + 0.125*np.random.rand() + 0.125*oct
                        depschdl.append(deptime)
            
            dfdep = pd.DataFrame({'departure time':depschdl,'tenders':deptndrs})
            dfdep = dfdep.round(2)
            st.dataframe(dfdep)
            st.metric('Total Train Departures',len(dfdep))
            
            csvdep = convert_df(dfdep)
            st.session_state.dl = st.download_button(
                'Download departure schedule as CSV',
                csvdep,
                'departure_schedule.csv',
                'text/csv'
        )
# %% Demand profile page  

# *****************************************************************************************************************
with tab3:
    st.title(':bar_chart: Charging/Refueling Demand and Tender Inventory Generator :clipboard:')
    st.markdown("---")

    st.markdown(
        """
        # Data Input and Parameters """)
    if design == 'Electric':
        tndrpwr = st.number_input('Tender charging power, MW', min_value = 0.25,max_value = 4.0,
                                  value = 2.5,step=0.1, key='j')
        tndrprcs = st.number_input('Tender processing time, minutes',0,20,10, key='k')
    elif design == 'Hydrogen':
        tndrflwrt = st.number_input('Tender refueling rate, kgH2/min',8.7,17.3,10.0,0.1, key='l')
        # kgH2/min -> MW (33.33 kWh/min -> 2000 kWh/hr -> 2 MW)
        tndrpwr = tndrflwrt*2
        tndrprcs = st.number_input('Tender processing time, minutes',0,20,key='m')
    # calculate energy required to charge each arriving tender
    arrdmnd = (1-dfarr.loc[:,'fuel remaining'])*dfarr['tenders']*tndrnrg
    # calculate total energy dispensed by station to arriivng tenders
    ttlnrg = sum(arrdmnd)
    # calculate the average station demand
    ttlavgpwr = ttlnrg/8760
    # display metrics
    # st.metric('Total Energy Dispensed, GWh',round(ttlnrg/1e3,1))
    # st.metric('Average Station Demand, MW',round(ttlavgpwr,1))
    # st.metric('Average MWh Dispensed Daily',round(ttlavgpwr*24,1))
    # *****************************************************************************************************************
    stepsize = 1 # minutes
    chgrs = []
    rdytndrs = []
    for i in range(len(dfarr)): # iterate through arrivals
        for j in range(dfarr.iloc[i,1]): # iterate through each train's tenders
            k = 0
            match = False
            while k < len(chgrs) and match == False: # iterate through chargers/dispensers
                end0 = chgrs[k][-1][1]
                if dfarr.iloc[i,0] > (end0+(tndrprcs/60)): # if charger is available
                    start = dfarr.iloc[i,0]+(tndrprcs/60) # begin charge time after processing time
                    end = start+((1-dfarr.iloc[i,2])*tndrnrg/tndrpwr) # end charge time
                    rdytndrs.append(end+(tndrprcs/60)) # add processing time
                    startend = (start,end) # combine start and end time into one element
                    chgrs[k].append(startend) # add charge event to charger
                    match = True
                k += 1
            if match == False: # if failed to match tender to available charger
                start = dfarr.iloc[i,0]+(tndrprcs/60)
                end = start+((1-dfarr.iloc[i,2])*tndrnrg/tndrpwr)
                startend = (start,end) # combine start and end time into one element
                chgrs.append([startend]) # add new charger and add charge event to it
    dmnd = []
    for i in range(len(chgrs)): # iterate through chargers/dispensers
        dmnd.append(generate_demand_profile(chgrs[i],stepsize))
    if design == 'Electric':
        # sum individual charger demand profiles and scale to charging power (MW)
        ttldmnd = [sum(x)*tndrpwr for x in zip(*dmnd)]
        # reduce temporal resolution for displaying in Streamlit (reduces loading time)
        ttldmndhr = average_demand_profile(ttldmnd,60,stepsize)
        # convert to 15-min interval for CSV export
        ttldmnd15 = average_demand_profile(ttldmnd,15,stepsize)
    elif design == 'Hydrogen':
        # sum individual charger demand profiles and scale to refueling rate (kgH2/hr)
        ttldmnd = [sum(x)*tndrflwrt*60 for x in zip(*dmnd)]
        # reduce temporal resolution for displaying in Streamlit (reduces loading time)
        ttldmndhr = average_demand_profile(ttldmnd,60,stepsize)
        # convert to 15-min interval for CSV export
        ttldmnd15 = average_demand_profile(ttldmnd,15,stepsize)
    # Tender inventory calculator
    rr = []
    for i in range(len(dfdep)): # iterate through departing trains
        for j in range(dfdep.iloc[i,1]): # iteratte through departing tenders
            if rdytndrs[0] < dfdep.iloc[i,0]: # available tenders
                rdytndrs.pop(0) # take a charged tender
            else: # no available tenders
                rr.append(dfdep.iloc[i,0]) # take a ready reserve tender
# *****************************************************************************************************************   
    st.markdown("---")

    st.markdown(
        """
        # Demand Profile""")
    col12, col22 = st.columns(2)
    if design == 'Electric':
        with col12:
            st.metric('Chargers',len(chgrs))
            st.metric('Average Station Demand, MW',round(ttlavgpwr,1))
            dfchgrschdl = pd.DataFrame(chgrs).T
            CSVchgrschdl = convert_df(dfchgrschdl)

            st.download_button(
                label='Download charger schedules as CSV',
                data = CSVchgrschdl,
                file_name='chargerschedules.csv',
                mime='text/csv')

            dfdmnd15 = pd.DataFrame({'time':np.arange(0,8760,0.25),'MW':ttldmnd15})
            dfdmnd15.loc[0,'chargers'] = len(chgrs)
            dfdmnd15.loc[0,'tender reserve'] = len(rr) #input for battery-electric
            CSVdmnd15 = convert_df(dfdmnd15)

            st.download_button(
            label='Download 15-minute demand profile as CSV',
            data=CSVdmnd15,
            file_name='electric_demand_profile.csv',
            mime='text/csv')

        with col22:
            fig1 = px.bar(y=ttldmndhr)
            fig1.update_layout(title='Charging Demand Profile, MW',xaxis_title='Hour',yaxis_title='MW')
            st.plotly_chart(fig1,use_container_width=True,height=800)
    elif design == 'Hydrogen':
        with col12:
            st.metric('Dispensers',len(chgrs))
            st.metric('Average Station Deamnd, kgH2/hr',round(ttlavgpwr/0.03333,1))
            dfchgrschdl = pd.DataFrame(chgrs).T
            CSVchgrschdl = convert_df(dfchgrschdl)

            st.download_button(
                label='Download refueling schedules as CSV',
                data = CSVchgrschdl,
                file_name='chargerschedules.csv',
                mime='text/csv')

            dfdmnd15 = pd.DataFrame({'time':np.arange(0,8760,0.25),'kgH2/hr':ttldmnd15})
            dfdmnd15.loc[0,'dispensers'] = len(chgrs)
            dfdmnd15.loc[0,'tender reserve'] = len(rr)
            CSVdmnd15 = convert_df(dfdmnd15)#input for battery-electric

            st.download_button(
            label='Download 15-minute demand profile as CSV',
            data=CSVdmnd15,
            file_name='hydrogen_demand_profile.csv',
            mime='text/csv')

        with col22:
            fig1 = px.bar(y=ttldmndhr)
            fig1.update_layout(title='Refueling Demand Profile, kgH2/hr',xaxis_title='Hour',yaxis_title='kgH2/hr')
            st.plotly_chart(fig1,use_container_width=True,height=800)
            
    st.markdown("---")

    st.markdown(
        """
        # Inventory""")
    col13, col23, col33 = st.columns(3)
    with col13:
        arrived = sum(dfarr.loc[:,'tenders']) 
        st.metric('Tenders Arrived At Station',arrived)
        departed = sum(dfdep.loc[:,'tenders'])
        st.metric('Tenders Departed From Station',departed)
        st.metric('Arrival/Departure Tender Balance',arrived-departed)
    with col23:
        st.metric('Ready Reserve Tenders Used',len(rr))
        st.metric('Average Ready Reserve Tenders Utilized Per Day',round(len(rr)/365,2))
        st.metric('Average Ready Reserve Tenders Utilized Per Week',round(len(rr)/52,2))
        st.metric('Average Ready Reserve Tenders Utilized Per Month',round(len(rr)/30.437,2))
    with col33:
        st.markdown('Ready Reserve Tenders, Time of Use (Hour of Year)')
        dfrr = pd.DataFrame({'Time of Use':rr})
        st.dataframe(dfrr)

# *****************************************************************************************************************
# %% Battery electric page  
with tab4:
    if design == "Electric":
        st.title(':battery: Battery-electric Charging Station Sizing :electric_plug:')
        dfdmnd = dfdmnd15
        st.markdown("---")
        st.markdown(
            """
            # Parameters """)
                   
        shavechoice = st.radio('Peak shaving',('No','Yes'),index=0)
        avgdmnd = dfdmnd.iloc[:,1].mean()
        pkdmnd = dfdmnd.iloc[:,1].max()
        if shavechoice == 'Yes':
            st.metric('Average Charging Demand, MW',round(avgdmnd,2))
            st.metric('Peak Charging Demand, MW',round(pkdmnd,2))
            with st.form('Peak Shaving'):
                runs = st.number_input('Sizing runs (1 to 5)',1,5,1)
                if runs == 1:
                    shavelevelinput = st.number_input('Peak shave level, % of average demand',100,round((pkdmnd/avgdmnd)*100),150)
                    shavelevel = shavelevelinput/100
                    st.metric('Peak Shave Level, MW',round(shavelevel*avgdmnd,2))
                elif runs > 1:
                    shavelevel = []
                    for i in range(runs):
                        shavelevel.append(st.number_input('Peak shave level, % of average demand, run '+str(i+1),100,round((pkdmnd/avgdmnd)*100),200+(i*100),key=i))
                        st.metric('Peak Shave Level, MW',round(shavelevel[i]/100*avgdmnd,2))
                    shavelevel = [x/100 for x in shavelevel]
                submitshave = st.form_submit_button('Refresh')
        else:
            runs = 0
        #ssnlprice = st.radio('Seasonal Electricity Pricing?',('No','Yes'))
        #if ssnlprice == 'No':
        nrgprice = st.number_input('Electricity Cost, $/kWh',0.05,0.50,0.15)
        #else:
        #    nrgprice1 = st.number_input('Electricity cost in the spring, $/kWh',0.05,0.50,0.13)
        #    nrgprice2 = st.number_input('Electricity cost in the summer, $/kWh',0.05,0.50,0.16)
        #    nrgprice3 = st.number_input('Electricity cost in the fall, $/kWh',0.05,0.50,0.13)
        #    nrgprice4 = st.number_input('Electricity cost in the winter, $/kWh',0.05,0.50,0.17)
        ssteff = st.number_input('Solid-state transformer efficiency, %',80,99,97)
        ssteff = ssteff/100
        chgeff = st.number_input('Tender charging efficiency, %',75,99,94)
        chgeff = chgeff/100
        if shavechoice == 'Yes':
            beseff = st.number_input('BES round-trip efficiency, %',60,99,85)
            beseff = beseff/100
            onebeseff = m.sqrt(beseff)
            
        st.markdown("---")
        st.markdown(
            """
            # Results """)
                       
        col14, col24, col34 = st.columns(3)
        if shavechoice == 'Yes':
            if runs > 1:
                with col34:
                    runsel = st.slider('View Run',1,runs,1)
                bespower = []
                powerseries = []
                besenergy = []
                energyseries = []
                for i in range(len(shavelevel)):
                    p, e = bes(shavelevel[i])
                    powerseries.append(p)
                    energyseries.append(e)
                    bespower.append(max(p)) # BES Power Rating
                    besenergy.append(max(e)-min(e)) # BES Capacity
                with col34:
                    fig2 = px.scatter(y=powerseries[runsel-1])
                    fig2.update_layout(title='BES Power Output',xaxis_title='Time Step',yaxis_title='MW')
                    fig2.update_traces(marker=dict(size=3))
                    st.plotly_chart(fig2,use_container_width=True)
                    fig3 = px.line(y=energyseries[runsel-1])
                    fig3.update_layout(title='BES Energy',xaxis_title='Time Step',yaxis_title='MWh')
                    fig3.update_traces(line=dict(width=1))
                    st.plotly_chart(fig3,use_container_width=True)
                with col24:
                    fig4 = px.scatter(x=[x*100 for x in shavelevel],y=bespower)
                    fig4.update_layout(title='BES Power Rating vs. Peak Shaving Amount',xaxis_title='Peak Shave Level, % of Average Demand',yaxis_title='MW')
                    fig4.update_traces(marker=dict(size=16))
                    st.plotly_chart(fig4,use_container_width=True)
                    fig5 = px.scatter(x=[x*100 for x in shavelevel],y=besenergy)
                    fig5.update_layout(title='BES Capacity vs. Peak Shaving Amount',xaxis_title='Peak Shave Level, % of Average Demand',yaxis_title='MW')
                    fig5.update_traces(marker=dict(size=16))
                    st.plotly_chart(fig5,use_container_width=True)
                with col14:
                    ttlnrg = [0]*runs
                    ttlnrgcost = [0]*runs
                    for i in range(runs):
                        temp1 = shavelevel[i]*avgdmnd*0.25/ssteff/chgeff
                        temp2 = 0.25/ssteff/chgeff
                        temp3 = 0.25/ssteff
                        for j in range(len(dfdmnd)):
                            if dfdmnd.iloc[j,1] > shavelevel[i]*avgdmnd:
                                ttlnrg[i] += temp1
                            else:
                                ttlnrg[i] += dfdmnd.iloc[j,1]*temp2
                            if powerseries[i][j] < 0:
                                ttlnrg[i] += -powerseries[i][j]*temp3
                        ttlnrgcost[i] = ttlnrg[i]*nrgprice*1000
                    fig0 = px.scatter(x=[x*100 for x in shavelevel],y=ttlnrg)
                    fig0.update_layout(title='Total energy consumption',xaxis_title='Peak Shave Level, % of Average Demand',yaxis_title='MWh')
                    fig0.update_traces(marker=dict(size=16))
                    st.plotly_chart(fig0,use_container_width=True)
                    fig1 = px.scatter(x=[x*100 for x in shavelevel],y=ttlnrgcost)
                    fig1.update_layout(title='Total energy cost',xaxis_title='Peak Shave Level, % of Average Demand',yaxis_title='$')
                    fig1.update_traces(marker=dict(size=16))
                    st.plotly_chart(fig1,use_container_width=True)
            else:
                powerseries, energyseries = bes(shavelevel)
                bespower = max(powerseries)
                besenergy = max(energyseries)-min(energyseries)
                with col24:
                    fig2 = px.scatter(y=powerseries)
                    fig2.update_layout(title='BES Power Output',xaxis_title='Time Step',yaxis_title='MW')
                    fig2.update_traces(marker=dict(size=3))
                    st.plotly_chart(fig2,use_container_width=True)
                    fig3 = px.line(y=energyseries)
                    fig3.update_layout(title='BES Energy',xaxis_title='Time Step',yaxis_title='MWh')
                    fig3.update_traces(line=dict(width=1))
                    st.plotly_chart(fig3,use_container_width=True)
                with col34:
                    st.metric('Battery Energy Storage Power Rating, MW',round(bespower,2))
                    st.metric('Battery Energy Storage Capacity, MWh',round(besenergy,2))
                with col14:
                    ttlnrg = 0
                    ttlnrgcost = 0
                    temp1 = shavelevel*avgdmnd*0.25/ssteff/chgeff
                    temp2 = 0.25/ssteff/chgeff
                    temp3 = 0.25/ssteff
                    for j in range(len(dfdmnd)):
                        if dfdmnd.iloc[j,1] > shavelevel*avgdmnd:
                            ttlnrg += temp1
                        else:
                            ttlnrg += dfdmnd.iloc[j,1]*temp2
                        if powerseries[j] < 0:
                            ttlnrg += -powerseries[j]*temp3
                    ttlnrgcost = ttlnrg*nrgprice*1000
                    st.metric('Total energy consumed by station, MWh',round(ttlnrg))
                    st.metric('Total energy dispensed to tenders, MWh',round(avgdmnd*8760))
                    st.metric('Total electricity cost, $',round(ttlnrgcost))
    
        else: # no peak shaving
            with col14:
                ttlnrg = 0
                ttlnrgcost = 0
                temp1 = 0.25/ssteff/chgeff
                for i in range(len(dfdmnd)):
                    ttlnrg += dfdmnd.iloc[i,1]*temp1
                ttlnrgcost += ttlnrg*1000*nrgprice
                st.metric('Total energy consumed, MWh',round(ttlnrg))
                st.metric('Total energy dispensed to tenders, MWh',round(avgdmnd*8760))
                st.metric('Total electricity cost, $',round(ttlnrgcost))
                
        dfres = pd.DataFrame(columns=
            ['system pressure','compressor capacity','compressor quantity','tube trailer capacity',
             'tube trailer quantity','tanker capacity','tanker quantity',
             'cascade tank capacity','cascade tank quantity','pipeline capacity',
             'cgh2 storage','cryopump capacity','cryopump quantity',
             'hp evaporator capacity','hp evaporator quantity','lp evaporator capacity',
             'lp evaporator quantity','lh2 storage','service capacity',
             'sst power rating','bes power rating','bes capacity','chargers',
             'dispensers','tender reserve','energy consumed','energy dispensed','energy cost'])
        if shavechoice == 'Yes':
            if runs > 1:
                for i in range(runs):
                    temp = round(shavelevel[i]*avgdmnd/ssteff,2)
                    dfres.loc[i,'service capacity'] = temp
                    dfres.loc[i,'sst power rating'] = temp
                    dfres.loc[i,'bes power rating'] = round(bespower[i],2)
                    dfres.loc[i,'bes storage capacity'] = round(besenergy[i],2)
                    dfres.loc[i,'energy consumed'] = round(ttlnrg[i],2)
                    dfres.loc[i,'energy cost'] = round(ttlnrgcost[i],2)
                    dfres.loc[i,'energy dispensed'] = round(avgdmnd*8760,2)
                    dfres.loc[i,'chargers'] = dfdmnd.loc[0,'chargers']
                    dfres.loc[i,'tender reserve'] = dfdmnd.loc[0,'tender reserve']
            else:
                dfres.loc[0,'service capacity'] = round(shavelevel*avgdmnd/ssteff,2)
                dfres.loc[0,'sst power rating'] = round(shavelevel*avgdmnd/ssteff,2)
                dfres.loc[0,'bes power rating'] = round(bespower,2)
                dfres.loc[0,'bes storage capacity'] = round(besenergy,2)
                dfres.loc[0,'energy consumed'] = round(ttlnrg,2)
                dfres.loc[0,'energy cost'] = round(ttlnrgcost,2)
                dfres.loc[0,'energy dispensed'] = round(avgdmnd*8760,2)
                dfres.loc[0,'chargers'] = dfdmnd.loc[0,'chargers']
                dfres.loc[0,'tender reserve'] = dfdmnd.loc[0,'tender reserve']
        else:
            dfres.loc[0,'service capacity'] = round(pkdmnd/ssteff,2)
            dfres.loc[0,'sst power rating'] = round(pkdmnd/ssteff,2)
            dfres.loc[0,'chargers'] = dfdmnd.loc[0,'chargers']
            dfres.loc[0,'tender reserve'] = dfdmnd.loc[0,'tender reserve']
            dfres.loc[0,'energy consumed'] = round(ttlnrg,2)
            dfres.loc[0,'energy dispensed'] = round(avgdmnd*8760,2)
            dfres.loc[0,'energy cost'] = round(ttlnrgcost,2)
    else:
        st.markdown(
            """
            # This tab is only for Electric technology. Go to the train schedule page to choose technology """)
# %% Hydrogen page  
with tab5:
    st.title(':droplet: Hydrogen Refueling Station Sizing :station:')
    if design == "Hydrogen":
        st.markdown("---")
        
        st.markdown(
            """
            # Station Design""")
        col15, col25, = st.columns((1,4))
        with col15:      
            supplydesign = st.radio('Hydrogen supply',('Gaseous','Liquid'))
            if supplydesign == 'Gaseous':
                transportdesign = st.radio('Transportation',('Tube trailer','Pipeline'))
                processdesign = st.radio('Process',('Compressor',))
            elif supplydesign == 'Liquid':
                transportdesign = st.radio('Transportation',('Liquid tanker',))
                processdesign = st.radio('Process',
                ('Low-pressure evaporator → Compressor','Cryopump → High-pressure evaporator'))
            design_dispense = st.radio('Dispensing',('Direct-fill',))
        with col2:
            st.header('Station Design')
            design_overview = supplydesign + '  →  ' \
            + transportdesign + '  →  ' \
            + processdesign + '  →  ' \
            + 'Dispensers'
            st.subheader(design_overview)
        st.markdown("---")
        
        st.markdown(
            """
            # Parameters""")
        col16, col26 = st.columns((3,2))
        
        with col16:
            H2price = st.number_input('Hydrogen Cost, $/kg',0.20,20.00,2.00)
            gridprice = st.number_input('Electricity Cost, $/kWh',0.05,0.50,0.15, key = 'z1')
            tenderpres = st.radio('Tender nominal pressure, bar',(350,700))
            
            if supplydesign == 'Gaseous':
                if transportdesign == 'Tube trailer':
                    trailercap = st.slider('Tube trailer capacity, kgH2',200,800,400)
                elif transportdesign == 'Pipeline':
                    avgkgH2hr = round(dfdmnd15['kgH2/hr'].mean(),1)
                    pipecap = st.number_input('Pipeline flowrate, kgH2/hr',
                                              m.ceil(avgkgH2hr)*1.0,m.ceil(avgkgH2hr)*10.0,m.ceil(avgkgH2hr)*2.0,1.0)
                compcap = st.slider('Compressor unit capacity, kgH2/hr',200,1000,550)
                nrgreq = st.slider('Compressor energy requirement, kWh/kgH2',0.5,2.0,1.4)
            
            elif supplydesign == 'Liquid':
                if processdesign == 'Low-pressure evaporator → Compressor':
                    tankercap = st.slider('Liquid tanker capacity, kgH2',1000,8000,3000)
                    lpevapcap = st.slider('Low-pressure evaporator unit capacity, kgH2/hr',200,600,352)
                    compcap = st.slider('Compressor unit capacity, kgH2/hr',200,1000,550)
                    nrgreq = st.slider('Compressor energy requirement, kWh/kgH2',0.5,2.0,1.4)
                elif processdesign == 'Cryopump → High-pressure evaporator':
                    tankercap = st.slider('Liquid tanker capacity, kgH2',1000,8000,3000)
                    cryocap = st.slider('Cryopump unit capacity, kgH2/hr',100,250,174)
                    hpevapcap = st.slider('High-pressure evaporator unit capacity, kgH2/hr',500,1000,744)
                    nrgreq = st.slider('Cryopump energy requirement, kWh/kgH2',0.25,2.0,0.7)
                    
        ttlH2 = dfdmnd15.loc[:,'kgH2/hr'].sum()*0.25
        ttlH2cost = ttlH2*H2price
        ttlH2nrg = ttlH2*0.03333 # 1 kgH2 = 0.03333 MWh
        gridpower = [x*nrgreq/1e3 for x in dfdmnd15.loc[:,'kgH2/hr']] # kW
        gridcap = max(gridpower)
        ttlgridnrg = sum(gridpower)*0.00025 # kW -> MWh
        ttlgridcost = ttlgridnrg*1e3*gridprice
        ttlnrg = ttlH2nrg + ttlgridnrg
        ttlnrgcost = ttlH2cost + ttlgridcost
        # Process calculations
        if supplydesign == 'Gaseous':
    
            if transportdesign == 'Tube trailer':
                trailerqty = m.ceil(ttlH2/trailercap)
                strg = [0] # remove this element after looping, only needed for initial iteration
                for dmnd in dfdmnd15.loc[:,'kgH2/hr']:
                    if strg[-1] <= 0:
                        strg.append(strg[-1]+trailercap)
                    elif dmnd > 0:
                        strg.append(strg[-1]-dmnd*0.25)
                    else:
                        strg.append(strg[-1])
                strg.pop(0) # remove first element
                offset = abs(min(strg))
                strg = [x + offset for x in strg]
                CGH2strg = 0 # tube trailer = onsite storage
    
                pkdmnd = max(dfdmnd15.loc[:,'kgH2/hr'])
                compqty = m.ceil(pkdmnd/compcap)
    
            elif transportdesign == 'Pipeline':
                strg = [0] # remove this element after looping, only needed for initial iteration
    
                for dmnd in dfdmnd15.loc[:,'kgH2/hr']:
    
                    if dmnd == 0:
                        if strg[-1] < 0:
                            strg.append(strg[-1]+min(pipecap,abs(strg[-1]*4))*0.25)
                        else:
                            strg.append(strg[-1])
                    elif dmnd < pipecap:
                        if strg[-1] < 0:
                            strg.append(strg[-1]+min(pipecap-dmnd,abs(strg[-1]*4))*0.25)
                        else:
                            strg.append(strg[-1])
                    elif dmnd > pipecap:
                        strg.append(strg[-1]-(dmnd-pipecap)*0.25)
                    else:
                        strg.append(strg[-1])
                strg.pop(0) # remove first element
                offset = abs(min(strg))
                strg = [x + offset for x in strg]
                CGH2strg = max(strg)
    
                pkdmnd = max(dfdmnd15.loc[:,'kgH2/hr'])
                compqty = m.ceil(pkdmnd/compcap)
    
        else: # Liquid
            # Liquid Tanker
            tankerqty = m.ceil(ttlH2/tankercap)
            strg = [0] # remove this element after looping, only needed for initial iteration
    
            for dmnd in dfdmnd15.loc[:,'kgH2/hr']:
                if strg[-1] <= 0:
                    strg.append(strg[-1]+tankercap)
                elif dmnd > 0:
                    strg.append(strg[-1]-dmnd*0.25)
                else:
                    strg.append(strg[-1])
            strg.pop(0) # remove first element
            offset = abs(min(strg))
            strg = [x + offset for x in strg]
            LH2strg = max(strg)
    
            if processdesign == 'Low-pressure evaporator → Compressor':
                pkdmnd = max(dfdmnd15.loc[:,'kgH2/hr'])
                compqty = m.ceil(pkdmnd/compcap)
                lpevapqty = m.ceil(pkdmnd/lpevapcap)
    
            elif processdesign == 'Cryopump → High-pressure evaporator':
                pkdmnd = max(dfdmnd15.loc[:,'kgH2/hr'])
                cryoqty = m.ceil(pkdmnd/cryocap)
                hpevapqty = m.ceil(pkdmnd/hpevapcap)
                
        st.markdown("---")
        
        st.markdown(
            """
            # Results""")
        col17, col27 = st.columns(2)
        with col17:
            st.metric('Total Hydrogen Dispensed, kg',round(ttlH2))
            st.metric('Total Hydrogen Cost, $',round(ttlH2cost))
            st.metric('Total Electricity Consumption, MWh',round(ttlgridnrg,2))
            st.metric('Total Electricity Cost, $',round(ttlgridcost))
        with col27:
            fig0 = px.scatter(y=gridpower)
            fig0.update_layout(title='Grid Power vs. Time',xaxis_title='Hour',yaxis_title='MW')
            fig0.update_traces(marker=dict(size=3))
            st.plotly_chart(fig0,use_container_width=True,height=800)
        if transportdesign == 'Tube trailer':
            st.metric('Average tube trailer deliveries per day',m.ceil(trailerqty/365))
            st.metric('Compressors',compqty)
            with col2:
                fig1 = px.scatter(y=strg)
                fig1.update_layout(title='CGH2 Storage Level vs. Time',xaxis_title='Hour',yaxis_title='kgH2')
                fig1.update_traces(marker=dict(size=3))
                st.plotly_chart(fig1,use_container_width=True,height=800)
        elif transportdesign == 'Pipeline':
            st.metric('Compressors',compqty)
            with col2:
                fig2 = px.scatter(y=strg)
                fig2.update_layout(title='CGH2 Storage Level vs. Time',xaxis_title='Hour',yaxis_title='kgH2')
                fig2.update_traces(marker=dict(size=3))
                st.plotly_chart(fig2,use_container_width=True,height=800)
        elif transportdesign == 'Liquid tanker':
            if processdesign == 'Low-pressure evaporator → Compressor':
                st.metric('Low-pressure Evaporators',lpevapqty)
                st.metric('Compressors',compqty)
            elif processdesign == 'Cryopump → High-pressure evaporator':
                st.metric('Cryopumps',cryoqty)
                st.metric('High-pressure Evaporators',hpevapqty)
            st.metric('Average liquid tanker deliveries per day',m.ceil(tankerqty/365))
            with col2:
                fig3 = px.scatter(y=strg)
                fig3.update_layout(title='LH2 Storage Level vs. Time',xaxis_title='Hour',yaxis_title='kgH2')
                fig3.update_traces(marker=dict(size=3))
                st.plotly_chart(fig3,use_container_width=True,height=800)
        st.markdown("---")
        
        st.markdown(
            """
            # Export""")
        dfres = pd.DataFrame(columns=
            ['system pressure','compressor capacity','compressor quantity','tube trailer capacity',
              'tube trailer quantity','tanker capacity','tanker quantity',
              'cascade tank capacity','cascade tank quantity','pipeline capacity',
              'cgh2 storage','cryopump capacity','cryopump quantity',
              'hp evaporator capacity','hp evaporator quantity','lp evaporator capacity',
              'lp evaporator quantity','lh2 storage','service capacity',
              'sst power rating','bes power rating','bes capacity','chargers',
              'dispensers','tender reserve','energy consumed','energy dispensed','energy cost'])
        dfres.loc[0,'system pressure'] = tenderpres
        if 'Compressor' in design_overview:
            dfres.loc[0,'compressor capacity'] = compcap
            dfres.loc[0,'compressor quantity'] = compqty
            if 'Low-pressure evaporator' in design_overview:
                dfres.loc[0,'lp evaporator capacity'] = lpevapcap
                dfres.loc[0,'lp evaporator quantity'] = lpevapqty
        if 'Tube trailer' in design_overview:
            dfres.loc[0,'tube trailer capacity'] = trailercap
            dfres.loc[0,'tube trailer quantity'] = trailerqty
        elif 'Liquid tanker' in design_overview:
            dfres.loc[0,'tanker capacity'] = tankercap
            dfres.loc[0,'tanker quantity'] = tankerqty
            dfres.loc[0,'lh2 storage'] = LH2strg
        #if 'Cascade' in design_overview:
        #    dfres.loc[0,'cascade tank capacity'] = cascL
        #    dfres.loc[0,'cascade tank quantity'] = 0 # cascqty
        if 'Pipeline' in design_overview:
            dfres.loc[0,'pipeline capacity'] = pipecap
            dfres.loc[0,'cgh2 storage'] = CGH2strg
        if 'Cryopump' in design_overview:
            dfres.loc[0,'cryopump capacity'] = cryocap
            dfres.loc[0,'cryopump quantity'] = cryoqty
            dfres.loc[0,'hp evaporator capacity'] = hpevapcap
            dfres.loc[0,'hp evaporator quantity'] = hpevapqty
        dfres.loc[0,'energy consumed'] = ttlnrg
        dfres.loc[0,'energy dispensed'] = ttlH2nrg
        dfres.loc[0,'energy cost'] = ttlnrgcost
        dfres.loc[0,'service capacity'] = gridcap
        dfres.loc[0,'dispensers'] = dfdmnd15.loc[0,'dispensers']
        dfres.loc[0,'tender reserve'] = dfdmnd15.loc[0,'tender reserve']
        CSVdfres = convert_df(dfres)
        st.download_button(
            label='Download Results',
            data=CSVdfres,
            file_name = 'Task3_output.csv',
            mime='text/csv'
        )
    else:
        st.markdown(
            """
            # This tab is only for Hydrogen technology. Go to the train schedule page to choose technology """)

