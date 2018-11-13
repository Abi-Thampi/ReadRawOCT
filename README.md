# ReadRawOCT

This code reads raw .TDMS and .FRG files OCT fringe data into .npy. Run the setup.py script to install the module:

```
python setup.py install 
```

## Dependancies
You will need to install the nptdms module for this code to work properly. You can do this using conda:

```
conda install nptdms -c conda-forge
```

You will also need Pillow if you want to save the data to an image:

```
conda install pillow -c conda-forge
```

