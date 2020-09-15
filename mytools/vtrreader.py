#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.vtr reader.

@author: CHEN Yongxin
"""

import vtk
import numpy as np

def reader(file, point_in=None, cell_in=None, display=True):
    """
    Paraview .vtr file reader.
    
    Parameters
    ----------
    file: string
        Name of .vtr file.
    point_in: list
        List of string to specify which point data will be output.
    cell_in: list
        List of string to specify which cell data will be output.
    display: bool, optional   
        Display the names of fields on screen.   
    
    Returns
    -------
    grid: dict
        X, Y and Z vertex grid coordinate.
    point_out: dict
        Output point data in a dict.
    cell_out: dict
        Output cell data in a dict.
    """
    reader = vtk.vtkXMLRectilinearGridReader()
    reader.SetFileName(file)
    reader.Update()
    data = reader.GetOutput()
    
    # Get grid
    x = np.array(data.GetXCoordinates())
    y = np.array(data.GetYCoordinates())
    z = np.array(data.GetZCoordinates())
    
    # Get data pointer
    point_data = data.GetPointData()
    cell_data = data.GetCellData()
    
    # Build output dicts
    point, cell = {}, {}
    for i in range(point_data.GetNumberOfArrays()):
        name = point_data.GetArrayName(i)
        array = np.array(point_data.GetAbstractArray(i))
        if array.ndim > 1:    # e.g velocity: (nx*ny*nz, 3)
            array = array.transpose()
        else:
            array = np.reshape(array, (1, array.size))
        point.update({name: array})
    
    for i in range(cell_data.GetNumberOfArrays()):
        name = cell_data.GetArrayName(i)
        array = np.array(cell_data.GetAbstractArray(i))
        if array.ndim > 1:
            array = array.transpose()
        else:
            array = np.reshape(array, (1, array.size))
        cell.update({name: array})
    
    # display names to help for debugging
    if display:
        print('Displaying fields names.')
        print('- Point data: ', end=' '); print()
        for i in point.keys():
            print(i, end='| ')
        print()
        print('- Cell data: ', end=' ')
        for i in cell.keys():
            print(i, end='| ')
        print()
            
    # assemble output data
    xyz = {"x":x, "y":y, "z":z}
    point_out, cell_out = {}, {}
    if point_in is not None:
        for name in point_in:
            point_out.update({name: point[name]})
    if cell_in is not None:
        for name in cell_in:
            cell_out.update({name: cell[name]})
    
    return xyz, point_out, cell_out