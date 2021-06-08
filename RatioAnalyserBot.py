import numpy as np
from matplotlib import pyplot as plt
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

#Determine all independent variables (secondary metrics), outputs as list
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

####TEMP TESTING STUFF####
data = create_data('CompanyScreeningReport.csv')  
correl(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
comparison_bases = ['P/LTM Diluted EPS Before Extra [Latest] (x)', 'P/BV [Latest] (x)']
comparison_metrics = create_comparison(data, comparison_bases)
all_r = find_all_r(data, comparison_metrics, comparison_bases)
highest_correl(all_r)
eqn = graph_function(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Return on Equity % [LTM]')
predict(eqn, 10)