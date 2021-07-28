import os
import numpy as np
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
from numpy.testing._private.utils import tempdir

#For web plotting
import base64
from io import BytesIO
from flask import Flask
from matplotlib.figure import Figure

# Excel file --> array. *Indexing: [columns][row]
def create_data(folder_name):
    df_temp = pd.DataFrame()

    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_name):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    for filename in listOfFiles:
        df = pd.read_excel(filename, header=0, skiprows=7)
        df_temp = df.append(df_temp, ignore_index=True)

    if len(df_temp) == 0:
        print("ERROR: No data records available.")

    # Make the column header names into a separate record at the top of the table
    # top_row = pd.DataFrame(test_data.columns).T
    # top_row.columns = top_row.iloc[0]
    # df_temp = pd.concat([top_row, df_temp], axis=0).reset_index(drop=True)
    return df_temp

#CSV file --> array
def create_data_from_csv(filename):
    df = pd.read_csv(filename, header = 1).values
    df = pd.DataFrame(df)
    df.columns = df.iloc[0] #set header
    df = df.drop(df.index[0])
    return df

#csv file --> array. *Indexing: [columns][row]
def create_data_from_csv(filename):
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


# Converts all the values of a DataFrame column into a float
def to_float(column):
    return list(filter(lambda x: isnumber(x), column))


# Functions to return various metrics of a particular column index
def total(dataset, columnindex):
    return np.sum(list(map(lambda x: float(x), filter(lambda x: isnumber(x), dataset[columnindex][1:]))))


def average(dataset, columnindex):
    return np.mean(list(map(lambda x: float(x), filter(lambda x: isnumber(x), dataset[columnindex][1:]))))


# Calculate Price to Earnings Ratio (Day close / EPS) - inputs 2 columns and creates a new column with PE ratios
def PE_ratio(dataset, EPS_col, day_close_col):
    PE_ratios = []
    for i in range(len(dataset[EPS_col])):
        if not isnumber(dataset[EPS_col][i]):  # invalid value
            PE_ratios.append('-')
        elif not isnumber(dataset[day_close_col][i]):  # invalid value in corresponding metric
            PE_ratios.append(None)
        else:  # Valid values in both share close column and PBV column
            PE_ratios.append((float(dataset[day_close_col][i]) / float(dataset[EPS_col][i])))
    dataset.insert(len(dataset.columns), 'PE_ratio', PE_ratios)


# Convert all the values in the column from string to float - does not update original dataframe
def col_str_to_int(dataset, col):
    temp = dataset[col]
    try: 
        temp[0]
        for i in range(len(temp)):
            if isnumber(temp[i]):
                temp[i] = float(temp[i])
    except:
        for i in range(1, len(temp)+1):
            if isnumber(temp[i]):
                temp[i] = float(temp[i])
    return temp


# Takes in 2 column headers, and then determining the correl coeff (r value) for the two sets of data
def correl(dataset, dependent, independent):
    x2, y2 = [], []
    y = col_str_to_int(dataset, dependent)
    x = col_str_to_int(dataset, independent)
    try:
        y[0]
        for i in range(len(y)):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
    except:
        for i in range(1, len(y)+1):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
    x_array = pd.Series(x2)
    y_array = pd.Series(y2)
    x_array_no_outliers = x_array[x_array.between(x_array.quantile(0.10), x_array.quantile(0.90))]
    y_array_no_outliers = y_array[y_array.between(y_array.quantile(0.10), y_array.quantile(0.90))]
    x_corresponding_list, y_corresponding_list = [], []
    for i in x_array_no_outliers.index:
        if i in y_array_no_outliers.index:
            x_corresponding_list.append(x_array[i])
            y_corresponding_list.append(y_array[i])
    x_corresponding_array = pd.Series(x_corresponding_list)
    y_corresponding_array = pd.Series(y_corresponding_list)
    r = np.corrcoef(x_corresponding_array, y_corresponding_array)
    if round(r[0, 1], 5) == round(r[1, 0], 5):
        return round(r[0, 1], 5)
    else:
        return r


