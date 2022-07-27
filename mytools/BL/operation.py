#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boundary Layer simulation module.
Operation collection.

@author: CHEN Yongxin
"""

import numpy as np
from ..asciiio import outputs_lite

def clip_xy_mask(x, y, normal, origin):
    """
    Clip a 3D array and return clipped x and y masks.
    
    Parameters
    ----------
    x, y, z: 1D array 
        Coordinates.
        
    normal: int {-2,-1,1,2}
        Normal plane to discard clipped part.
    
    origin: float
        Original point.
    
    Returns
    -------
    xmask, ymask:
        x and y masks
    """
    assert(normal in (-2, -1, 1, 2))
    xmask, ymask = np.ones_like(x, dtype=bool), np.ones_like(y, dtype=bool)
    
    if abs(normal) == 1:
        if np.sign(normal) > 0:
            xmask = x <= origin
        else:
            xmask = x >= origin
    else:
        if np.sign(normal) > 0:
            ymask = y <= origin
        else:
            ymask = y >= origin            
    return xmask, ymask


def vtk_data_xy_clip(a, x, y, z, normal, origin):
    """
    VTK data clip wrapper.
    Clip data in x and y directions.
    
    Parameters
    ----------
    a: 2D array in a vtr reader format.
        Either scalar (1, nx*ny*nz) or vector fields (3, nx*ny*nz).
    
    x, y, z: 1D array
        Axes.
        
    normal: normal direction 
        One of (-2, -1, 1, 2).
    
    origin: float
        Original point of the clipping plane.
        
    Returns
    -------
    Grid: tuple
        A tuple of 3 axes components.
    
    data: vtk data
    """
    xmask, ymask = clip_xy_mask(x, y, normal, origin)
    nelement = a.shape[0]
    nx, ny, nz = x.size, y.size, z.size
    newa = []
    for i in range(nelement):
        aa = np.reshape(a[i, :], (nx, ny, nz), order='F')
        aa = aa[xmask, :, :][:, ymask, :]
        newa.append(np.reshape(aa, aa.size, order='F'))
    return (x[xmask], y[ymask], z), np.array(newa)

def vtk_point_data_horizontal_phase_average(a, x, y, z, px=1, py=1):
    """
    VTK data phase average in horizontal plane with specified sections.
    
    Parameters
    ----------
    a : VTK data
        
    x : 1D array
        X axis.
    y : 1D array
        Y axis.
    z : 1D array
        Z axis.
    px : int, optional
        Number of parts in x. The default is 1.
    py : int, optional
        Number of parts in y. The default is 1.

    Returns
    -------
    Grid: tuple
        A tuple of 3 axes components.
    
    data: vtk data
    """
    nelement = a.shape[0]
    onx, ony, onz = x.size, y.size, z.size      # original grid size
    xx, yy, zz = x.copy(), y.copy(), z.copy()   # get original grid
    
    # Discard the last one if that is odd number
    nx, ny = onx, ony
    if onx%2 == 0:
        nx = onx -1 
        xx = xx[:nx]

    if ony%2 == 0:
        ny = ony -1
        yy = yy[:ny]
    
    npx, npy = (nx-1)//px, (ny-1)//py          # new number of cells in x and y
    xx,  yy  = x[:npx+1],  y[:npy+1]
    newa = []
    
    for e in range(nelement):
        aa = np.reshape(a[e, :], (onx, ony, onz), order='F') # take each compoonent
        average = np.zeros((npx+1, npy+1, onz))  # averaged data
        
        for i in range(px):
            for j in range(py):
                average += aa[npx*i:npx*(i+1)+1, npy*j:npy*(j+1)+1, :]
        
        average /= (px*py)
        newa.append(np.reshape(average, average.size, order='F'))
    
    return (xx, yy, zz), np.array(newa)

def vtk_cell_data_phase_average(a, x, y, z, npx=1, npy=1):
    pass

def vtk_single_point_data_horizontal_average(a, x, y, z):
    """
    Horizontally average vtk point data along height.

    Parameters
    ----------
    a : TYPE
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    z : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    nx, ny, nz = x.size, y.size, z.size
    reduced = []
    for e in range(a.shape[0]):
        ae = np.reshape(a[e, :], (nx, ny, nz), order='F') # take each compoonent
        p  = np.zeros(nz)
        for k in range(nz):
            p[k] = np.mean(ae[:,:,k])
        reduced.append(p)
    return np.array(reduced)

