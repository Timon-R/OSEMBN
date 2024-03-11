'''
Give 2 dimensional data, and an x value the interpolator will interpolate or extrapolate the data for the x value.

@author: Timon Renzelmann
'''

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def interpolate_polynomial(xy, x_new, degree): # for polynomial interpolation
    x = xy[:, 0]
    y = xy[:, 1]
    coeffs = np.polyfit(x, y, degree)
    y_new = np.round(np.polyval(coeffs, x_new), 2)
    
    # Calculate the r-squared value for the polynomial fit
    y_pred = np.polyval(coeffs, x)
    residuals = y - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - (ss_res / ss_tot)    
    return y_new, r2
   

def func(x, a, b, c): # uses the exponential decay function
    return a * np.exp(-b * (x-2015)) + c

# Data
x = np.arange(2021, 2051)
y = np.array([34.08, 33.95, 33.82, 33.68, 33.55, 33.42, 33.29, 33.16, 33.03, 32.90, 32.78, 32.65, 32.52, 32.39, 32.27, 32.14, 32.02, 31.89, 31.77, 31.64, 31.52, 31.40, 31.27, 31.15, 31.03, 30.91, 30.79, 30.67, 30.55, 30.43])

# Interpolate the data 
popt, pcov = curve_fit(func, x, y)

x_new = np.arange(2015, 2061)
y_new_exp = func(x_new, *popt)
y_new_exp = np.round(y_new_exp, 2)

print("Exponential decay function results 2015-2060:", y_new_exp)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'o', label='Original data')
plt.plot(x_new, y_new_exp, '--', label='Exponential decay function')
plt.legend()
plt.show()


def calculate_percentage_difference(lower, middle, upper):
    diff_down = (middle - lower) / middle * 100
    diff_up = (upper - middle) / middle * 100
    return diff_down, diff_up

