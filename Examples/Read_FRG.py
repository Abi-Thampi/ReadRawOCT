import numpy as np
import matplotlib.pyplot as plt
from ReadRawOCT import OCT_FRG_TDMS as pytdms


filename = "../../../grid42inten_3D_000.FRG"
frame_skip = 5
matrix = pytdms.read_frg(filename, frame_skip)  
#plt.imshow(matrix[0,:,:], cmap = 'binary')
#plt.show()