def vtk_cell_data_horizontal_average(a, x, y, z):
    pass

def vtk_point_data_horizontal_average(point, x, y, z, fname):
    """
    
    Parameters
    ----------
    point : dict
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    z : TYPE
        DESCRIPTION.
    fname : string
        File name.

    Returns
    -------
    None.

    """
    dims  = []             # dimension of each component
    items = []             # table header
    
    for value in point.values():
        dims.append(value.shape[0])
    table = np.zeros((z.size, np.array(dims).sum()+1))
    table[:, 0] = z
    items.append("z")
    
    icol = 1
    for i, (key, value) in enumerate(point.items()):
        data = vtk_single_point_data_horizontal_average(value, x, y, z)
        n = dims[i]
        if n != 1:
            for j in range(n):
                items.append(key+f":{j}")
                table[:, icol] = data[j, :]
                icol += 1
        else:
            items.append(key)
            table[:, icol] = data[0, :]
            icol += 1
            
    outputs_lite(fname, table, items)
        
def vtk_point_data_velgrad(u, x, y, z):
    """
    

    Parameters
    ----------
    u : TYPE
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    z : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    def derivate(du, dx, j):
        dudx = np.copy(du)
        n = dx.size
        if j == 0:
            for i in range(n):
                dudx[i, :, :] /= dx[i]
        if j == 1:
            for i in range(n):
                dudx[:, i, :] /= dx[i]
        if j == 2:
            for i in range(n):
                dudx[:, :, i] /= dx[i]
        return dudx
            
    nx, ny, nz = x.size, y.size, z.size         # original grid size
    xx = (x[:-1]+x[1:])/2                       # cell centered coordinate
    yy = (y[:-1]+y[1:])/2
    zz = (z[:-1]+z[1:])/2
    
    dx = []
    dx.append(x[1:]-x[:-1])
    dx.append(y[1:]-y[:-1])
    dx.append(z[1:]-z[:-1])
    
    """
    dx = x[1:]-x[:-1]
    dy = y[1:]-y[:-1]
    dz = z[1:]-z[:-1]
    """
    
    delta_u = []
    
    """
    du = np.reshape(u[0, :], (nx, ny, nz), order='F')
    dv = np.reshape(u[1, :], (nx, ny, nz), order='F')
    dw = np.reshape(u[2, :], (nx, ny, nz), order='F')
    """
    
    du = np.reshape(u[0, :], (nx, ny, nz), order='F')
    du = (du[1:, :, :] - du[:-1, :, :])
    #du = (du[:, :-1, :-1] + du[:, :-1, 1:] + du[:, 1:, :-1] + du[:, 1:, 1:])/4
    du = du[:, :-1, :-1]
    delta_u.append(du)
    
    dv = np.reshape(u[1, :], (nx, ny, nz), order='F')
    dv = (dv[:, 1:, :] - dv[:, :-1, :])
    #dv = (dv[:-1, :, :-1] + dv[:-1, :, 1:] + dv[1:, :, :-1] + dv[1:, :, 1:])/4
    dv = dv[:-1, :, :-1]
    delta_u.append(dv)
    
    dw = np.reshape(u[2, :], (nx, ny, nz), order='F')
    dw = (dw[:, :, 1:] - dw[:, :, :-1])
    #dw = (dw[:-1, :-1, :] + dw[:-1, 1:, :] + dw[1:, :-1, :] + dw[1:, 1:, :])/4
    dw = dw[:-1, :-1, :]
    delta_u.append(dw)
    
    velgrad = np.zeros((3, 3, nx-1, ny-1, nz-1))
    for i in range(3):
        for j in range(3):
            velgrad[i, j, :, :, :] = derivate(delta_u[i], dx[j], j)
    
    return (xx, yy, zz), velgrad