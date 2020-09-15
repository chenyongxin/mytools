# -*- coding: utf-8 -*-
"""
Write Paraview file in XML and binary. It supports rectilinear grid (.vtr), 
structured grid (.vts) and unstructured grid (.vtu). To reduce data size, all
the output data is in single-precision. This is a simple version of Paraview 
binary output script and only point data is supported.

@author: CHEN Yongxin
"""

import numpy as np
from struct import pack

__all__ = ["vtr", "vts", "vtu"]

# String encoder
def encode(string): 
    return str.encode(string)

def vtr(name, x, y, z, **kwargs):
    """
    Write rectilinear grid .vtr file in binary.

    Parameters
    ----------
    name: str
        File name (without '.vtr' extension).
    x, y, z: array-like, float, (N,)
        x, y, z axis 1D grid point.
    **kwargs: dict, optional
        Output fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz)) or 
        2D. e.g. Value = np.zeros((ndim, nx*ny*nz))
    """
    nx, ny, nz = x.size, y.size, z.size          # dimensions
    off = 0                                      # offset
    ise, jse, kse = [1, nx], [1, ny], [1, nz]    # start and ending indices

    with open(name+".vtr", 'wb') as fh:
        fh.write(encode( '<VTKFile type="RectilinearGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode(f'<RectilinearGrid WholeExtent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode(f'<Piece Extent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode( '<Coordinates>\n'))
        fh.write(encode(f'<DataArray type="Float32" Name="x" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nx*4 + 4
        fh.write(encode(f'<DataArray type="Float32" Name="y" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += ny*4 + 4
        fh.write(encode(f'<DataArray type="Float32" Name="z" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nz*4 + 4
        fh.write(encode( '</Coordinates>\n'))
        
        # additional info for fields if kwargs is present
        if len(kwargs) > 0:
            fh.write(encode('<PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode('<DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'
                                 .format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('</PointData>\n'))

        fh.write(encode('</Piece>\n'))
        fh.write(encode('</RectilinearGrid>\n'))
        fh.write(encode('<AppendedData encoding="raw">\n'))
        fh.write(encode('_'))
        fh.write(pack("i",   4*nx))
        fh.write(pack("f"*nx,  *x))
        fh.write(pack("i",   4*ny))
        fh.write(pack("f"*ny,  *y))
        fh.write(pack("i",   4*nz))
        fh.write(pack("f"*nz,  *z))

        # write fields if present
        if len(kwargs) > 0:
            for value in kwargs.values():
                fh.write(pack("i", 4*value.size))
                fh.write(pack("f"*value.size, *(value.flatten(order='F'))))
        
        fh.write(encode('\n'))
        fh.write(encode('</AppendedData>\n'))
        fh.write(encode('</VTKFile>\n'))
        
def vts(name, x, y, z, **kwargs):
    """
    Write structured grid .vts file in binary.

    Parameters
    ----------
    name: str
        File name (without '.vts' extension).
    x,y,z: array-like, float, (nx,ny,nz)
        x,y,z grid point array.
    **kwargs: dict, optional
        Fields dictionary object.
        Key: field's name.
        Value: numpy array, 4D. e.g. Value = np.zeros((ndim, nx, ny, nz)) or 
        2D. e.g. Value = np.zeros((ndim, nx*ny*nz))
    """
    nx, ny, nz = np.shape(x)
    ise, jse, kse = [1, nx], [1, ny], [1, nz]
    
    with open(name+".vts", 'wb') as fh:
        fh.write(encode( '<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode(f'<StructuredGrid WholeExtent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode(f'<Piece Extent="{ise[0]} {ise[1]} {jse[0]} {jse[1]} {kse[0]} {kse[1]}">\n'))
        fh.write(encode( '<Points>\n'))
        fh.write(encode( '<DataArray type="Float32" Name="Points" format="appended" offset="0" NumberOfComponents="3"/>\n'))
        fh.write(encode( '</Points>\n'))

        # info for fields
        if len(kwargs) > 0:
            off = nx*ny*nz*3*4 + 4            # reserved for grid
            fh.write(encode('<PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode('<DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'
                                 .format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('</PointData>\n'))

        fh.write(encode('</Piece>\n'))
        fh.write(encode('</StructuredGrid>\n'))
        fh.write(encode('<AppendedData encoding="raw">\n'))
        fh.write(encode('_'))
        fh.write(pack("i", 4*nx*ny*nz*3))
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    fh.write(pack("f", x[i,j,k]))
                    fh.write(pack("f", y[i,j,k]))
                    fh.write(pack("f", z[i,j,k]))
        
        # fields
        if len(kwargs) > 0:
            for value in kwargs.values():
                fh.write(pack("i", 4*value.size))
                fh.write(pack("f"*value.size, *(value.flatten(order='F'))))

        fh.write(encode('\n'))
        fh.write(encode('</AppendedData>\n'))
        fh.write(encode('</VTKFile>\n'))

def vtu(name, xyz, cells, cellTypes, **kwargs):
    """
    Write unstrcutred grid .vtu file in binary.
    
    Parameters
    ----------
    name: string
        File name (without '.vtu' extension).
    xyz: numpy array, 2D: n*3
        Vertex point coordinates.
        [[x0,      y0,      z0     ],
         ...
         [x_{n-1}, y_{n-1}, z_{n-1}]].
    cells: numpy array, integer
        Defines the connectivity.
        2D array with dimension n*m, where n is the number of cells and m is
        the maximum number of connection of points among all the cells.
    cellTypes: number array, 1D, integer
        Defines cell type of each cell.
    **kwargs: dict, optional
        Vector or scalar field.
        Key: field's name.
        Value: numpy array, 2D. The field in Value should be arranged as 
        a[NumberOfComponents, n].
    """
    nPoints = xyz.shape[0]
    nCells  = cells.shape[0]
    off = 0

    # write file title
    with open(name+".vtu", 'wb') as fh:
        fh.write(encode( '<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n'))
        fh.write(encode( '<UnstructuredGrid>\n'))
        fh.write(encode( '<Piece NumberOfPoints="{}" NumberOfCells="{}">\n'.format(nPoints, nCells)))
        fh.write(encode( '<Points>\n'))
        fh.write(encode( '<DataArray type="Float32" Name="Points" format="appended" offset="0" NumberOfComponents="3"/>\n'))
        fh.write(encode( '</Points>\n'))
        fh.write(encode( '<Cells>\n'))
        off += nPoints*3*4 + 4
        fh.write(encode(f'<DataArray type="Int32" Name="connectivity" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += np.sum(cells[:,0])*4 + 4
        fh.write(encode(f'<DataArray type="Int32" Name="offsets" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nCells*4 + 4
        fh.write(encode(f'<DataArray type="Int32" Name="types" format="appended" offset="{off}" NumberOfComponents="1"/>\n'))
        off += nCells*4 + 4
        fh.write(encode( '</Cells>\n'))

        # info for fields
        if len(kwargs) > 0:
            fh.write(encode('<PointData>\n'))
            for key, value in kwargs.items():
                ndim = value.shape[0]
                fh.write(encode('<DataArray type="Float32" Name="{}" format="appended" offset="{}" NumberOfComponents="{}"/>\n'.
                                format(key, off, ndim)))
                off += value.size*4 + 4
            fh.write(encode('</PointData>\n'))

        fh.write(encode('</Piece>\n'))
        fh.write(encode('</UnstructuredGrid>\n'))
        fh.write(encode('<AppendedData encoding="raw">\n'))
        fh.write(encode('_'))

        # points
        fh.write(pack("i", 4*nPoints*3))
        for i in range(nPoints):
            fh.write(pack("f"*3, *xyz[i,:]))

        # connectivity
        fh.write(pack("i", 4*np.sum(cells[:,0])))
        for i in range(nCells):
            for j in range(cells[i,0]):
                fh.write(pack("i", cells[i,j+1]))

        # offsets
        fh.write(pack("i", 4*nCells))
        offsets = np.cumsum(cells[:,0])
        for i in range(nCells):
            fh.write(pack("i", offsets[i]))

        # types
        fh.write(pack("i", 4*nCells))
        for i in range(nCells):
            fh.write(pack("i", cellTypes[i]))

        # fields
        if len(kwargs) > 0:
            for value in kwargs.values():
                fh.write(pack("i", 4*value.size))
                fh.write(pack("f"*value.size, *(value.flatten(order='F'))))
                
        fh.write(encode('\n'))
        fh.write(encode('</AppendedData>\n'))
        fh.write(encode('</VTKFile>\n'))



if __name__ == '__main__':
    print("Test paraview binary output. \n")
    
    print("1. 3D rectilinear grid.")
    nx, ny, nz = 101, 51, 61
    x = np.linspace(0, nx-1, nx)
    y = np.linspace(0, ny-1, ny)
    z = np.linspace(0, nz-1, nz)
    p = np.zeros((1, nx, ny, nz))
    v = np.zeros((3, nx, ny, nz))
    for j in range(p.shape[2]):
        p[:,:,j,:] = j
    for i in range(v.shape[1]):
        v[0,i,:,:] = i
    for j in range(v.shape[2]):
        v[1,:,j,:] = j
    for k in range(v.shape[3]):
        v[2,:,:,k] = k
    fields = {"Pressure":p, "Velocity":v}
    vtr("rectilinear", x, y, z, **fields)
    print("Saved in rectilinear.vtr \n")
    
    print("2. 3D structured grid.")
    nx, ny =121, 61
    R1, R2 = 5., 10.            
    x = np.zeros((nx, ny))      
    y = np.zeros((nx, ny))
    dr = (R2-R1)/(ny-1)
    dtheta = np.pi/(nx-1)
    for j in range(ny):
        r = R1 + dr*j
        for i in range(nx):
            x[i,j] = r*np.cos(np.pi-i*dtheta)
            y[i,j] = r*np.sin(np.pi-i*dtheta)
    
    SliceShape = x.shape
    nz =  20
    dz = .25
    
    # convert 2D to 3D: extrude a slice in 3rd direction
    x = np.stack([x for _ in range(nz)], axis=-1)
    y = np.stack([y for _ in range(nz)], axis=-1)
    z = np.stack([np.zeros(SliceShape)+i*dz for i in range(nz)], axis=-1)
    
    # make scalar field p, 2-component field, 3-component field
    p  = np.zeros((1,)+x.shape)
    v2 = np.zeros((2,)+x.shape)
    v3 = np.zeros((3,)+x.shape)
    for j in range(p.shape[2]):
        p[:,:,j,:] = j
    for i in range(v3.shape[1]):
        v3[0,i,:,:] = i
        v2[0,i,:,:] = i
    for j in range(v3.shape[2]):
        v3[1,:,j,:] = j
        v2[1,:,j,:] = j
    for k in range(v3.shape[3]):
        v3[2,:,:,k] = k 
    fields = {"Pressure":p, "V2":v2, "V3":v3}
    vts("structured", x, y, z, **fields)
    print("Saved in structured.vts \n")
    
    
    print("3. 3D unstructured grid.")
    
    # make grid: convert structured grid to unstructured grid
    xyz = np.zeros((x.size, 3))
    xflat = x.flatten(order='F')
    yflat = y.flatten(order='F')
    zflat = z.flatten(order='F')
    xyz[:,0] = xflat
    xyz[:,1] = yflat
    xyz[:,2] = zflat
    
    # make cell connectivity array, 8-point cell
    cells = np.zeros(((nx-1)*(ny-1)*(nz-1), 1+8), dtype=int)
    cells[:,0] = 8
    for k in range(nz-1):
        for j in range(ny-1):
            for i in range(nx-1):
                idx = i+j*(nx-1)+k*(nx-1)*(ny-1)
                cells[idx,1] = i+j*nx+k*nx*ny
                cells[idx,2] = i+j*nx+k*nx*ny + 1
                cells[idx,3] = i+j*nx+k*nx*ny + nx
                cells[idx,4] = i+j*nx+k*nx*ny + nx + 1
                cells[idx,5] = i+j*nx+k*nx*ny + nx*ny
                cells[idx,6] = i+j*nx+k*nx*ny + nx*ny + 1
                cells[idx,7] = i+j*nx+k*nx*ny + nx*ny + nx
                cells[idx,8] = i+j*nx+k*nx*ny + nx*ny + nx + 1
                      
    cellTypes = np.zeros((nx-1)*(ny-1)*(nz-1), dtype=int)
    cellTypes[:] = 11               # VTK_VOXEL (=11)
    
    p  = p.reshape((  p.shape[0],   p.size//p.shape[0]), order='F')
    v2 = v2.reshape((v2.shape[0], v2.size//v2.shape[0]), order='F')
    v3 = v3.reshape((v3.shape[0], v3.size//v3.shape[0]), order='F')
    
    fields = {"Pressure":p, "V2":v2, "V3":v3}
    vtu("unstructured", xyz, cells, cellTypes, **fields)
    print("Saved in unstructured.vtu \n")