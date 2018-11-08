from nptdms import TdmsFile,TdmsObject,TdmsWriter,ChannelObject
import matplotlib.pylab as plt
from matplotlib.collections import PathCollection
import numpy as np
from PIL import Image
from scipy import signal,ndimage
import numpy.ma as ma
import os as os
import glob as glob
import struct

### Example of use:

### Read the raw data and convert to C_Scan matrix using the read_tdms function. The number of B_scans and A_scans are required to shape the C_scan:

#A_scan_num = 714
#B_scan_num = 150

#Data0  =  pytdms.read_tdms("Raw_C-Scan/G0_S1_XY_Ch0.tdms", A_scan_num, B_scan_num)
#Data1  =  pytdms.read_tdms("Raw_C-Scan/G0_S1_XY_Ch1.tdms", A_scan_num, B_scan_num)

###  Process the raw PS_OCT data to find the intensity and retardation matrices using the Scan_processing_3D function. If save == True the processed data will be saved as a numpy arrays with the given name.

#Int, Ret = pytdms.Scan_processing_3D(Data0,Data1,'Raw_C-Scan/G0_S1_XY',save = True)

### If you just want to process a single B_Scan you can use the Scan_processing_2D function. 

#Int_2D, Ret_2D = pytdms.Scan_processing_2D(Data0[50,:,:],Data1[50,:,:])

### to save the C_scan or B_scan as a tiff you can use the Save_Image funtion:

## to save a C_Scan:
#pytdms.Save_Image('Raw_C-Scan/G0_S1_XY_Int.tiff', Int)

## to save a B_Scan:
#pytdms.Save_Image('Raw_C-Scan/G0_S1_XY_Int.tiff', Int[50])

def read_tdms(filename, A_scan_num, B_scan_num):

    ## Read the TDMS data from the PS-OCT system and write to a C-Scan matrix.
    ## inputs filename = TDMS file location, A_scan_num is the number of A_Scans in each B_Scan and B_scan_num is the number of B_Scans in the C_Scan.
    tdms_file = TdmsFile(filename) ##import the data as a TDMS
    data =  tdms_file.object('Untitled', tdms_file.group_channels('Untitled')[0].channel).data ## Extract the data
    
    A_scan_length = int(len(data)/B_scan_num/A_scan_num) # calculate A_scan length
    data.resize((B_scan_num,A_scan_num,A_scan_length))
    C_scan = np.array(data) 
    del data    
    return(C_scan)


def Scan_processing_3D( C_scan_CH0, C_scan_CH1, string, name, save = False):
#### Turn the channel data into Intensity and Birefringence matrices

## Inputs 3D numpy matrices for each channel. Outputs are the Intenstiy and Retardation  3D matrices. If save == True, the processed data is saved as a numpy array using the provided name.
    Intensity = []
    Retardation = []
    ### for each B_scan 
    for x in range(0,len(C_scan_CH1[:,0,0])):

    ### for each channel compute the Intensity (Int) and Retardation (Ret).
        ch1 = C_scan_CH1[x,:,:]
        ch0 = C_scan_CH0[x,:,:]
        Int, Ret = Scan_processing_2D(ch0,ch1)

    ### append the B_scan to the C_scan
        Intensity.append(Int)
        Retardation.append(Ret)
    ### save the data to a .npy file    
    if save == True:    
        np.save(string + name + 'Int.npy', np.array(Intensity))
        np.save(string + name + 'Ret.npy', np.array(Retardation))
    return np.array(Intensity), np.array(Retardation)

def Scan_processing_2D(B_scan_CH0, B_scan_CH1):  
## Inputs 2D numpy matrices for a B_scan in each channel. Outputs are the Intenstiy and Retardation  2D matrices.
    
    for x in range(len(B_scan_CH0)):
        B_scan_CH1[x] = np.hanning(len(B_scan_CH1[x]))*B_scan_CH1[x]
        B_scan_CH0[x] = np.hanning(len(B_scan_CH0[x]))*B_scan_CH0[x]

    A_length = len(B_scan_CH1[0])
    fft_ch0 = np.fft.fft(B_scan_CH0)
    fft_ch1 = np.fft.fft(B_scan_CH1)
    
