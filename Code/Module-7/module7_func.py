import pandas as pd
### Paths and Files
###################
### read the combined commodity and carbon-intensity price data sent by Adi    
static_input_path = "../Data/Static"    
module7_output_path = "../Data/Output/Module-7"

input_mod7 = pd.read_csv("%s/commodityPrice_and_carbonIntensity_module7.csv" %(module7_output_path)) 

def energy_prices(energy_system_scenario_options, 
                  renewable_prices, h2_sub, oil_prices 
                  ):
    """Subset commodity price and carbon intensity data based on user inputs on renewable trajectories,
    hydrogen subsidies, and energy system scenario.
    
    Keyword arguments:
    energy_system_scenario_options -- energy_system_scenario_options from Module 1
    renewable_prices --  options = ('Moderate', 'Conservative','Advanced')
    h2_sub -- hydrogen subsidies; Yes or No
    oil_prices -- Low, Mid, or High
    """
    output_mod7 = input_mod7.loc[
                            (input_mod7['renewables_prices'] == renewable_prices) &
                            (input_mod7['hydrogen_subsidies'] == h2_sub) &
                            (input_mod7['energy_system_scenario'] == energy_system_scenario_options) &
                            (input_mod7['oil_prices'] == oil_prices) 
                            ]

    
    output_mod7.drop(columns = ["oil_prices", "renewables_prices", 'hydrogen_subsidies'] , inplace=True)
    
    #output_mod7.to_csv("%s/module7_to_module9.csv" %(module7_output_path))
    output_mod7.to_csv("%s/output_mod7_to_mod9.txt" %(module7_output_path), sep="\t", header=None, index=False)
    
    
    
    
    
    
    
    
    
    
    
    