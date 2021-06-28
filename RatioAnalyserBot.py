import numpy as np
from matplotlib import pyplot as plt
from numpy.testing._private.utils import tempdir
import pandas as pd

#csv file --> array. *Indexing: [columns][row]
def create_data(filename):
    df = pd.read_csv(filename, header = 1).values
    df = pd.DataFrame(df)
    df.columns = df.iloc[0] #set header
    df = df.drop(df.index[0])
    return df

#Check if a value in a cell is a float - returns False if cell is empty or NM
def isnumber(string):
    try:
        float(string)
        return True
    except:
        return False

#Converts all the values of a DataFrame column into a float
def to_float(column):
    return list(filter(lambda x: isnumber(x), column))

#Functions to return various metrics of a particular column index 
def total(dataset, columnindex):
    return np.sum(list(map(lambda x: float(x), filter(lambda x: isnumber(x), dataset[columnindex][1:]))))

def average(dataset, columnindex):
    return np.mean(list(map(lambda x: float(x), filter(lambda x: isnumber(x), dataset[columnindex][1:]))))

#Calculate Price to Earnings Ratio (Day close / EPS) - inputs 2 columns and creates a new column with PE ratios
def PE_ratio(dataset, EPS_col, day_close_col):
    PE_ratios = [] 
    for i in range(1, len(dataset[EPS_col])+1):
        if not isnumber(dataset[EPS_col][i]): #invalid value
            PE_ratios.append('-')
        elif not isnumber(dataset[day_close_col][i]): #invalid value in corresponding metric
            PE_ratios.append(None)
        else: #Valid values in both share close column and PBV column
            PE_ratios.append((float(dataset[day_close_col][i])/float(dataset[EPS_col][i])))  
    dataset.insert(len(dataset.columns), 'PE_ratio', PE_ratios)

#Convert all the values in the column from string to float - does not update original dataframe
def col_str_to_int(dataset, col):
    temp = dataset[col]
    for i in range(1, len(temp)+1 ):
        if isnumber(temp[i]):
            temp[i] = float(temp[i])
    return temp
    
#Takes in 2 column headers, and then determining the correl coeff (r value) for the two sets of data
def correl(dataset, dependent, independent):
    x2, y2 = [], []
    y = col_str_to_int(dataset, dependent)
    x = col_str_to_int(dataset, independent)
    for i in range(1, len(y)+1 ): #remove blanks
        if isnumber(y[i]) and isnumber(x[i]):
            y2.append(y[i])
            x2.append(x[i])
    x_array = pd.Series(x2)
    y_array = pd.Series(y2)
    x_array_no_outliers = x_array[x_array.between(x_array.quantile(0.15), x_array.quantile(0.85))]
    y_corresponding_list = []
    for i in x_array_no_outliers.index:
        y_corresponding_list.append(y_array[i])
    y_corresponding_array = pd.Series(y_corresponding_list)
    r = np.corrcoef(x_array_no_outliers, y_corresponding_array)
    if round(r[0,1], 5) == round(r[1,0], 5):
        return round(r[0,1], 5)
    else:
        return r

#Determine all independent variables (secondary metrics), outputs as list. *OUTDATED
def create_comparison(dataset, dependent): #dependent --> core ratios to be compared to (e.g. PE, PB ratio), input as a sequence
    comparison_bases = list(dataset.columns)
    if not dependent:
        print('No comparison bases')
    for base in dependent:
        comparison_bases.remove(base)
    if 'Company Name' in comparison_bases:
        comparison_bases.remove('Company Name')
    if 'Exchange:Ticker' in comparison_bases:
        comparison_bases.remove('Exchange:Ticker')
    if 'Industry Classifications' in comparison_bases:
        comparison_bases.remove('Industry Classifications')
    return comparison_bases

#find correlation between all independent and dependent variables
def find_all_r(dataset, independent, dependent): 
    all_r = {}
    for base in dependent:
        if base not in all_r:
            all_r[base] = []
        for metric in independent:
            r = correl(dataset, base, metric)
            all_r[base].append([metric, r])
    return all_r

