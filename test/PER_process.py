#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Python Test Box
# ------------------------------------------------------------------------------
"""
    :package: WireSharkLogger
    :brief: Control class for Latencies logging activities 
    :author: Attilio Panniello
    :date:   2020/12/03
"""

# ------------------------------------------------------------------------------
# versioning
# ------------------------------------------------------------------------------
__version__ = '0.1'
__author__ = 'Attilio Panniello'
# ------------------------------------------------------------------------------
# imports
# -----------------------------------------------------------------------------

import numpy as np
import pandas as pd

calibration_meas = './Savituck_TRM-2Mbps-01.csv'
per_meas = './Savituck_RCV-2Mbps-01.csv'

minChanel = 3
maxChanel = 79

calibration_chanels = maxChanel- minChanel +1
calibration_fields = ['Channel', 'H1 (dBm)']
calibration_df = pd.read_csv(calibration_meas, skiprows=1,nrows=calibration_chanels, usecols=calibration_fields, sep=',', na_values=" , ")

trmCalibrationPwr = 8
targetPERrd = 0.14
# targetPERrd = '74.56%'

# Custom function taken from https://stackoverflow.com/questions/12432663/what-is-a-clean-way-to-convert-a-string-percent-to-a-float
# Used to convert string type 'xx%' to int value xx when importing dataframe from csv file with the use of converters argument.
def p2f(x):
    return float(x.strip('%'))/100

attenuationValues =[0,20,40,60,80,85,87,89,90,91,92,93,95,98,100]
# print(df.loc[df['Name'] == 'Bert'])
# Attenuation_Enum
# attenuationValues =[0,89,100]


# attenuationSteps = 15 # number of different attenuations used
attenuationSteps = len(attenuationValues) # number of different attenuations used
print(f'Number of attenuation steps: {attenuationSteps}')
PER_lines = calibration_chanels*attenuationSteps
PER_fields = ['PerRx(%)', 'Channel','Attenuation']
PER_df = pd.read_csv(per_meas, skiprows=1,nrows=PER_lines, usecols=PER_fields, converters={'PerRx(%)':p2f}, sep=',', na_values=" , ")
print(f'PER_df end : {PER_df.tail()}')

sorted_PER_df = PER_df[PER_df['PerRx(%)'] >= targetPERrd]
sorted_PER_df_min = PER_df[PER_df['PerRx(%)'] >= targetPERrd]['PerRx(%)'].min()
sorted_PER_df_max = PER_df[PER_df['PerRx(%)'] >= targetPERrd]['PerRx(%)'].max()
# Code syntax example example
# mValue[x] = round(results_df[(results_df.noise == noise)& (results_df.samples > 2000)]['RB score [%]'].mean())
print(f'sorted_PER_df end : {sorted_PER_df.tail()}')
print(f'--------------------------------------------')
print(f'PER_df start : {PER_df.head()}')
print(f'sorted_PER_df start : {sorted_PER_df.head()}')
print(f'--------------------------------------------')
print(f'sorted_PER_df_min : {sorted_PER_df_min}')
print(f'sorted_PER_df_max : {sorted_PER_df_max}')
print(f'--------------------------------------------')

# for i in range(minChanel, maxChanel+1, 1):
#     Received_power = calibration_df['H1 (dBm)'][calibration_df.Channel == i]
#     print(f'Received_power on chanel {i} :{Received_power}')
    
#     for k in attenuationValues:
#         print(f'Attenuation value:{k}')
#         # PER_df['Rx InputPower [dBm]'] = Received_power - PER_df['Attenuation'][(PER_df.Channel == i) & (PER_df.Attenuation == k)]
#         print(f'Received_power : {Received_power}')
#         # print(PER_df['Attenuation'][(PER_df.Channel == i)])
        
#         tmp = PER_df['Attenuation'][(PER_df.Channel == i) & (PER_df['PerRx(%)'] >= targetPERrd)]
#         print(f'Programmed attenuation @ PER >= {targetPERrd} % : {tmp.head()}')
#         # print(calibration_df['H1 (dBm)'][calibration_df.Channel == i] - PER_df['Attenuation'][(PER_df.Channel == i) & (PER_df.Attenuation == k)])
#         # PER_df['Rx InputPower [dBm]'] = calibration_df['H1 (dBm)'][calibration_df.Channel == i]
#         print(f'---------------')

# Rx InputPower [dBm]
print(f'calibration_df beginning : {calibration_df.head()}')
print(f'calibration_df end : {calibration_df.tail()}')
# print(calibration_df.head())
# print(calibration_df.tail())

print(f'PER_df beginning : {PER_df.head()}')
print(f'PER_df end : {PER_df.tail()}')

print(f'sorted_PER_df beginning : {sorted_PER_df.head()}')
print(f'sorted_PER_df end : {sorted_PER_df.tail()}')
# print(PER_df.head())
# print(PER_df.tail())

# print(calibration_df.Channel.dtype)
# print(calibration_df['H1 (dBm)'].dtype)
# print(list(calibration_df.columns))
# # calibration_df['Channel'] = calibration_df['Channel'].astype('int')
# print(calibration_df['H1 (dBm)'][calibration_df.Channel == 6])
# a = calibration_df['H1 (dBm)'][calibration_df.Channel == 6]

# print(f'{a} +2 = {a+2}')

# col_mean_df_header_list = ['device','No Noise', 'Very Noisy', 'LAN', 'Home 20Mhz', 'Tournament']

# mean_df = pd.DataFrame(columns=col_mean_df_header_list)
# # ignore_index=True

# print(results_df.head())

# # del results_df

# print(results_df[results_df.samples > 10000])

# print(results_df[(results_df.device =='Garnet Molduck TopazTKL Molduck LS2') & (results_df.noise == 'No Noise Nominal') & (results_df.test == 'M11_R08_K05_R08_SYM')])

# mean_df = results_df[(results_df.device =='Garnet Molduck TopazTKL Molduck LS2') & (results_df.noise == 'No Noise Nominal') & (results_df.test == 'M11_R08_K05_R08_SYM')]

# meanRB = mean_df["RB score"].mean()

# print(f'RB Score mean value : {meanRB}')

