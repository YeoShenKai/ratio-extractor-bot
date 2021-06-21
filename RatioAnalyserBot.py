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
def correl(dataset, col1, col2):
    x2, y2 = [], []
    x = col_str_to_int(dataset, col1)
    y = col_str_to_int(dataset, col2)
    for i in range(1, len(x)+1 ):
        if isnumber(x[i]) and isnumber(y[i]):
            x2.append(x[i])
            y2.append(y[i])
    x_array = np.array(x2)
    y_array = np.array(y2)
    r = np.corrcoef(x_array, y_array)
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
    x = col_str_to_int(dataset, dependent)
    y = col_str_to_int(dataset, independent)
    for i in range(1, len(x)+1 ):
        if isnumber(x[i]) and isnumber(y[i]):
            x2.append(x[i])
            y2.append(y[i])
    x_array = np.array(x2)
    y_array = np.array(y2)
    eqn = np.polyfit(x_array, y_array, 1)
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
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[i] == 'Industry Classifications':
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
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[i] == 'Industry Classifications':
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
    for i in range(5):
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

def analysis(filename):
    data = create_data(filename)
    dependents_and_independents = find_dependents_and_independents(data)
    all_r = find_all_r(data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    eqn = eqn_constructor(data, all_r_sorted)
    independent_value = input('Please provide a value for the independent variable selected: ')
    prediction = predict(eqn, int(independent_value))
    print(f'The predicted value of the dependent variable is {round(prediction, 3)}')
    return prediction

####TEMP TESTING STUFF####
insurance_data = create_data('Insurance Report.csv')
chemicals_data = create_data('Chemicals Report.csv')
#correl(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
#highest_correl(all_r)
#eqn = graph_function(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
#predict(eqn, 10)
#dependents = find_dependents(data)
#independents = find_independents(data, dependents)
#dependents_and_independents = find_dependents_and_independents(data)
#all_r = find_all_r(data, independents, dependents)
#all_r_sorted = sort_all_r(all_r)
#highest_correl(all_r)
#equation = eqn_constructor(data, all_r_sorted)
insurance_prediction = analysis('Insurance Report.csv')
chemicals_prediction = analysis('Chemicals Report.csv')