#from a dct of all correlations, return the highest correlation for each dependent variable in a new dct
def highest_correl(all_r): 
    output = {}
    for base, values in all_r.items():
        highest_metric = None
        highest_r = 0
        for metric, r in values:
            if abs(r) > abs(highest_r):
                highest_metric = metric
                highest_r = r
        output[base] = (highest_metric, highest_r)
    return output

#sorts all correlation values by largest (best) to smallest (worst)
def sort_all_r(all_r):
    for base, values in all_r.items():
        values.sort(key = lambda x: abs(x[1]), reverse = True)
    return all_r

#Takes in 2 columns (note the order), returns the equation of best fit line y = mx + c
def graph_function(dataset, dependent, independent): 
    x2, y2 = [], []
    y = col_str_to_int(dataset, dependent)
    x = col_str_to_int(dataset, independent)
    for i in range(1, len(y)+1 ): #remove blanks
        if isnumber(y[i]) and isnumber(x[i]):
            y2.append(y[i])
            x2.append(x[i])
    x_array = pd.Series(x2)
    y_array = pd.Series(y2)
    x_array_no_outliers = x_array[x_array.between(x_array.quantile(0.15), x_array.quantile(0.85))]
    y_corresponding_list = []
    for i in x_array_no_outliers.index:
        y_corresponding_list.append(y_array[i])
    y_corresponding_array = pd.Series(y_corresponding_list)
    eqn = np.polyfit(y_corresponding_array, x_array_no_outliers, 1)
    #print(f'{round(eqn[0], 3)}x + {round(eqn[1], 3)}')
    return eqn

#Takes in a regression line and an independent variable (x), then returns the dependent variable (y)
def predict(eqn, independent): 
    model = np.poly1d(eqn)
    output = model(independent)
    #print(round(output, 3))
    return output

#Find dependent and independent variables *OUTDATED - REFER TO FIND_DEPENDENTS AND FIND_INDEPENDENTS
def user_input(dataset, all_r_sorted):
    dependent = input('Please enter the dependent variable (e.g. PE Ratio, PB ratio). Enter "list" for a list of possible variables. \
        Enter "exit" to stop the program \nDependent variable: ')
    if dependent in all_r_sorted.keys():
        for r in all_r_sorted[dependent]:
            print(f'{r[0]}: {r[1]} correlation')
            independent_value = input("Enter variable value, or 'NIL' to try the next best variable \n Value: ")
            independent_value = float(independent_value)
            if independent_value == 'NIL':
                continue
            else:
                try:
                    eqn = graph_function(dataset, dependent, r[0])
                    prediction = predict(eqn, independent_value)
                    print(f'With a {r[0]} value of {independent_value}, {dependent} is likely to be {round(prediction, 3)}')
                    return prediction
                except:
                    print('Variable value entered incorrectly. Please restart the program')
                    user_input(dataset, all_r_sorted)
    elif dependent == 'list':
        print(all_r_sorted.keys())
        user_input(dataset, all_r_sorted)
    elif dependent == 'exit':
        print('Program stopped!')
        return None
    else:
        print('Invalid dependent variable. Please check the exact name of dependent variable')
        user_input(dataset, all_r_sorted)

