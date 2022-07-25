#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Python Test Box
# ------------------------------------------------------------------------------
"""
    :package: RF Connectivity Team Tools
    :brief: Calculate sensitivity from eRTS output files 
    :author: Attilio Panniello
    :date:   14/06/2022
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
from time import sleep,time
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import sys

inputFiles = input("Please put your measurement files (RCV-2Mbps-01.csv & TRM-2Mbps-01.csv) in inputFiles folder and press ENTER")

# # # Input file settings section
#
calibration_meas = Path('./inputFiles/TRM-2Mbps-01.csv')
calibration_meas_path_exists = calibration_meas.is_file()
print(f'--------------------------------------------')
print(f'TRM eRTS file found : {calibration_meas_path_exists}')
# per_meas_path = Path('./Savituck_RCV-2Mbps-01 - Copy.csv')
per_meas_path = Path('./inputFiles/RCV-2Mbps-01.csv')
per_meas_path_exists = per_meas_path.is_file()
print(f'RCV eRTS file found : {per_meas_path_exists}')

attenuator_calibration_file_path = Path('./inputFiles/J7211A_Correction.csv')
attenuator_calibration_file_path_exists = attenuator_calibration_file_path.is_file()
print(f'Attenuator calibration file found : {attenuator_calibration_file_path_exists}')
print(f'--------------------------------------------')

if not calibration_meas_path_exists or not per_meas_path_exists :
    print(f'Measurement datas not found, please copy them in inputFiles local folder...')
    sys.exit()
# # # Output file settings section
#
sensitivity_meas = Path('./outputFiles/Sensitivity-2Mbps-01.csv')

# ------------------------------------------------------------------------------
# meas configuration settings
# -----------------------------------------------------------------------------

#############
#Functions definitions

def yes_no(question):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
     
    while True:
        choice = input(question).lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           print ("Please respond with 'yes' or 'no'")

def defineTargetPER():

    print('Typical packet content :')
    print(f'---------------------------------------------------------------------------------------------------------')
    print(f'|Preamble+Adress(6 or 5 bytes) | Control Information(1.125 byte) | Payload(xx bytes) | CRC(3 or 2 bytes)|')
    print(f'---------------------------------------------------------------------------------------------------------\n')

    dataPayload = int(input("Please enter payload length in bytes [default = 10]:") or 10 )
    isGaming = yes_no("Gaming [y or Return] or Unifying [n] DUT?")

    if isGaming == True:
        preambleAndAdress = 6
        cRc = 3
            
    else:
        preambleAndAdress = 5
        cRc = 2

    controlInfo = 1.125

    print('\nUsed packet content :')
    print(f'-----------------------------------------------------------------------------------------------')
    print(f'|Preamble+Adress({preambleAndAdress} bytes) | Control Information(1.125 byte) | Payload({dataPayload} bytes) | CRC({cRc} bytes)|')
    print(f'-----------------------------------------------------------------------------------------------\n')

    totalBytesPerPacket = preambleAndAdress + controlInfo + dataPayload + cRc  
    totalBitsPerPacket = 8*totalBytesPerPacket

    targetBER = 0.1/100
    targetPER = 1-(1-targetBER)**(totalBitsPerPacket)
    print (f'Total number of Bits per Packet : {totalBitsPerPacket}')
    # print (f'Traget PER value for {dataPayload} bytes data payload : {targetPER}')
    targetPERrd = round(targetPER,3)
    print (f'Traget PER value for {dataPayload} bytes data payload : {targetPERrd}')

    return targetPERrd

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

# Senitivity graphs plotting function
def plotSensi(df,path,minDeltaPER):
    ax = df.plot(x='Channel', y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'], marker='.') #https://e2eml.school/matplotlib_points.html
    fig = ax.get_figure() #https://stackoverflow.com/questions/18992086/save-a-pandas-series-histogram-plot-to-file
    if minDeltaPER:
        ax.set_title('Sensitivity Measurement Results (Closest PER method)')
    else:
        ax.set_title('Sensitivity Measurement Results (Strict PER method)')
    ax.set_xlim((minChanel, maxChanel))
    ax.set_ylim((-93, -83))
    xminor_locator=matplotlib.ticker.MultipleLocator(base=1.0)
    xmajor_locator=matplotlib.ticker.MultipleLocator(5)
    ax.xaxis.set_minor_locator(xminor_locator)
    ax.xaxis.set_major_locator(xmajor_locator)
    ax.set_xlabel('Channel')
    ax.set_ylabel('Sensitivity [dBm]')
    ax.grid(visible=True, which='major') # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
    plotPath=path.with_suffix('.png')
    fig.savefig(plotPath)
    plt.show()
    # xAxisLim = [minChanel, maxChanel]
    # yAxisLim = [-93, -83]
    # sensitivity_PER_df.plot(x='Channel',y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'], xlim = xAxisLim, ylim = yAxisLim, xlabel='Channel', ylabel='Sensitivity [dBm]', title='Sensitivity Measurement Results')
    # marker='o'
    # plt.axis([minChanel, maxChanel, -100, -70])

#########################################################
# Start of User interaction section

# Target PER calculation based on packet length
targetPERrd = defineTargetPER()

# Choose PER calculation method (default = minimum PERdelta)
minDeltaPER = yes_no("Closest PER method ((abs[TargetPER - MeasPER])min) [y or Return] or strict PER method (MeasPER < TargetPER) [n]?")
# debug = False # Set to FALSE in normal mode
debug = True # Set to FALSE in normal mode
#########################################################
# End of User interaction section
startTime=datetime.now()


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
calibration_df_0dBm = pd.read_csv(calibration_meas, skiprows=1,nrows=calibration_chanels, usecols=calibration_fields, sep=',', na_values=" , ")

attenuator_cal_fields = ['Attenuation Setting', '2450']
attenuator_cal_df = pd.read_csv(attenuator_calibration_file_path, skiprows=1, usecols=attenuator_cal_fields, sep=',', na_values=" , ")

# targetPERrd = 0.149

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
# df_deltaPER = PER_df
PER_df['DeltaPER'] = abs(targetPERrd - PER_df['PerRx(%)'])
##########################################################################
#
# Debug printings
#
if debug:
    print(f'calibration_df_0dBm start : {calibration_df_0dBm.head()}')
    print(f'--------------------------------------------')
    print(f'PER_df head : {PER_df.head()}')
    print(f'--------------------------------------------')
    print(f'PER_df tail : {PER_df.tail()}')
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
# RxPwr_column2 = []
DS_sensitivity = []
sensitivity_PER_df = pd.DataFrame()


for i in range(minChanel, maxChanel+1, 1):
    if minDeltaPER:
        delta_per_min_val = PER_df[PER_df['Channel']==i]['DeltaPER'].min()
        channel_per_df = PER_df[(PER_df['Channel']==i) & (PER_df['DeltaPER']==delta_per_min_val)]
        per_max_attenuation = channel_per_df['Attenuation']

    else:
        channel_df = sorted_PER_df[sorted_PER_df['Channel']==i]
        per_max_attenuation = sorted_PER_df[sorted_PER_df['Channel']==i]['Attenuation'].max()
        channel_per_df = channel_df[channel_df['Attenuation'] == per_max_attenuation]
  

    attenuation_mask = channel_per_df['Channel']==i
    
    if attenuator_calibration_file_path_exists: # take into account attenuator file if  it exists
        attenuation_uncal = channel_per_df.loc[attenuation_mask,'Attenuation'].item()
        attenuator_mask = attenuator_cal_df['Attenuation Setting'] == attenuation_uncal
        attenuator_mask0 = attenuator_cal_df['Attenuation Setting'] == 0
        attenuation = attenuator_cal_df.loc[attenuator_mask,'2450'].item() - attenuator_cal_df.loc[attenuator_mask0,'2450'].item()
    else:
        attenuation = channel_per_df.loc[attenuation_mask,'Attenuation'].item()
    calibration_mask = calibration_df_0dBm['Channel'] == i
    RxPwr = calibration_df_0dBm.loc[calibration_mask,'H1 (dBm)'].item() - attenuation # : to avoid chained-indexing
    RxPwr_column.append(RxPwr)
    sensitivity_PER_df = sensitivity_PER_df.append(channel_per_df, ignore_index=True)

sensitivity_PER_df['Sensitivity [dBm]'] = RxPwr_column

DS_sensitivity_ADDR0 = -89
DS_sensitivity_ADDRxx = DS_sensitivity_ADDR0 + 3
DS_sensitivity_ADDR0column = [DS_sensitivity_ADDR0]*calibration_chanels
DS_sensitivity_ADDRxxcolumn = [DS_sensitivity_ADDRxx]*calibration_chanels
sensitivity_PER_df['Datasheet Sensitivity @ ADDR0 [dBm]'] = DS_sensitivity_ADDR0column
sensitivity_PER_df['Datasheet Sensitivity @ ADDRxx [dBm]'] = DS_sensitivity_ADDRxxcolumn

if debug:
    print(f'max attenuation @ perTarget  : {per_max_attenuation}')
    print(f'--------------------------------------------')
    print(f'channel_df_@min : {channel_per_df}')
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
plotSensi(sensitivity_PER_df,sensitivity_meas,minDeltaPER)
# sensitivity_PER_df.plot(x='Channel', y=['Sensitivity [dBm]','Datasheet Sensitivity @ ADDR0 [dBm]','Datasheet Sensitivity @ ADDRxx [dBm]'], grid = True, ax = ax)

#########################################################
endTime=datetime.now()
execTime=(endTime-startTime )
print(f'Script execution time: {execTime}')
#print(f'Measurement file name extension: {fileSaveTag}')

