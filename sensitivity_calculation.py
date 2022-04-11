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

results_df = pd.read_csv('./results_df.csv', sep=',', na_values=" , ")
per_df = pd.read_csv('./RCV2M.csv', sep=',', na_values=" , ")
calibration_df = pd.read_csv('./TRM2M.csv', sep=',', na_values=" , ")

col_mean_df_header_list = ['device','No Noise', 'Very Noisy', 'LAN', 'Home 20Mhz', 'Tournament']


mean_df = pd.DataFrame(columns=col_mean_df_header_list)
# ignore_index=True

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

# User interaction section
dataPayload = int(input("Please enter payload length in bytes [default = 10]:") or 10 )
isGaming = yes_no("Gaming [y or Return] or Unifying [n] DUT?")

if isGaming == True:
    preambleAndAdress = 6
    CRC = 3
        
else:
    preambleAndAdress = 5
    CRC = 2

toto = 1.125
totalBytesPerPacket = preambleAndAdress + toto + dataPayload + CRC  
totalBitsPerPacket = 8*totalBytesPerPacket

targetPER = 
targetPERrd = round(targetPER,2) 


# End of User interaction section

print(results_df.head())

# del results_df

print(results_df[results_df.samples > 10000])

print(results_df[(results_df.device =='Garnet Molduck TopazTKL Molduck LS2') & (results_df.noise == 'No Noise Nominal') & (results_df.test == 'M11_R08_K05_R08_SYM')])

mean_df = results_df[(results_df.device =='Garnet Molduck TopazTKL Molduck LS2') & (results_df.noise == 'No Noise Nominal') & (results_df.test == 'M11_R08_K05_R08_SYM')]

meanRB = mean_df["RB score"].mean()

print(f'RB Score mean value : {meanRB}')