#Find the dependent variables, based on user inputs. Can optionally take in list of independent variables to reduce number of selections
def find_dependents(dataset, *independents):
    valid_nums = []
    message = 'POSSIBLE DEPENDENT VARIABLES: \n' 
    for i in range(len(dataset.columns)):
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[i] == 'Industry Classifications'\
            or dataset.columns[i] == 'Company Type':
            continue
        elif independents: #if there are predetermined independent variables
            if dataset.columns[i] in independents[0]:
                continue
        valid_nums.append(i)
        message += str(i) + ' '*(5-len(str(i))) + f'{dataset.columns[i]} \n'
    print(message) #asks for input of dependent variables
    selection = input('Please enter the number of the selected dependent variables, seperated by a comma (no spaces):  ') 
    selection = selection.split(',')
    message2 = '\nSELECTED DEPENDENT VARIABLES: \n'
    output = []
    for num in selection:
        try:
            num = int(num)
            message2 += f'{dataset.columns[num]} \n'
            if int(num) not in valid_nums:
                print('\n***Please enter a valid selection***\n')
                temp = find_dependents(dataset, *independents)
                return temp
        except:
            print('\n***Please enter a valid selection***\n')
            temp = find_dependents(dataset, *independents)
            return temp
        output.append(dataset.columns[num])
    print(message2) #displays confirmation
    confirmation = input('Confirm? y/n:  ')
    if confirmation == 'y':
        print('\nDependent variables confirmed!\n')
        return output
    else:
        temp = find_dependents(dataset, *independents)
        return temp

#Find the independent variables, based on user inputs. Can optionally take in list of dependent variables to reduce number of selections
def find_independents(dataset, *dependents):
    valid_nums = []
    message = 'POSSIBLE INDEPENDENT VARIABLES: \n' 
    for i in range(len(dataset.columns)):
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[i] == 'Industry Classifications'\
            or dataset.columns[i] == 'Company Type':
            continue
        elif dependents: #if there are predetermined dependent variables
            if dataset.columns[i] in dependents[0]:
                continue
        valid_nums.append(i)
        message += str(i) + ' '*(5-len(str(i))) + f'{dataset.columns[i]} \n'
    print(message) #asks for input of independent variables
    selection = input('Please enter the number of the selected independent variables, seperated by a comma (no spaces). Enter "all" to select all:  ')
    output = []
    message2 = '\nSELECTED INDEPENDENT VARIABLES: \n'
    if selection == 'all':
        for i in valid_nums:
            output.append(dataset.columns[i])
            message2 += f'{dataset.columns[i]}\n'
        print(message2) #displays confirmation
        confirmation = input('Confirm? y/n:  ')
        if confirmation == 'y':
            print('\nIndependent variables confirmed!\n')
            return output
        else:
            temp = find_independents(dataset, *dependents)
            return temp
    selection = selection.split(',')
    
    for num in selection:
        try:
            num = int(num)
            message2 += f'{dataset.columns[num]} \n'
            if int(num) not in valid_nums:
                print('\n***Please enter a valid selection***\n')
                temp = find_independents(dataset, *dependents)
                return temp
        except:
            print('\n***Please enter a valid selection***\n')
            temp = find_independents(dataset, *dependents)
            return temp
        output.append(dataset.columns[num])
    print(message2) #displays confirmation
    confirmation = input('Confirm? y/n:  ')
    if confirmation == 'y':
        print('\nIndependent variables confirmed!\n')
        return output
    else:
        temp = find_independents(dataset, *dependents)
        return temp

#Combines finding dependents and independents into one function, then defines them globally. Also returns both in a list.
def find_dependents_and_independents(dataset):
    global dependents
    global independents
    dependents = find_dependents(dataset)
    independents = find_independents(dataset, dependents)
    return [dependents, independents]

