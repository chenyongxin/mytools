# -*- coding: utf-8 -*-
"""
1D time series manipulation.

@author: CHEN Yongxin
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import  welch

class Series(object):
    """
    Time series class deals with a 1D time series data. Both uniform and 
    non-uniform sampled data are supported. Input: t (time) and ft (values).
    """
    
    def __init__(self, t, ft):
        """Initialize a time series.
        
        Parameters
        ----------
        t: numpy array
            1D array of time.
        ft: numpy array
            1D array of values.
        """
        self.t  = t                      # time 
        self.ft = ft                     # values

        self.N = len(t)                  # total sample number
        self.fun = interp1d(t, ft)       # function f(t)
        self.ut = np.linspace(t.min(), t.max(), self.N)  # uniform time 
        self.uft = self.fun(self.ut)     # series from uniform time
        self.dt = self.ut[1]-self.ut[0]  # uniform time step
        
        self.f = None                    # frequency
        self.F = None                    # frequency domain series
        self.hf = None                   # half frequency
        self.P1 = None                   # single sided spectrum
        
        self.psd_f = None                # PSD frequency
        self.psd_pxx = None              # power spectrum (density) 
        
        self.calc_spectrum()             # calculate single-sided spectrum
        self.calc_psd()                  # calculate psd
        
    def calc_spectrum(self):
        """Calculate single-sided spectrum."""
        self.F = np.fft.fft(self.uft)
        P2 = abs(self.F)/self.N*2      # double it as only present half freq
        self.P1 = P2[0:int(self.N/2)+1]
        Fs = 1./self.dt                # minimum frequency
        self.f = Fs*np.linspace(0., 1., self.N)
        self.hf = Fs*np.linspace(0, 1./2., int(self.N/2)+1)
        
    def plot_spectrum(self):
        """Plot single-sided spectrum."""
        plt.figure()
        plt.plot(self.hf, self.P1)
        plt.xlabel('Frequency')
        plt.show()
        
    def get_spectrum(self):
        """Get single-sided spectrum and return (freq, value)."""
        return self.hf, self.P1
    
    def calc_psd(self, **kwargs):
        """Calculate power spectrum density by using Welch's method."""
        self.psd_f, self.psd_pxx = welch(self.uft, fs=1./self.dt, **kwargs)
    
    def plot_psd(self):
        """Plot power spectrum density."""
        plt.figure()
        plt.plot(self.psd_f, self.psd_pxx)
        plt.xlabel('Frequency')
    
    def get_psd(self):
        """Get power spectrum density output (freq, pxx)."""
        return self.psd_f, self.psd_pxx
    
    
if __name__=='__main__':
    Fs = 1000                        # sampling frequency
    T  = 1/Fs                        # Sampling peroid, Delta t
    L  = 500                         # Length of singal: how many samples
    t = np.linspace(0, (L-1)*T, L)   # time vector
    f1, f2 = 100, 200                # Two principal frequencies
    a1, a2 = 0.7, 1.                 # Two amplitude
    y = a1*np.sin(2*np.pi*f1*t) + a2*np.sin(2*np.pi*f2*t)
    scale = .3
    rand = (np.random.rand(np.size(y)) - 0.5) * scale
    y2 = y + rand
    
    series = Series(t, y2)
    series.plot_spectrum()        