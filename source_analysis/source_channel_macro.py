import ROOT as r
r.gROOT.SetBatch(1)
import csv
import numpy as np
import os
from pandas import *

# reading CSV file
data = read_csv("sourceRuns.csv")
 
# converting column data to list
channel_cut = data['Channel'].tolist()
run_number = data['Run'].tolist()

#channel_cut = [16, 18, 60, 28]
#run_number = [507, 508, 526, 537]
sbMean = 5
sbRMS = 1.2

directory = "source_calib"
parent_dir = "./"
path = os.path.join(parent_dir, directory)
 
# Create the directory
os.makedirs(path, exist_ok=True)

#To initiate the .csv files
f1 = open('./source_calib/param_values1.csv', 'w')
f2 = open('./source_calib/param_values2.csv', 'w')
# create the csv writers
writer1 = csv.writer(f1)
writer2 = csv.writer(f2)

for i in np.arange(len(run_number)):
    #Open this from the milliQanSourceRuns folder!
    inputFile = r.TFile("./milliQanSourceRuns/MilliQan_Run{run}_default_v28.root".format(run=run_number[i])) #Local
    #inputFile = r.TFile("/homes/milliqan/milliqanOffline/Run3Detector/outputRun3/v29/MilliQan_Run{run}_default_v29.root".format(run=run_number[i])) #UCSB
    inputTree = inputFile.Get("t")

    height_histo = r.TH1D("height_histo", "chan"+str(channel_cut)+";height", 200, 0, 400) #Not necessary here.
    area_histo = r.TH1D("area_histo", "chan{chan}_run{run}; area".format(chan=channel_cut[i], run=run_number[i]), 200, 0, 20000)
    oC = r.TCanvas()

    #Performing the cuts and filling the desired histo
    for event in inputTree:
        for iPulse in range(len(event.height)):
            if(event.chan[iPulse] == channel_cut[i] and iPulse == 0):
                #print(event.sidebandMean[channel_cut[i]])
                if(np.fabs(event.sidebandMean[channel_cut[i]]) < sbMean and np.fabs(event.sidebandRMS[channel_cut[i]]) < sbRMS):
                    area_histo.Fill(event.area[iPulse])

    area_histo.Draw("")

    #Performing the fits.
    f1 = r.TF1("f1", "gaus", 0, 2000)
    f2 = r.TF1("f2", "gaus", 4000, 16000)

    area_histo.Fit("f1", "RL")
    r.gStyle.SetOptFit(1011)
    params1 = f1.GetParameters()

    area_histo.Fit("f2", "RL+")
    params2 = f2.GetParameters()

    #Saving the params in a writeable format.
    csv_params1 = []
    csv_header1 = []
    csv_params2 = []
    csv_header2 = []

    csv_params1.append(run_number[i])
    csv_params1.append(channel_cut[i])
    csv_params2.append(run_number[i])
    csv_params2.append(channel_cut[i])
    
    if i==0:
        csv_header1.append("Run")
        csv_header1.append("Channel")
        csv_header2.append("Run")
        csv_header2.append("Channel")

    for j in np.arange(f1.GetNpar()):
        csv_params1.append(params1[j])
        csv_header1.append(f1.GetParName(int(j)))
    for k in np.arange(f2.GetNpar()):
        csv_params2.append(params2[k])
        csv_header2.append(f2.GetParName(int(k)))

    #print(csv_params1, csv_params2, csv_header1, csv_header2)
    
    #Writing the fit params to the .csv file!
    if i==0:
        writer1.writerow(csv_header1)
        writer2.writerow(csv_header2)
    writer1.writerow(csv_params1)
    writer2.writerow(csv_params2)

    oC.SaveAs("./source_calib/area_histo_chan{chan}_run{run}.png".format(chan=channel_cut[i], run=run_number[i]))