# find correlation between all independent and dependent variables
def find_all_r(dataset, independent, dependent):
    all_r = {}
    for base in dependent:
        if base not in all_r:
            all_r[base] = []
        for metric in independent:
            r = correl(dataset, base, metric)
            all_r[base].append([metric, r])
    return all_r


# from a dct of all correlations, return the highest correlation for each dependent variable in a new dct
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


# sorts all correlation values by largest (best) to smallest (worst)
def sort_all_r(all_r):
    for base, values in all_r.items():
        values.sort(key=lambda x: abs(x[1]), reverse=True)
    return all_r


# Takes in 2 columns (note the order), returns the equation of best fit line y = mx + c
def graph_function(dataset, dependent, independent):
    x2, y2 = [], []
    y = col_str_to_int(dataset, dependent)
    x = col_str_to_int(dataset, independent)
    try:
        y[0]
        for i in range(len(y)):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
    except:
        for i in range(1, len(y)+1 ):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
    x_array = pd.Series(x2)
    y_array = pd.Series(y2)
    x_array_no_outliers = x_array[x_array.between(x_array.quantile(0.10), x_array.quantile(0.90))]
    y_array_no_outliers = y_array[y_array.between(y_array.quantile(0.10), y_array.quantile(0.90))]
    x_corresponding_list, y_corresponding_list = [], []
    for i in x_array_no_outliers.index:
        if i in y_array_no_outliers.index:
            x_corresponding_list.append(x_array[i])
            y_corresponding_list.append(y_array[i])
    eqn = np.polyfit(x_corresponding_list, y_corresponding_list, 1)
    # print(f'{round(eqn[0], 3)}x + {round(eqn[1], 3)}')
    return eqn


# Takes in a regression line and an independent variable (x), then returns the dependent variable (y)
def predict(eqn, independent):
    model = np.poly1d(eqn)
    output = model(independent)
    return output


# Find the dependent variables, based on user inputs. Can optionally take in list of independent variables to reduce number of selections
def find_dependents(dataset, *independents):
    valid_nums = []
    message = 'POSSIBLE DEPENDENT VARIABLES: \n'
    for i in range(len(dataset.columns)):
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[
            i] == 'Industry Classifications' \
                or dataset.columns[i] == 'Company Type':
            continue
        elif independents:  # if there are predetermined independent variables
            if dataset.columns[i] in independents[0]:
                continue
        valid_nums.append(i)
        message += str(i) + ' ' * (5 - len(str(i))) + f'{dataset.columns[i]} \n'
    print(message)  # asks for input of dependent variables
    selection = input(
        'Please enter the number of the selected dependent variables, seperated by a comma (no spaces):  ')
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
    print(message2)  # displays confirmation
    confirmation = input('Confirm? y/n:  ')
    if confirmation == 'y':
        print('\nDependent variables confirmed!\n')
        return output
    else:
        temp = find_dependents(dataset, *independents)
        return temp


# Find the independent variables, based on user inputs. Can optionally take in list of dependent variables to reduce number of selections
def find_independents(dataset, *dependents):
    valid_nums = []
    message = 'POSSIBLE INDEPENDENT VARIABLES: \n'
    for i in range(len(dataset.columns)):
        if dataset.columns[i] == 'Company Name' or dataset.columns[i] == 'Exchange:Ticker' or dataset.columns[
            i] == 'Industry Classifications' \
                or dataset.columns[i] == 'Company Type':
            continue
        elif dependents:  # if there are predetermined dependent variables
            if dataset.columns[i] in dependents[0]:
                continue
        valid_nums.append(i)
        message += str(i) + ' ' * (5 - len(str(i))) + f'{dataset.columns[i]} \n'
    print(message)  # asks for input of independent variables
    selection = input(
        'Please enter the number of the selected independent variables, seperated by a comma (no spaces). Enter "all" to select all:  ')
    output = []
    message2 = '\nSELECTED INDEPENDENT VARIABLES: \n'
    if selection == 'all':
        for i in valid_nums:
            output.append(dataset.columns[i])
            message2 += f'{dataset.columns[i]}\n'
        print(message2)  # displays confirmation
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
    print(message2)  # displays confirmation
    confirmation = input('Confirm? y/n:  ')
    if confirmation == 'y':
        print('\nIndependent variables confirmed!\n')
        return output
    else:
        temp = find_independents(dataset, *dependents)
        return temp