#takes in a dct of sorted r values, and asks the user to choose which 2 to do analysis on
def eqn_constructor(dataset, all_r_sorted):
    keys = list(all_r_sorted.keys())
    print('CHOOSE YOUR DEPENDENT VARIABLE: \n')
    for i in range(len(keys)):
        print(f'{i}:    {list(all_r_sorted.keys())[i]}')
    dependent_selection = input('\nAll possible selections have been displayed. \nPlease enter your selection, or enter "exit" to stop the program:   ')
    if dependent_selection == 'exit':
        print('Program stopped!')
        return
    try:
        dependent_variable = keys[int(dependent_selection)] 
    except ValueError:
        print('ERROR: Please enter a valid selection. The selection should be a number.')
        return
    except IndexError:
        print('ERROR: Please choose within the numbers provided in the list above.')
        return
    if int(dependent_selection) < 0:
        print('ERROR: Please choose within the numbers provided in the list above.')
        return
    print(f'\nDependent variable has been selected as {dependent_variable}. \n')
    print('CHOOSE YOUR INDEPENDENT VARIABLE: \n')
    selected_dependent_avail_choices = list(all_r_sorted[keys[int(dependent_selection)]])
    for i in range(min(len(selected_dependent_avail_choices), 5)):
        print(f'{i}:    {selected_dependent_avail_choices[i][0]}: corr = {selected_dependent_avail_choices[i][1]}')
    independent_selection = input('\nThe top 5 independent variables with the highest correlation have been displayed.\
         \nPlease enter your selection, or enter "exit" to stop the program:    ')
    if independent_selection == 'exit':
        print('Program stopped!')
        return
    try:
        independent_variable = all_r_sorted[dependent_variable][int(independent_selection)][0]     
    except ValueError:
        print('ERROR: Please enter a valid selection. The selection should be a number between 0 to 4 inclusive.')
        return
    if int(independent_selection) > 4 or int(independent_selection) < 0:
        print('ERROR: Please choose within the numbers provided in the list above.')
        return
    print(f'\nIndependent variable has been selected as {independent_variable}. \n')
    eqn = graph_function(dataset, dependent_variable, independent_variable)
    return eqn

