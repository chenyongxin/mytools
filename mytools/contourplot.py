#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contour plot with the immersed boundary method.

@author: CHEN Yongxin
"""

import numpy as np
import matplotlib.pyplot as plt

def plotter(x, y, f, xlim=None, ylim=None, cmap=plt.cm.bwr, cmap_range=[-5,5], \
            intervals=100, extend=None):
    """
    Contour plot.
    Parameters
    ----------
    x, y: array like
        1D array for coordinate in X and Y.
    f: array like
        2D field.
    xlim, ylim: array like, optional
        2-entity list to define the limit of contour.
    cmap: object, optional
        Colormap. 
    cmap_range: array like, optional
        2-entity list.
    intervals: int, optional
        Number of intervals for colorbar. Recommand an even number.
    extend: {'min', 'max', 'both'}, optional
        If to extend either side.
    """
    
    xmask = np.ones_like(x, dtype=bool)
    ymask = np.ones_like(y, dtype=bool)
    
    if xlim is not None:
        xmask = (x>xlim[0]) & (x<xlim[1])
    if ylim is not None:
        ymask = (y>ylim[0]) & (y<ylim[1])

    X, Y = np.meshgrid(x[xmask], y[ymask], indexing='ij')

    # mask 2D array
    domain = f.copy()
    domain = domain[xmask, :]
    domain = domain[:, ymask]

    # plot contour
    lv = np.linspace(cmap_range[0], cmap_range[1], intervals)
    cf = plt.contourf(X, Y, domain, levels=lv, cmap=cmap)
    if extend is not None:
        plt.contourf(X, Y, domain, levels=lv, cmap=cmap, extend=extend)
    return cf


"""
### Example implementation code
x = np.load('x.npy')
y = np.load('y.npy')
f = np.load('vort.npy')
d = np.load('dist.npy')
plt.figure(figsize=(6,5))
cf = plotter(x, y, f, xlim=[0, 10], ylim=[-5,5], extend='both')
df = plotter(x, y, d, xlim=[0, 10], ylim=[-5,5], cmap=plt.cm.gray, cmap_range=[-10,0], intervals=2)
plt.axis('equal')
"""