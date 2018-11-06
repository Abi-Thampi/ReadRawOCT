from ReadRawOCT import OCT_FRG_TDMS as pytdms
import matplotlib.pyplot as plt
import numpy as np
import os, glob

filelocation = "J:/OCT data/13_oct11/sample699/"
savelocation = "J:/OCT data/13_oct11/sample699/"

#filelocation = "D:/OCT_data/8-oct2/sample695/"
#savelocation = "D:/OCT_data/Numpy_data/695/"
A_scan_num = 714
B_scan_num = 150

for file in [x for x in os.listdir(filelocation) if x.endswith("Ch0.tdms")]:
    name = os.path.splitext(file)[0].split('_')[0] + '_'

    if os.path.isfile(savelocation + name + "Int.npy") == False:
        Data0  =  pytdms.read_tdms(filelocation + name + "Ch0.tdms" , A_scan_num, B_scan_num)

        Data1  =  pytdms.read_tdms(filelocation + name + "Ch1.tdms", A_scan_num, B_scan_num)

        pytdms.Scan_processing_3D(Data0,Data1,savelocation ,name,save = True)
        print('grid written')

print('Done')