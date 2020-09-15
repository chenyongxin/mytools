# -*- coding: utf-8 -*-
"""
ASCII input/output. 

@author: CHEN Yongxin
"""

import numpy as np
import pandas as pd
import sys
import os
import datetime

__all__ = ["outputs", "outputs_lite", "inputs"]

CELL_WIDTH = 15

def outputs(name, array, items, description=None):
    """
    Full version of spreadsheet output. The file looks like
    
    # Description line 1 ...
    # Description line 2 ...
    $
    item1  item2  item3  ...
     xxx    xxx    xxx   ...
     xxx    xxx    xxx   ...
     ...
    
    # denotes the line is a comment. 
    $ is used to separate the main data part from the preamble part. 
    It also means the stuff after $ is valuable. Each cell uses white space to
    separate.
    
    Parameters
    ----------
    name: str
        Name of file.
    array: array-like
        2D array.
    items: list
        List of items. Every item is a string.
    description: str, optional
        Additional description for output file. Use ''' xxx ''' for multiple 
        line input.
    """
    if os.path.isfile(name):
        sys.exit("File {} already exists.".format(name))
    
    if len(items) != array.shape[1]:
        sys.exit("Number of items must match columns of data.")
    
    for item in items:
        if len(item) > CELL_WIDTH-1:
            sys.exit(f"Item length must less than {CELL_WIDTH-1} characters.")
    
    with open(name, 'w') as fh:
        now = datetime.datetime.now()
        fh.write("# @ CHEN Yongxin \n")
        fh.write("# Date: {}/{}/{} \n".format(now.year, now.month, now.day))
        fh.write("# Time: {}:{} \n".format(now.hour, now.minute))
        if description is not None:
            for line in description.splitlines():
                fh.write("# {} \n".format(line))
        
        fh.write("$ \n")
        dump_array(fh, array, items)
        
        
def outputs_lite(name, array, items):
    """
    Light-weighted version of spreadsheet output. The spreadsheet looks like
    
    items ->  |item1  item2  item3  ...
    data  ->  | xxx    xxx    xxx   ...
              | xxx    xxx    xxx   ...
              | ...
     
    Parameters
    ----------
    name: str
        Name of file.
    array: array-like
        2D array.
    items: list
        List of items. Every item is a string.
    """
    if os.path.isfile(name):
        sys.exit("File {} already exists.".format(name))
        
    if len(items) != array.shape[1]:
        sys.exit("Number of items must match columns of data.")
    
    for item in items:
        if len(item) > CELL_WIDTH-1:
            sys.exit(f"Item length must less than {CELL_WIDTH-1} characters.")
    
    with open(name, 'w') as fh:
        dump_array(fh, array, items)

def dump_array(fh, array, items):
    """
    Dump array to a file with a specific file handle.
    
    Parameters
    ----------
    fh: object
        File handle.    
    array: array-like
        2D array.
    items: list
        List of items. Every item is a string.
    """
    # write header
    line = ""
    for item in items:
        line += " "*(CELL_WIDTH-len(item))+item 
    fh.write(line+'\n')

    # write array in scientific notation
    nrows, ncols = array.shape
    fmt = "{:" + "{}.{}e".format(CELL_WIDTH, CELL_WIDTH//2-1) + "}"   
    for i in range(nrows):
        for j in range(ncols):
            fh.write(str(fmt.format(array[i, j])))
        fh.write('\n')

def inputs(name, to_numpy=False):
    """
    Full version of spreadsheet input. The file looks like
    
    # Description line 1 ...
    # Description line 2 ...
    $
    item1  item2  item3  ...
     xxx    xxx    xxx   ...
     xxx    xxx    xxx   ...
     ...
    
    # denotes the line is a comment. 
    $ is used to separate the main data part from the preamble part. 
    
    Parameters
    ----------
    name: str
        Name of file.
    to_numpy: bool, optional
        Convert data to a 2D numpy array if true. If not, returns pandas 
        dataframe. Default false.
    
    Returns
    -------
    r: data
        Returns pandas dataframe or numpy array.
    """
    with open(name, 'r') as fh:
        for i, line in enumerate(fh):
            if line.strip().find("$") == 0: 
                nrows = i+1             # no. of rows to $
                break
    
    try:
        df = pd.read_csv(name, delim_whitespace=True, skiprows=nrows)
    except UnboundLocalError:
        sys.exit("ASCII input file format error: no '$' found.")
        
    if to_numpy:
        return df.to_numpy()
    else:
        return df
    

if __name__ == "__main__":
    
    n = 100
    data = np.zeros((n, 3))
    data[:,0] = np.linspace(0, np.pi*2, n)
    data[:,1] = np.sin(data[:,0])
    data[:,2] = np.cos(data[:,1])
    items = ["t", "cos", "sin"]
    
    print("1. Test output data.")
    outputs("output.dat", data, items, description="Note: sinusoidal function")
    print("Data saved in output.dat. \n")
    
    print("2. Test lite output data.")
    outputs_lite("output_lite.dat", data, items)
    print("Data saved in output_lite.dat. \n")
    
    print("3. Test input data.")
    a = inputs("output.dat", to_numpy=False)
    print("Data read from output.dat: \n", a)