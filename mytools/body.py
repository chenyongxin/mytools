#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read geometry and the time history of fields on the body. 
The result is to be further processed.

@author: CHEN Yongxin
"""

import numpy as np
from mytools.paraview import vts

def read_geom(file):
    """
    Read geometry file.
    
    geom file looks like
    -----
    nz
    nxy
    x1 y1
    x2 y2
    ...
    xn yn
    -----
    This is for reading spanwise extruding body.
    
    Parameters
    ----------
    file: string
        File name for geometry.
    
    Returns
    -------
    ctp: array-like
        Center point coordinate.
    n: int
        Number of points in a ring.    
    nz: int
        Number of points in spanwise directions.
    """
    with open(file, 'r') as fh:
        nz = int(fh.readline().strip('\n').strip())
        n = int(fh.readline().strip('\n').strip())
        ctp = np.zeros((n, 2))
        for i in range(n):
            ctp[i, :] = np.array([float(i) for i in fh.readline().strip('\n').
                              strip().split()])
    return ctp, n, nz


def visu_extrude(file, ctp, nz, lzs, lze, f):
    """
    Visualise extruding body along spanwise direction with structured grid in 
    paraview. 
    
    Parameters
    ----------
    file: string
        File name.
    ctp: array-like 
        Centre point. 2-D data with n-by-nz dimensions. 
    nz: int
        Number in z direction.
    lzs, lze: float
        lz start and end coordinate.
    f: dict
        FieldName:Array pair. Dimensions of `value` are arranged as a scalar P[1, n, nz] and 
        a vector U[3, n, nz].
    """
    n = ctp.shape[0]
    x = np.zeros((n+1, nz, 1))
    y = np.zeros((n+1, nz, 1))
    z = np.zeros((n+1, nz, 1))
    dz = (lze-lzs)/(nz-1)
    for j in range(nz): 
        for i in range(n):
            x[i, j, 0] = ctp[i, 0]
            y[i, j, 0] = ctp[i, 1]
            z[i, j, 0] = lzs + j*dz
        x[n, j, 0] = x[0, j, 0]
        y[n, j, 0] = y[0, j, 0]
        z[n, j, 0] = z[0, j, 0]
        
    fields = {}
    for key, value in f.items():
        shape = value.shape
        temp  = np.zeros((shape[0], shape[1]+1, shape[2]))  # temporary
        temp[:, :-1, :] = value.copy()
        for d in range(shape[0]):                           # loop over dimension  
            temp[d, -1, :] = temp[d, 0, :]                  # fill in the cut 
        fields.update({key:temp})
    vts(file, x, y, z, **fields)
    