# Combines finding dependents and independents into one function, then defines them globally. Also returns both in a list.
def find_dependents_and_independents(dataset):
    global dependents
    global independents
    dependents = find_dependents(dataset)
    independents = find_independents(dataset, dependents)
    return [dependents, independents]


# takes in a dct of sorted r values, and asks the user to choose which 2 to do analysis on
def eqn_constructor(dataset, all_r_sorted):
    keys = list(all_r_sorted.keys())
    print('CHOOSE YOUR DEPENDENT VARIABLE: \n')
    for i in range(len(keys)):
        print(f'{i}:    {list(all_r_sorted.keys())[i]}')
    dependent_selection = input(
        '\nAll possible selections have been displayed. \nPlease enter your selection, or enter "exit" to stop the program:   ')
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


# Takes in a dct of sorted r values, then returns predictions for the greatest r value for each dependent variable.
# This function is split into 2 smaller parts - auto_eqn and auto_prediction
def auto_eqn_and_prediction(dataset, all_r_sorted):
    output = {}  # storage for function return
    memory = {}  # storage for user entered values, so that users would not need to enter the same value twice
    prints = '\nPrice Multiples Prediction: \n'  # storage for printed text
    for dependent, independent in all_r_sorted.items():
        temp_target_indep_variable = independent[0][0]
        eqn = graph_function(dataset, dependent, temp_target_indep_variable)
        if temp_target_indep_variable in memory:
            independent_value = memory[temp_target_indep_variable]
        else:
            independent_value = input(
                f'\nPlease provide a value for the independent variable {temp_target_indep_variable}\
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


# Takes in sorted correlation values and outputs equations for the best indep variable for each dependent variable in a dictionary
def auto_eqn(dataset, all_r_sorted):
    output = {}
    for dependent, independent in all_r_sorted.items():
        target_indep_variable = independent[0][0]
        correl = independent[0][1]
        equation = graph_function(dataset, dependent, target_indep_variable)
        output[dependent] = [target_indep_variable, equation, correl]
    return output


# Takes in equations for the best indep variable and asks for user input, to generate predictions
def auto_prediction(dataset, best_eqns, show_correl=0):
    output = {}  # storage for function return
    memory = {}  # storage for user entered values, so that users would not need to enter the same value twice
    prints = '\nPrice Multiples Prediction: \n'  # storage for printed text
    input_values = []
    for dependent, best_independent_and_correl in best_eqns.items():
        target_indep_variable, equation, correl = best_independent_and_correl
        independent_value = input(
            f'\nPlease provide a value for the independent variable {target_indep_variable}. Enter "exit" to stop the program: ')
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
            input_values.append(independent_value_float)
            if show_correl:
                prints += f'{dependent} (corr = {round(correl, 2)}):    {round(prediction, 3)}\n'
            else:
                prints += f'{dependent}:    {round(prediction, 3)}\n'
            memory[target_indep_variable] = independent_value_float
        output[dependent] = [target_indep_variable, prediction]
    print(prints)
    return ([output, input_values])


#Creates matplotlib plots
def plot_graphs(data, best_eqns, predictions):
    j = 0
    for dependent, indep_eqn_corr in best_eqns.items():
        x2, y2 = [], []
        y = col_str_to_int(data, dependent)
        independent = indep_eqn_corr[0]
        x = col_str_to_int(data, independent)
        for i in range(1, len(y)):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
        x2array = pd.Series(x2)
        y2array = pd.Series(y2)

        # remove outliers
        x_array_no_outliers = x2array[x2array.between(x2array.quantile(0.10), x2array.quantile(0.90))]
        y_array_no_outliers = y2array[y2array.between(y2array.quantile(0.10), y2array.quantile(0.90))]
        x_corresponding_list, y_corresponding_list = [], []
        for i in x_array_no_outliers.index:
            if i in y_array_no_outliers.index:
                x_corresponding_list.append(x2array[i])
                y_corresponding_list.append(y2array[i])

        prediction = predictions[0][dependent][1]  # Predicted value for dependent variable (y axis)
        selected_dependent = predictions[1][j]  # Input value for each particular dependent variable (x axis)
        j += 1  # Cycles through the input values

        # Creating best lit line
        eqn = np.polyfit(x_corresponding_list, y_corresponding_list, 1)
        gradient = eqn[0]
        intercept = eqn[1]
        x_corresponding_array = np.array(x_corresponding_list)
        fit = gradient * x_corresponding_array + intercept

        print('x len', len(x_corresponding_list))
        print('y len', len(y_corresponding_list))
        print('gradient', gradient)
        print('intercept', intercept)

        # Plotting
        fig = plt.figure()
        ax = fig.subplots()
        ax.plot(x_corresponding_list, fit, color='black', label='Linear fit')  # Best fit line
        ax.scatter(x_corresponding_list, y_corresponding_list, s=1, label='Data points')  # Individual data points
        ax.plot(selected_dependent, prediction, 'rx', label='Selected Company', markersize=10)

        # Labelling the graph
        ax.set_title(f'{dependent} against {independent}', fontsize='small')
        ax.set_ylabel(f'{dependent}')
        ax.set_xlabel(f'{independent}')
        ax.legend()
    plt.show(block=False)
    return eqn


# Function to do full analysis based on the best indep values with highest correl
def auto_analysis(filename):
    data = create_data(filename)
    dependents_and_independents = find_dependents_and_independents(data)
    all_r = find_all_r(data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    best_eqns = auto_eqn(data, all_r_sorted)
    predictions = auto_prediction(data, best_eqns, 1)
    plot_graphs(data, best_eqns, predictions)
    return predictions


def user_prediction(dataset, best_eqns, user_inputs):
    # user_inputs = [industry_type, revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital]
    dct, input_values = {}, []
    independents = ['Total Revenues, 3 Yr CAGR % [LTM] (%)', 'Return on Equity % [LTM]', 'Current Ratio [LTM]',
                    'EBITDA Margin % [LTM]', \
                    'Total Asset Turnover [Latest Annual]', 'Total Debt/Capital % [Latest Annual]']
    for dependent, indep_eqn_correl in best_eqns.items():
        index = independents.index(indep_eqn_correl[0])
        value = user_inputs[index]
        prediction = predict(indep_eqn_correl[1], value)
        dct[dependent] = [indep_eqn_correl[0], prediction]
        input_values.append(value)
    return ([dct, input_values])

#Filters by industry and resets index
def industry_filter(data, industry):
    filter = data['Industry Classifications'] == industry
    filtered_data = data[filter]
    filtered_data = filtered_data.reset_index(drop=True)
    return filtered_data

def get_industries(data):
    return list(data['Industry Classifications'].unique())

# Takes in a set number of values for some fixed independent variables, and returns a dictionary with key: dependent variable and value: best prediction
# Solely for website
def output_website(folder_location, user_inputs):
    # user_inputs = [industry_type, revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital]
    if len(user_inputs) != 7:
        print('Please enter all the required values.')
        return None

    variable_values = user_inputs[1:]
    data = create_data(folder_location)
    global industry_data
    industry_data = industry_filter(data, user_inputs[0])
    dependents = ['P/LTM Diluted EPS Before Extra [Latest] (x)', 'P/BV [Latest] (x)']
    independents = ['Total Revenues, 3 Yr CAGR % [LTM] (%)', 'Return on Equity % [LTM]', 'Current Ratio [LTM]',
                    'EBITDA Margin % [LTM]', \
                    'Total Asset Turnover [Latest Annual]', 'Total Debt/Capital % [Latest Annual]']
    all_r = find_all_r(industry_data, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    global best_eqns
    global predictions
    best_eqns = auto_eqn(industry_data, all_r_sorted)
    predictions = user_prediction(industry_data, best_eqns, variable_values)
    #plot_graphs(industry_data, best_eqns, predictions)
    #return web_plot(industry_data, best_eqns, predictions)
    return [best_eqns, predictions]

def web_plot(folder_location, best_eqns, predictions):
    j = 0
    data = create_data(folder_location)
    for dependent, indep_eqn_corr in best_eqns.items():
        x2, y2 = [], []
        y = col_str_to_int(data, dependent)
        independent = indep_eqn_corr[0]
        x = col_str_to_int(data, independent)
        for i in range(1, len(y)):  # remove blanks
            if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
        x2array = pd.Series(x2)
        y2array = pd.Series(y2)

        # remove outliers
        x_array_no_outliers = x2array[x2array.between(x2array.quantile(0.10), x2array.quantile(0.90))]
        y_array_no_outliers = y2array[y2array.between(y2array.quantile(0.10), y2array.quantile(0.90))]
        x_corresponding_list, y_corresponding_list = [], []
        for i in x_array_no_outliers.index:
            if i in y_array_no_outliers.index:
                x_corresponding_list.append(x2array[i])
                y_corresponding_list.append(y2array[i])

        prediction = predictions[0][dependent][1]  # Predicted value for dependent variable (y axis)
        selected_dependent = predictions[1][j]  # Input value for each particular dependent variable (x axis)
        j += 1  # Cycles through the input values

        # Creating best lit line
        eqn = np.polyfit(x_corresponding_list, y_corresponding_list, 1)
        gradient = eqn[0]
        intercept = eqn[1]
        x_corresponding_array = np.array(x_corresponding_list)
        fit = gradient * x_corresponding_array + intercept

        # Plotting
        fig = Figure()
        ax = fig.subplots()
        ax.plot(x_corresponding_list, fit, color='black', label='Linear fit')  # Best fit line
        ax.scatter(x_corresponding_list, y_corresponding_list, s=1, label='Data points')  # Individual data points
        ax.plot(selected_dependent, prediction, 'rx', label='Selected Company', markersize=10)

        # Labelling the graph
        ax.set_title(f'{dependent} against {independent}', fontsize='small')
        ax.set_ylabel(f'{dependent}')
        ax.set_xlabel(f'{independent}')
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"

def web_plot_2(folder_location, best_eqns, predictions, plottype, industry, user_input_values):
    data = create_data(folder_location)
    data = industry_filter(data, industry)
    target_best_eqn = best_eqns[plottype]
    #target_prediction = predictions[plottype]
    x2, y2 = [], []
    y = col_str_to_int(data, plottype)
    independent = target_best_eqn[0]
    x = col_str_to_int(data, independent)
    for i in range(1, len(y)):
        if isnumber(y[i]) and isnumber(x[i]):
                y2.append(y[i])
                x2.append(x[i])
    x2array = pd.Series(x2)
    y2array = pd.Series(y2)

    # remove outliers
    x_array_no_outliers = x2array[x2array.between(x2array.quantile(0.10), x2array.quantile(0.90))]
    y_array_no_outliers = y2array[y2array.between(y2array.quantile(0.10), y2array.quantile(0.90))]
    x_corresponding_list, y_corresponding_list = [], []
    for i in x_array_no_outliers.index:
        if i in y_array_no_outliers.index:
            x_corresponding_list.append(x2array[i])
            y_corresponding_list.append(y2array[i])
    #print('no outlier len', len(x_corresponding_list), len(y_corresponding_list))

    prediction = predictions[0][plottype][1]  # Predicted value for dependent variable (y axis)
    #print('prediction', prediction)
        
    # Creating best lit line
    eqn = np.polyfit(x_corresponding_list, y_corresponding_list, 1)
    gradient = eqn[0]
    intercept = eqn[1]
    x_corresponding_array = np.array(x_corresponding_list)
    #print(x_corresponding_array)
    #print('x len', len(x_corresponding_list))
    #print('gradient', gradient)
    #print('intercept', intercept)
    fit = gradient * x_corresponding_array + intercept
    user_input_val = user_input_values[best_eqns[plottype][0]]

    # Plotting
    #fig = plt.figure()
    fig = Figure()
    ax = fig.subplots()
    ax.plot(x_corresponding_list, fit, color='black', label='Linear fit')  # Best fit line
    ax.scatter(x_corresponding_list, y_corresponding_list, s=1, label='Data points')  # Individual data points
    ax.plot(user_input_val, prediction, 'rx', label='Selected Company', markersize=10)

    # Labelling the graph
    ax.set_title(f'{plottype} against {independent}', fontsize='small')
    ax.set_ylabel(f'{plottype}')
    ax.set_xlabel(f'{independent}')
    ax.legend()
    
    buf = BytesIO()
    fig.savefig(buf, format="png")
    graph_image = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'<img src="data:image/png;base64,{graph_image}" alt="Plot" style="max-width:100%; height:auto;" width="600" height="400"/>'
    
def find_unique_industries(data):
    unique_array = data['Industry Classifications'].unique()
    unique_list = list(unique_array)
    unique_list.sort()
    primary_only_list = []
    #Select first option (primary industry)
    for industry in unique_list:
        seperate_industry = industry.split('; ')
        primary_industry = seperate_industry[0]
        if primary_industry not in primary_only_list:
            primary_only_list.append(primary_industry)

    primary_only_list_no_duplicates = []
    for indiv in primary_only_list:
        if '(Primary)' in indiv:
            primary_only_list_no_duplicates.append(indiv)
    return primary_only_list_no_duplicates

if __name__ == "__main__":
    print('hello')
    ####TEMP TESTING STUFF####
    # 1. Testing standalone functions
    #insurance_data = create_data_from_csv('Insurance Report.csv')
    test_data = create_data('data/')
    unique_industries = find_unique_industries(test_data)
    test_data_filtered = industry_filter(test_data, 'Health Care (Primary)')
    chemicals_data = create_data_from_csv('Chemicals Report.csv')
    # correl(test_data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
    # highest_correl(all_r)
    # eqn = graph_function(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
    # predict(eqn, 10)
    # dependents = find_dependents(data)
    # independents = find_independents(data, dependents)
    dependents_and_independents = find_dependents_and_independents(test_data_filtered)
    all_r = find_all_r(test_data_filtered, independents, dependents)
    all_r_sorted = sort_all_r(all_r)
    # highest_correl(all_r)
    best_eqns = auto_eqn(test_data_filtered, all_r_sorted)
    predictions = auto_prediction(test_data_filtered, best_eqns, 1)
    # equation = eqn_constructor(chemicals_data, all_r_sorted)
    # insurance_prediction = user_analysis('Insurance Report.csv')
    # chemicals_prediction = user_analysis('Chemicals Report.csv')
    # auto_eqn_and_prediction(chemicals_data, all_r_sorted)
    # temp_result = output_website('Chemicals Report.csv', ["Chemicals",1,1,1,1,1,1])
    plot_graphs(test_data_filtered, best_eqns, predictions)
    web_plot_2('data/', best_eqns, predictions, 'P/LTM Diluted EPS Before Extra [Latest] (x)')

    # 2. Testing full functions
    # full_analysis = auto_analysis('Chemicals Report.csv')
    # full_analysis = auto_analysis('Insurance Report.csv')

    now = datetime.now()
    results = output_website("data/", ["Health Care (Primary)", 10, 10, 10, 10, 1, 10])
    print(datetime.now() - now)

#test_data = create_data('data/')
#filtered_data = industry_filter(test_data, "Health Care (Primary)")
#get_industries(chemicals_data)
#get_industries(test_data)