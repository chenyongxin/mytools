# -*- coding: utf-8 -*-
"""
Binary data reader.

@author: CHEN Yongxin
"""

import numpy as np
from struct import pack, unpack, calcsize

class BinaryReader(object):
    """
    Read a pure binary file. The binary file often contains massive time series
    data, which can be represented in a spreadsheet. The binary data looks as
    
    t1 | a1, b1, c1, d1, ..., 
    t2 | a2, b2, c2, d2, ...,
    t3 | a3, b3, c3, d3, ....
    
    The time series data ax, bx, cx could be in different types, e.g. integer, 
    float, double. This specific data format can be customized. The data in the
    specific location are homogeneous among lines/different time steps.
    """
    
    def __init__(self, name=None, prec='d'):
        """
        Initialize binary reader object. 
        
        Parameters
        ----------
        name: str, optional
            Name of path to a file.
        prec: char, optional
            Precision of data. Default doulbe.
        """
        self.nrows      = 0             # number of rows
        self.ncols      = 0             # number of columns
        self.data       = np.array(())  # data array
        self.prec       = prec          # precision
        self.fh         = None          # file handle
        self.customized = False         # customized data flag
        self.fmt        = None          # customized data format
        self.nbytes     = 0             # size of a line in bytes
        if name is not None:
            self.file(name)
    
    def file(self, name):
        """Open a binary file and return file handle."""
        self.fh = open(name, mode='rb')
        
    def customize(self, fmt):
        """
        Define a customized format.
        
        Parameters
        ----------
        fmt: str
            Data format in one line, e.g. 'iffffdddd'.
        """
        assert(type(fmt) is str)
        self.fmt        = fmt
        self.nbytes     = calcsize(fmt)     
        self.ncols      = len(fmt)          
        self.customized = True    
    
    def sort(self, ncols=None, trunc=None):
        """
        Sort time series data into a 2D array.
        
        Parameters
        ----------
        ncols: int, optional
            Number of columns in one line.
        trunc: int, optinoal
            Number of rows in truncated data. Use it to reduce data size.
        """
        # if not customize format, use the default prec to make format.
        if self.customized is False:
            assert(type(ncols) is int)
            self.nbytes = calcsize(self.prec)*ncols
            self.ncols = ncols
            self.fmt = ncols*self.prec
            
        # stack data line by line
        toTruncate = True if type(trunc) is int else False
        count = 0
        while True:
             buffer = self.fh.read(self.nbytes)
             if len(buffer) != self.nbytes: break    # reaches EOF
             newline = np.array(unpack(self.fmt, buffer))
             self.data = \
                 np.vstack((self.data, newline)) if self.data.size else newline
             count += 1
             if toTruncate: 
                 if count >= trunc: break
        self.nrows = count

    def shape(self):
        """
        Query shape of data. 
        
        Returns
        -------
        r: tuple
            (nrows, ncols).
        """
        return self.nrows, self.ncols
    
    def close(self):
        """Close the file."""
        self.fh.close()
        

if __name__ == "__main__":
   
    print('Save double-precision data 1-9 in test.bin. \n')
    with open('test.bin', 'wb') as fh:
        a = np.linspace(1,9,9)
        fh.write(pack("d"*9, *a))
    
    print('1. Read data to a 3*3 array')
    b = BinaryReader('test.bin')
    b.sort(ncols=3)
    print('data: \n', b.data)
    print('shape: \n', b.shape(), '\n')
    
    print('2. Read data to a truncated 2*3 array')
    c = BinaryReader('test.bin')
    c.sort(ncols=3, trunc=2)
    print('data: \n', c.data)
    print('shape: \n', c.shape(), '\n')
    
    print('3. Read data to a format-customized 2*4 array')
    d = BinaryReader('test.bin')
    d.customize('dddd')
    d.sort()
    print('data: \n', d.data)
    print('shape: \n', d.shape(), '\n')