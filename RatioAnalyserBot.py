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
data = create_data('CompanyScreeningReport.csv')

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
    for i in range(1, len(data[EPS_col])+1):
        if not isnumber(data[EPS_col][i]): #invalid value
            PE_ratios.append('-')
        elif not isnumber(data[day_close_col][i]): #invalid value in corresponding metric
            PE_ratios.append(None)
        else: #Valid values in both share close column and PBV column
            PE_ratios.append((float(data[day_close_col][i])/float(data[EPS_col][i])))  
    dataset.insert(len(dataset.columns), 'PE_ratio', PE_ratios)

PE_ratio(data, 'P/LTM Diluted EPS Before Extra [Latest] (x)', 'Day Close Price [Latest] (SGD, Historical rate)')

#Function to convert all the values in the column from string to float - does not update original dataframe
def col_str_to_int(dataset, col):
    temp = dataset[col]
    for i in range(1, len(temp)+1 ):
        if isnumber(temp[i]):
            temp[i] = float(temp[i])
    return temp
    
#Function taking in 2 column headers, and then determining the correl coeff (r value) for the two sets of data
def correl(dataset, col1, col2):
    x2, y2 = [], []
    x = col_str_to_int(dataset, col1)
    y = col_str_to_int(dataset, col2)
    #print(x, y)
    for i in range(1, len(x)+1 ):
        if isnumber(x[i]) and isnumber(y[i]):
            x2.append(x[i])
            y2.append(y[i])
    x_array = np.array(x2)
    y_array = np.array(y2)
    print(x_array, y_array)
    r = np.corrcoef(x_array, y_array)
    if round(r[0,1], 5) == round(r[1,0], 5):
        return round(r[0,1], 5)
    else:
        return r
    
print(correl(data, 'PE_ratio', 'Return on Equity % [LTM]'))
