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
import matplotlib.pyplot as plt
import csv

calibration_meas = './Savituck_TRM-2Mbps-01.csv'
# per_meas = './Savituck_RCV-2Mbps-01.csv'
per_meas = './Savituck_RCV-2Mbps-01 - Copy.csv'
attenuator_calibration_file = './J7211A_Correction.csv'
sensitivity_meas = './Savituck_Sensitivity-2Mbps-01.csv'


# # Parse file for measurment settings
# with open(per_meas, 'r') as csv_file:
#     csv_reader = csv.reader(csv_file)
#     for line in csv_reader:
#         if 'Attenuation_Enum' in line:
#             print(f'It''s here : {line}')
#         else:
#             print(f'Attenuation_Enum not found...')

#############
# Parsing functions
def search_string_in_file(file_name, string_to_search):
    """Search for the given string in file and return lines containing that string,
    along with line numbers"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append((line_number, line.rstrip()))
    # Return list of tuples containing line numbers and lines where string is found
    return list_of_results

def search_meas_params_in_csv(file_name, string_to_search):
    """Search for channels and attenuation values used for PER eRTS meas in .csv output file and return values"""
    line_number = 0
    listEnum = []
    listMinMax = []
    listEnumFlag = False
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if str(string_to_search + '_Enum') in line:
                # If yes, then add the line number & line as a tuple in the list
                results_str = line.rstrip()
                tempList = results_str.split("=")
                listName = tempList[0]
                # listName = line.rstrip().split("=")[0]
                listEnum.append(listName)
                listValuesStr = tempList[1].split(",")
                print(f'listValuesStr = {listValuesStr}')
                if listValuesStr != ['']:
                    listValues = [int(x) for x in listValuesStr]
                    # [int(x) for x in a]
                    listEnum.append(listValues)
                    listEnumFlag = True
                tempList = []
            elif str(string_to_search + '_Min') in line:
                listMin = line.rstrip().split("=")[1]
            elif str(string_to_search + '_Max') in line:
                listMax = line.rstrip().split("=")[1]
            elif str(string_to_search + '_Step') in line:
                listStep = line.rstrip().split("=")[1]
    
    print(f'listEnumFlag = {listEnumFlag}')
    if listEnumFlag == True :
        list = listEnum
    else:
        print(f'listMinMax = {listMinMax}')
        print(f'listMin type : {type(listMin)}')
        listMinMax.append(str(string_to_search + '_Enum'))
        listMinMax.append([int(listMin),int(listMax),int(listStep)])
        list = listMinMax
    print(f'list = {list}')
    # Return list of tuples containing line numbers and lines where string is found
    return list

# a = search_meas_params_in_csv(per_meas,'Attenuation')
# print(f'Attenuations found : {a} of type {type(a)}')
# print(f'--------------------------------------------')

# c = search_meas_params_in_csv(per_meas,'Channel')
# print(f'Channels found : {c} of type {type(c)}')
# print(f'--------------------------------------------')


attenuationValues = search_meas_params_in_csv(per_meas,'Attenuation')[1]
print(f'attenuationValues : {attenuationValues}')
print(f'--------------------------------------------')
channelValues = search_meas_params_in_csv(per_meas,'Channel')
print(f'channelValues : {channelValues}')
print(f'--------------------------------------------')
minChanel = channelValues[1][0]
maxChanel = channelValues[1][1]
stepChanel = channelValues[1][2]

calibration_chanels = maxChanel- minChanel +1
calibration_fields = ['Channel', 'H1 (dBm)']
calibration_df = pd.read_csv(calibration_meas, skiprows=1,nrows=calibration_chanels, usecols=calibration_fields, sep=',', na_values=" , ")

attenuator_cal_fields = ['Attenuation Setting', '2450']
attenuator_cal_df = pd.read_csv(attenuator_calibration_file, skiprows=1, usecols=attenuator_cal_fields, sep=',', na_values=" , ")

trmCalibrationPwr = 8
targetPERrd = 0.149
# targetPERrd = '74.56%'

# Custom function taken from https://stackoverflow.com/questions/12432663/what-is-a-clean-way-to-convert-a-string-percent-to-a-float
# Used to convert string type 'xx%' to int value xx when importing dataframe from csv file with the use of converters argument.
def p2f(x):
    return float(x.strip('%'))/100

# attenuationValues =[0,20,40,60,80,85,87,89,90,91,92,93,95,98,100]


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
DS_sensitivity = []
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
    sensitivity_PER_df = sensitivity_PER_df.append(channel_df_min, ignore_index=True)

# sensitivity_PER_df = sensitivity_PER_df.reset_index()
sensitivity_PER_df['Sensitivity [dBm]'] = RxPwr_column

DS_sensitivity = -86
DS_sensitivity_column = [DS_sensitivity]*calibration_chanels
sensitivity_PER_df['Datasheet Sensitivity [dBm]'] = DS_sensitivity_column

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
csv_path = sensitivity_meas
if sensitivity_PER_df is not None:
    # pd.concat([df3, df4], axis=1)).to_csv('foo.csv')
    sensitivity_PER_df.to_csv(csv_path, header=True, index=False)   # write file to drive
    print(f'File {csv_path} saved.')
#
##########################################################################


##########################################################################
#
# Graphs plotting section
sensitivity_PER_df.head
xAxisLim = [minChanel, maxChanel]
yAxisLim = [-100, -70]
sensitivity_PER_df.plot(x='Channel',y=['Sensitivity [dBm]','Datasheet Sensitivity [dBm]'], xlim = xAxisLim, ylim = yAxisLim, xlabel='Channel', ylabel='Sensitivity [dBm]', title='Sensitivity Measurement Results')
# plt.axis([minChanel, maxChanel, -100, -70])
# fig,ax = plt.subplots()

plt.show()