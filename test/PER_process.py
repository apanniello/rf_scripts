#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Python Test Box
# ------------------------------------------------------------------------------
"""
    :package: RF_scripts
    :brief: Script to automate sensitivity calculation baesd on eRTS output files (RCV & TRM) 
    :author: Attilio Panniello
    :team: Wireless Connectivity 
    :date:   2022/05/25
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
import matplotlib
import matplotlib.pyplot as plt
import csv
from pathlib import Path
# path = Path(path_to_file)
# path.is_file()

# # # FLAG used for debug console printings
#
debug = True # Set to FALSE in normal mode

# # # Input file settings section
#
calibration_meas = Path('./Savituck_TRM-2Mbps-01.csv')
calibration_meas_path_exists = calibration_meas.is_file()
print(f'--------------------------------------------')
print(f'TRM eRTS file found : {calibration_meas_path_exists}')

# per_meas_path = Path('./Savituck_RCV-2Mbps-01 - Copy.csv')
per_meas_path = Path('./Savituck_RCV-2Mbps-01.csv')
per_meas_path_exists = per_meas_path.is_file()
print(f'RCV eRTS file found : {per_meas_path_exists}')

attenuator_calibration_file_path = Path('./J7211A_Correction.csv')
attenuator_calibration_file_path_exists = attenuator_calibration_file_path.is_file()
print(f'Attenuator calibration file found : {per_meas_path_exists}')

# # # Output file settings section
#
sensitivity_meas = Path('./Savituck_Sensitivity-2Mbps-01.csv')


# # Parse eRTS RCV output file and find all measurment settings (channels & attenuation values)
#
# with open(per_meas_path, 'r') as csv_file:
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
        # Read all lines in the file one by one and find first occurence only.
        occurence_Enum = False
        occurence_Min = False
        occurence_Max = False
        occurence_Step = False   
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if str(string_to_search + '_Enum') in line:
                # If yes, then add the line number & line as a tuple in the list
                if not occurence_Enum:
                    results_str = line.rstrip()
                    tempList = results_str.split("=")
                    listName = tempList[0]
                    # listName = line.rstrip().split("=")[0]
                    listEnum.append(listName)
                    listValuesStr = tempList[1].split(",")
                    if debug:
                        print(f'listValuesStr = {listValuesStr}')
                    if listValuesStr != ['']:
                        listValues = [int(x) for x in listValuesStr]
                        # [int(x) for x in a]
                        listEnum.append(listValues)
                        listEnumFlag = True
                    tempList = []
                    occurence_Enum = True
            elif str(string_to_search + '_Min') in line:
                if not occurence_Min:
                    listMin = line.rstrip().split("=")[1]
                    occurence_Min = True
                else:
                    if debug:
                        print(f'skipped on min')
            elif str(string_to_search + '_Max') in line:
                if not occurence_Max:
                    listMax = line.rstrip().split("=")[1]
                    occurence_Max = True
            elif str(string_to_search + '_Step') in line:
                if not occurence_Step:
                    listStep = line.rstrip().split("=")[1]
                    occurence_Step = True
    
    if debug:
        print(f'listEnumFlag = {listEnumFlag}')
    if listEnumFlag == True :
        list = listEnum
    else:
        if debug:
            print(f'listMinMax = {listMinMax}')
            print(f'listMin type : {type(listMin)}')
        listMinMax.append(str(string_to_search + '_Enum'))
        listMinMax.append([int(listMin),int(listMax),int(listStep)])
        list = listMinMax
    if debug:
        print(f'list = {list}')
    # Return list of tuples containing line numbers and lines where string is found
    return list

# Custom function taken from https://stackoverflow.com/questions/12432663/what-is-a-clean-way-to-convert-a-string-percent-to-a-float
# Used to convert string type 'xx%' to int value xx when importing dataframe from csv file with the use of converters argument.
def p2f(x):
    return float(x.strip('%'))/100

# a = search_meas_params_in_csv(per_meas_path,'Attenuation')
# print(f'Attenuations found : {a} of type {type(a)}')
# print(f'--------------------------------------------')

# c = search_meas_params_in_csv(per_meas_path,'Channel')
# print(f'Channels found : {c} of type {type(c)}')
# print(f'--------------------------------------------')

##########################################################################
#
# Measurement settings definition

attenuationValues = search_meas_params_in_csv(per_meas_path,'Attenuation')[1]
print(f'--------------------------------------------')
print(f'Attenuation values : {attenuationValues}')
print(f'--------------------------------------------')
channelValues = search_meas_params_in_csv(per_meas_path,'Channel')
print(f'Channels values : min={channelValues[1][0]}, max={channelValues[1][1]},step={channelValues[1][2]}')
print(f'--------------------------------------------')
minChanel = channelValues[1][0]
maxChanel = channelValues[1][1]
stepChanel = channelValues[1][2]

calibration_chanels = maxChanel- minChanel +1
calibration_fields = ['Channel', 'H1 (dBm)']
calibration_df = pd.read_csv(calibration_meas, skiprows=1,nrows=calibration_chanels, usecols=calibration_fields, sep=',', na_values=" , ")

attenuator_cal_fields = ['Attenuation Setting', '2450']
attenuator_cal_df = pd.read_csv(attenuator_calibration_file_path, skiprows=1, usecols=attenuator_cal_fields, sep=',', na_values=" , ")

targetPERrd = 0.149

# number of different attenuations used
if len(attenuationValues)==3 and attenuationValues[2]==1 :
    attenuationSteps= attenuationValues[1]-attenuationValues[0]+1
else:
    attenuationSteps = len(attenuationValues)
print(f'Number of attenuation steps: {attenuationSteps}')


PER_lines = calibration_chanels*attenuationSteps
PER_fields = ['PerRx(%)', 'Channel','Attenuation']
PER_df = pd.read_csv(per_meas_path, skiprows=1,nrows=PER_lines, usecols=PER_fields, converters={'PerRx(%)':p2f}, sep=',', na_values=" , ")

sorted_PER_df = PER_df[PER_df['PerRx(%)'] <= targetPERrd]
##########################################################################
#
# Debug printings
#
if debug:
    print(f'calibration_df start : {calibration_df.head()}')
    print(f'--------------------------------------------')
    print(f'PER_df start : {PER_df.head()}')
    print(f'--------------------------------------------')
    print(f'sorted_PER_df head : {sorted_PER_df.head()}')
    print(f'--------------------------------------------')
    print(f'sorted_PER_df tail : {sorted_PER_df.tail()}')
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
# channel_df_per_max = pd.DataFrame(columns=channel_df_fields)

for i in range(minChanel, maxChanel+1, 1):
    channel_df = sorted_PER_df[sorted_PER_df['Channel']==i]
    channel_per_max = sorted_PER_df[sorted_PER_df['Channel']==i]['PerRx(%)'].max()
    per_max_attenuation = sorted_PER_df[sorted_PER_df['Channel']==i]['Attenuation'].max()
    # channel_df_per_max = channel_df[channel_df['PerRx(%)'] == channel_per_max]
    channel_df_per_max = channel_df[channel_df['Attenuation'] == per_max_attenuation]
    # channel_df_per_max['Rx InputPower [dBm]'] = ""
    # channel_df_per_max.loc[:,'Rx InputPower [dBm]'] = i
    # channel_df_per_max['Rx InputPower [dBm]'] = i
    attenuation_mask = channel_df_per_max['Channel']==i
    calibration_mask = calibration_df['Channel'] == i
    # Attenuation = channel_df_per_max[channel_df_per_max['Channel']==i]['Attenuation'].item()
    # DF.loc[DF.someCondition=condition, 'A'].item() : to avoid chained-indexing
    # Attenuation = channel_df_per_max.loc[channel_df_per_max['Channel']==i,'Attenuation'].item()
    if attenuator_calibration_file_path_exists: # take into account attenuator file if  it exists
        attenuation_uncal = channel_df_per_max.loc[attenuation_mask,'Attenuation'].item()
        attenuator_mask = attenuator_cal_df['Attenuation Setting'] == attenuation_uncal
        attenuation = attenuator_cal_df.loc[attenuator_mask,'2450'].item()
    else:
        attenuation = channel_df_per_max.loc[attenuation_mask,'Attenuation'].item()
    # DF.loc[DF.someCondition=condition, 'A'].item()
    # RxPwr = calibration_df[calibration_mask]['H1 (dBm)'] - attenuation : chained-indexing
    RxPwr = calibration_df.loc[calibration_mask,'H1 (dBm)'].item() - attenuation # : to avoid chained-indexing
    RxPwr_column.append(RxPwr)
    sensitivity_PER_df = sensitivity_PER_df.append(channel_df_per_max, ignore_index=True)

# sensitivity_PER_df = sensitivity_PER_df.reset_index()
sensitivity_PER_df['Sensitivity [dBm]'] = RxPwr_column

DS_sensitivity_ADDR0 = -89
DS_sensitivity_ADDRxx = DS_sensitivity_ADDR0 + 3
DS_sensitivity_ADDR0column = [DS_sensitivity_ADDR0]*calibration_chanels
DS_sensitivity_ADDRxxcolumn = [DS_sensitivity_ADDRxx]*calibration_chanels
sensitivity_PER_df['Datasheet Sensitivity @ ADDR0 [dBm]'] = DS_sensitivity_ADDR0column
sensitivity_PER_df['Datasheet Sensitivity @ ADDRxx [dBm]'] = DS_sensitivity_ADDRxxcolumn

if debug:
    print(f'channel_df :\n {channel_df}')
    print(f'type channel_df : {type(channel_df)}')
    print(f'--------------------------------------------')
    print(f'channel_per_max : {channel_per_max}')
    print(f'--------------------------------------------')
    print(f'channel_df_@min : {channel_df_per_max}')
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
if sensitivity_PER_df is not None:
    # pd.concat([df3, df4], axis=1)).to_csv('foo.csv')
    sensitivity_PER_df.to_csv(sensitivity_meas, header=True, index=False)   # write file to drive
    print(f'Output file {sensitivity_meas} saved.')
    print(f'--------------------------------------------')
#
##########################################################################


##########################################################################
#
# Graphs plotting section

# fig,ax = plt.subplots()

ax = sensitivity_PER_df.plot(x='Channel', y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'])
fig = ax.get_figure() #https://stackoverflow.com/questions/18992086/save-a-pandas-series-histogram-plot-to-file
ax.set_title('Sensitivity Measurement Results')
ax.set_xlim((minChanel, maxChanel))
ax.set_ylim((-90, -80))
xminor_locator=matplotlib.ticker.MultipleLocator(base=1.0)
xmajor_locator=matplotlib.ticker.MultipleLocator(5)
ax.xaxis.set_minor_locator(xminor_locator)
ax.xaxis.set_major_locator(xmajor_locator)
ax.set_xlabel('Channel')
ax.set_ylabel('Sensitivity [dBm]')
ax.grid(visible=True, which='major') # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html


# sensitivity_PER_df.plot(x='Channel', y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'], grid = True, ax = ax)


# xAxisLim = [minChanel, maxChanel]
# yAxisLim = [-93, -83]
# sensitivity_PER_df.plot(x='Channel',y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'], xlim = xAxisLim, ylim = yAxisLim, xlabel='Channel', ylabel='Sensitivity [dBm]', title='Sensitivity Measurement Results')
# marker='o'
# plt.axis([minChanel, maxChanel, -100, -70])
plt.show()
fig.savefig('./Sensitivity.png')


