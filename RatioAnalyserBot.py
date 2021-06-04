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

####TEMP####
data = create_data('CompanyScreeningReport (3).csv')

#Helper function to check if a value in a cell is a float - returns False if cell is empty or NM
def isnumber(string):
    try:
        float(string)
        return True
    except:
        return False

#Function that converts all the values of a DataFrame column into a float
def to_float(column):
    return list(filter(lambda x: isnumber(x), column))

#Functions to return various metrics of a particular column index 
def total(columnindex):
    return np.sum(list(map(lambda x: float(x), filter(lambda x: isnumber(x), data[columnindex][1:]))))

def average(columnindex):
    return np.mean(list(map(lambda x: float(x), filter(lambda x: isnumber(x), data[columnindex][1:]))))

#To calculate Price to Earnings Ratio (Day close / EPS) - inputs 2 columns and creates a new column with PE ratios
def PE_ratio(dataset, EPS_col, day_close_col):
    PE_ratios = [] 
    for i in range(1, len(data[EPS_col])):
        if not isnumber(data[EPS_col][i]): #invalid value
            PE_ratios.append(None)
        elif not isnumber(data[day_close_col][i]): #invalid value in corresponding metric
            PE_ratios.append(None)
        else: #Valid values in both share close column and PBV column
            PE_ratios.append((float(data[day_close_col][i])/float(data[EPS_col][i])))  
    dataset.insert(len(dataset.columns), 'PE_ratio', PE_ratios)

def col_str_to_int(dataset, col):
    for val in dataset[col]:
        if isnumber(val):
            pass
    
#Function taking in 2 column headers, and then determining the correl coeff (r value) for the two sets of data
def correl(col1, col2):
    x = data[col1]
    y = data[col2]
#print(correl(4, 9))

pass

pass