def user_analysis(filename):
    data = create_data(filename)
    dependents_and_independents = find_dependents_and_independents(data)
    all_r = find_all_r(data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    eqn = eqn_constructor(data, all_r_sorted)
    if eqn is not None:
        independent_value = input('Please provide a value for the independent variable selected: ')
        prediction = predict(eqn, float(independent_value))
        print(f'The predicted value of the dependent variable is {round(prediction, 3)}')
        return prediction

#Takes in a dct of sorted r values, then returns predictions for the greatest r value for each dependent variable.
#This function is split into 2 smaller parts - auto_eqn and auto_prediction
def auto_eqn_and_prediction(dataset, all_r_sorted):
    output = {} #storage for function return
    memory = {} #storage for user entered values, so that users would not need to enter the same value twice
    prints = '\nPrice Multiples Prediction: \n' #storage for printed text
    for dependent, independent in all_r_sorted.items():
        temp_target_indep_variable = independent[0][0]
        eqn = graph_function(dataset, dependent, temp_target_indep_variable)
        if temp_target_indep_variable in memory:
            independent_value = memory[temp_target_indep_variable]
        else:
            independent_value = input(f'\nPlease provide a value for the independent variable {temp_target_indep_variable}\
. Enter "exit" to stop the program: ')
            if independent_value == 'exit':
                print('\nProgram stopped!')
                return
            else:
                try:
                    independent_value_float = float(independent_value) 
                except ValueError:
                    print('Error: Please enter a valid value for the variable.')
                    return
                prediction = predict(eqn, independent_value_float)
                prints += f'{dependent}: {round(prediction, 3)}\n'
                memory[temp_target_indep_variable] = independent_value_float
        output[dependent] = [temp_target_indep_variable, prediction]
    print(prints)
    return output

#Takes in sorted correlation values and outputs equations for the best indep variable for each dependent variable in a dictionary
def auto_eqn(dataset, all_r_sorted):
    output = {}
    for dependent, independent in all_r_sorted.items():
        target_indep_variable = independent[0][0]
        correl = independent[0][1]
        equation = graph_function(dataset, dependent, target_indep_variable)
        output[dependent] = [target_indep_variable, equation, correl]
    return output

#Takes in equations for the best indep variable and asks for user input, to generate predictions
def auto_prediction(dataset, best_eqns, show_correl = 0):
    output = {} #storage for function return
    memory = {} #storage for user entered values, so that users would not need to enter the same value twice
    prints = '\nPrice Multiples Prediction: \n' #storage for printed text
    for dependent, best_independent_and_correl in best_eqns.items():
        target_indep_variable, equation, correl = best_independent_and_correl
        if target_indep_variable in memory:
            independent_value = memory[target_indep_variable]
        else:
            independent_value = input(f'\nPlease provide a value for the independent variable {target_indep_variable}\
. Enter "exit" to stop the program: ')
            if independent_value == 'exit':
                print('\nProgram stopped!')
                return
            else:
                try:
                    independent_value_float = float(independent_value) 
                except ValueError:
                    print('Error: Please enter a valid value for the variable.')
                    return
                prediction = predict(equation, independent_value_float)
                if show_correl:
                    prints += f'{dependent} (corr = {round(correl, 2)}):    {round(prediction, 3)}\n'
                else:
                    prints += f'{dependent}:    {round(prediction, 3)}\n'
                memory[target_indep_variable] = independent_value_float
        output[dependent] = [target_indep_variable, prediction]
    print(prints)
    return output

#Function to do full analysis based on the best indep values with highest correl
def auto_analysis(filename):
    data = create_data(filename)
    dependents_and_independents = find_dependents_and_independents(data)
    all_r = find_all_r(data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    best_eqns = auto_eqn(data, all_r_sorted)
    predictions = auto_prediction(data, best_eqns, 1)
    return predictions

def user_prediction(dataset, best_eqns, user_inputs):
    #user_inputs = [industry_type, revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital]
    dct = {}
    independents = ['Total Revenues, 3 Yr CAGR % [LTM] (%)', 'Return on Equity % [LTM]', 'Current Ratio [LTM]', 'EBITDA Margin % [LTM]', \
        'Total Asset Turnover [Latest Annual]', 'Total Debt/Capital % [Latest Annual]']
    for dependent, indep_eqn_correl in best_eqns.items():
        index = independents.index(indep_eqn_correl[0])
        value = user_inputs[index]
        prediction = predict(indep_eqn_correl[1], value)
        dct[dependent] = prediction
    return dct

#Takes in a set number of values for some fixed independent variables, and returns a dictionary with key: dependent variable and value: best prediction
#Solely for website
def output_website(filename, user_inputs):
    #user_inputs = [industry_type, revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital]
    if len(user_inputs) != 7:
        print('Please enter all the required values.')
        return None

    data = create_data(filename)
    dependents = ['P/LTM Diluted EPS Before Extra [Latest] (x)', 'P/BV [Latest] (x)']
    independents = ['Total Revenues, 3 Yr CAGR % [LTM] (%)', 'Return on Equity % [LTM]', 'Current Ratio [LTM]', 'EBITDA Margin % [LTM]', \
        'Total Asset Turnover [Latest Annual]', 'Total Debt/Capital % [Latest Annual]']
    all_r = find_all_r(data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    best_eqns = auto_eqn(data, all_r_sorted)
    predictions = user_prediction(data, best_eqns, user_inputs)
    return predictions
 
####TEMP TESTING STUFF####
#1. Testing standalone functions
#insurance_data = create_data('Insurance Report.csv')
chemicals_data = create_data('Chemicals Report.csv')
#correl(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
#highest_correl(all_r)
#eqn = graph_function(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
#predict(eqn, 10)
#dependents = find_dependents(data)
#independents = find_independents(data, dependents)
dependents_and_independents = find_dependents_and_independents(chemicals_data)
all_r = find_all_r(chemicals_data, independents, dependents)
all_r_sorted = sort_all_r(all_r)
highest_correl(all_r)
#equation = eqn_constructor(chemicals_data, all_r_sorted)
#insurance_prediction = user_analysis('Insurance Report.csv')
#chemicals_prediction = user_analysis('Chemicals Report.csv')
#auto_eqn_and_prediction(chemicals_data, all_r_sorted)
best_eqns = auto_eqn(chemicals_data, all_r_sorted)
#predicc = auto_prediction(chemicals_data, best_eqns, 1)
#temp_result = output_website('Chemicals Report.csv', ["Chemicals",1,1,1,1,1,1])

#2. Testing full functions
#full_analysis = auto_analysis('Chemicals Report.csv')
#full_analysis = auto_analysis('Insurance Report.csv')
