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
attenuator_calibration_file = './J7211A_Correction.csv'

minChanel = 3
maxChanel = 79

calibration_chanels = maxChanel- minChanel +1
calibration_fields = ['Channel', 'H1 (dBm)']
calibration_df = pd.read_csv(calibration_meas, skiprows=1,nrows=calibration_chanels, usecols=calibration_fields, sep=',', na_values=" , ")
attenuator_cal_fields = ['Attenuation Setting', '2450']
attenuator_cal_df = pd.read_csv(attenuator_calibration_file, skiprows=1, usecols=attenuator_cal_fields, sep=',', na_values=" , ")

trmCalibrationPwr = 8
targetPERrd = 0.14
# targetPERrd = '74.56%'

# Custom function taken from https://stackoverflow.com/questions/12432663/what-is-a-clean-way-to-convert-a-string-percent-to-a-float
# Used to convert string type 'xx%' to int value xx when importing dataframe from csv file with the use of converters argument.
def p2f(x):
    return float(x.strip('%'))/100

attenuationValues =[0,20,40,60,80,85,87,89,90,91,92,93,95,98,100]
attenuationSteps = len(attenuationValues) # number of different attenuations used
# print(f'Number of attenuation steps: {attenuationSteps}')
PER_lines = calibration_chanels*attenuationSteps
PER_fields = ['PerRx(%)', 'Channel','Attenuation']
PER_df = pd.read_csv(per_meas, skiprows=1,nrows=PER_lines, usecols=PER_fields, converters={'PerRx(%)':p2f}, sep=',', na_values=" , ")

##########################################################################
#
# Debug printings
#
print(f'calibration_df start : {calibration_df.head()}')
print(f'--------------------------------------------')
print(f'PER_df start : {PER_df.head()}')
print(f'--------------------------------------------')
sorted_PER_df = PER_df[PER_df['PerRx(%)'] >= targetPERrd]
print(f'sorted_PER_df start : {sorted_PER_df.head()}')
print(f'--------------------------------------------')

# EXAMPLES:
# 1) Suppose this dataframe:

# >>> print(df.head())
#     N   M  S
# 0  10  42  4
# 1  39  22  2
# 2  11  52  4
# 3  97  42  2
# 4  66  72  1

# How do I get the row where a column has the minimum value? For example, how do I get the row where column 'S' has value 1?

# ANSWER
# df[df['S']==df['S'].min()]


# 2) https://stackoverflow.com/questions/58583661/how-do-i-select-all-rows-with-a-minimum-value-that-meet-a-condition-in-another-c

#ANSWER
# df[(df['Points']==0) & (df['Day']==df[df['Points']==0]['Day'].min())]

RxPwr_column = []
sensitivity_PER_df = pd.DataFrame()
# channel_df_fields = ['PerRx(%)','Channel','Attenuation','Rx InputPower [dBm]']
# channel_df_min = pd.DataFrame(columns=channel_df_fields)

for i in range(minChanel, maxChanel+1, 1):
    channel_df = sorted_PER_df[sorted_PER_df['Channel']==i]
    channel_min = sorted_PER_df[sorted_PER_df['Channel']==i]['PerRx(%)'].min()
    channel_df_min = channel_df[channel_df['PerRx(%)'] == channel_min]
    # channel_df_min['Rx InputPower [dBm]'] = ""
    # channel_df_min.loc[:,'Rx InputPower [dBm]'] = i
    # channel_df_min['Rx InputPower [dBm]'] = i
    attenuation_mask = channel_df_min['Channel']==i
    calibration_mask = calibration_df['Channel'] == i
    # Attenuation = channel_df_min[channel_df_min['Channel']==i]['Attenuation'].item()
    # DF.loc[DF.someCondition=condition, 'A'].item() : to avoid chained-indexing
    # Attenuation = channel_df_min.loc[channel_df_min['Channel']==i,'Attenuation'].item()
    attenuation = channel_df_min.loc[attenuation_mask,'Attenuation'].item()
    # DF.loc[DF.someCondition=condition, 'A'].item()
    # RxPwr = calibration_df[calibration_mask]['H1 (dBm)'] - attenuation : chained-indexing
    RxPwr = calibration_df.loc[calibration_mask,'H1 (dBm)'].item() - attenuation # : to avoid chained-indexing
    RxPwr_column.append(RxPwr)
    sensitivity_PER_df=sensitivity_PER_df.append(channel_df_min, ignore_index=True)

# sensitivity_PER_df = sensitivity_PER_df.reset_index()
sensitivity_PER_df['Sensitivity [dBm]'] = RxPwr_column

print(f'channel_df :\n {channel_df}')
print(f'type channel_df : {type(channel_df)}')
print(f'--------------------------------------------')
print(f'channel_min : {channel_min}')
print(f'--------------------------------------------')
print(f'channel_df_@min : {channel_df_min}')
print(f'--------------------------------------------')
print(f'--------------------------------------------')
print(f'sensitivity_PER_df :\n {sensitivity_PER_df}')
print(f'--------------------------------------------')
print(f'--------------------------------------------')
print(f'attenuator_cal_df : {attenuator_cal_df}')
print(f'--------------------------------------------')
print(f'--------------------------------------------')
print(f'last attenuation : {attenuation}')
print(f'last RxPwr : {RxPwr}')


##########################################################################
#
# Save sensitivity attenuation values into ooutput file
csv_path = './output.csv'
if sensitivity_PER_df is not None:
    # pd.concat([df3, df4], axis=1)).to_csv('foo.csv')
    sensitivity_PER_df.to_csv(csv_path, header=True, index=False)   # write file to drive
    print(f'File {csv_path} saved.')
#
##########################################################################