#Take the asbolute
    abs_ch0 = np.absolute(fft_ch0)
    abs_ch1 = np.absolute(fft_ch1)

#Now create the image from the data
    Int = np.rot90(np.sqrt(abs_ch0**2 + abs_ch1**2)[:,0:int(A_length/2)],3)
    Ret = np.rot90(np.arctan(abs_ch1/abs_ch0)[:,0:int(A_length/2)],3)
    Int = Int[:,0:(np.size(B_scan_CH0,0))]
    Ret = Ret[:,0:(np.size(B_scan_CH0,0))]
    return(Int, Ret)

def Save_Image(ImName, Mat):

    Mat = (np.amax(Mat)/Mat*255).astype(np.int16)
    # This function saves the convert matrix to a greyscale image    

    if Mat.ndim > 2:
        # make a list of images from Mat
        imlist = []
        for m in Mat:
            imlist.append(Image.fromarray(m))
        #save multiframe image
        imlist[0].save(ImName, save_all=True, append_images=imlist[1:])

    else:    
        im = Image.fromarray(Mat)
        im.save(ImName)


def read_frg(filename, B_scan_skip):
    # pylint: disable = W0612
    ### this function is used to read raw fringe data from a commercial thorlabs OCT system which saves fringe data as .FRG. The function takes the file name of the .frg data and an integer number of B-scans which can be skipped if necessary.
    #### example use:

    #import numpy as np
    #import matplotlib.pyplot as plt
    #import tdmsCode as pytdms 
    #filename = "../../../grid42inten_3D_000.FRG"
    #frame_skip = 5
    #C_Scan = pytdms.read_frg(filename, frame_skip)  

    ### currently this code is not working correctly: the header information is being correctly identified but the actual data is scrambled. This is most likely an issue where 14-bit integers have been stored in 16-bit (2 bytes).
   
    with open(filename, 'rb') as binary_file:
        ### read 
        header = binary_file.read(512)
        
        width = int.from_bytes(header[20:24], byteorder = 'little')
        depth = int.from_bytes(header[24:28], byteorder = 'little')
        B_scan_num = int.from_bytes(header[28:32], byteorder = 'little')
        C_scan_num = int.from_bytes(header[32:36], byteorder = 'little')
        
        FFT_length = int.from_bytes(header[36:40], byteorder = 'little')
        Record_length = int.from_bytes(header[44:48], byteorder = 'little')
        print(FFT_length, Record_length)
        PSOCT = int.from_bytes(header[48:50],byteorder = 'little')
        Frame_size_bytes = int.from_bytes(header[40:44], byteorder = 'little')
        Frame_size = width*FFT_length*2*2
        matrix = np.zeros((B_scan_num, depth, width))
        
        
        for x in range(1,2):

            Frame = binary_file.read(39)
            header2 = Frame[0:40]
            a_scan = []
            a_scan2 = []
            count = 0
            for x in range(0,int(B_scan_num)):
                for y in range(0,FFT_length,2):    
                    a_scan.append(int.from_bytes(binary_file.read(2), byteorder = 'little', signed = True))
                for z in range(0,FFT_length,2):
                    a_scan2.append(int.from_bytes(binary_file.read(2), byteorder = 'little', signed = True))
            a_scan = np.array(a_scan) 
            b_scan = np.reshape(a_scan, (FFT_length,-1))
            a_scan2 = np.array(a_scan2) 
            b_scan2 = np.reshape(a_scan2, (FFT_length,-1))
            print(np.shape(b_scan))

            Channel_A = np.fft.fftshift(np.fft.fft(b_scan[0:len(b_scan[:,0]):2,:] ))
            Channel_B = np.fft.fftshift(np.fft.fft(b_scan[0:len(b_scan2[:,0]):2,:] ))
            plt.plot(b_scan[0])
            plt.show()
            plt.imshow(abs(Channel_A**2 + Channel_B**2), cmap = 'binary', vmax = 10**12, vmin = 10**10)
            plt.show()
            
        binary_file.close()
    return(matrix)