import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

#csv file --> array. *Indexing: [columns][row]
data = pd.read_csv('CompanyScreeningReport (3).csv', header=1).values
data = pd.DataFrame(data)

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

#Function taking in 2 column indexes, and then determining the correl coeff (r value) for the two sets of data
def correl(colindex1, colindex2):
    pass