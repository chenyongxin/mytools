# -*- coding: utf-8 -*-
"""
Customized HDF5 functions.

@author: CHEN Yongxin
"""

import numpy as np
import h5py as h5
import matplotlib.pyplot as plt


class MyHDF5(object):
    """
    Customized HDF5 object. By default, all datasets are stored in the root 
    location as /dataset1, /dataset2, ... For the sake of simplification, it is
    recommended not to use groups. 
    """
    
    def __init__(self, name=None, mode='a'):
        """
        Initialize a HDF5 file object if file name is provided.
        """
        self.fh      = None                  # file handle
        self.dataset = []
        self.group   = []
        if name is not None:
            self.file(name=name, mode=mode)
        
    def file(self, name, mode='a'):
        """
        Open a file with default mode 'a' (append).
        
        Parameters
        ----------
        name: str
            Name of file.
        mode: char, optional
            Open file mode.
        """
        self.fh = h5.File(name=name, mode=mode)
        self.info()
        
    def info(self):
        """Update dataset and group info."""
        self.dataset, self.group = [], []
        def classify(name, obj):
            # Get group and dataset info.
            if isinstance(obj, h5.Dataset): self.dataset.append(name)
            if isinstance(obj, h5.Group):   self.group.append(name)
        self.fh.visititems(classify)
                
    def concatenate(self, dataset):
        """
        Concatenate data to an existing dataset by deleting old one and adding
        a new one with concatenating the new dataset. 
        
        Parameters
        ----------
        dataset: dict
            Dataset to be appended. 
            {'An Existing dataset name':array to be appended}.
        """
        assert(isinstance(dataset, dict))
        assert(len(dataset) == 1)
        datasetName = list(dataset.keys())[0]
        originalDataset = self.get(datasetName)
        newDataset = list(dataset.values())[0]
        del self.fh[datasetName]
        self.fh.create_dataset(datasetName, data=
                               np.concatenate((originalDataset, newDataset)))
        
    def get(self, dataName):
        """
        Get the value of dataset and return a numpy array.
        
        Parameters
        ----------
        dataName: str
            Name of dataset.
        
        Returns
        -------
        a: array
            Value of the dataset.
        """
        assert(dataName in self.dataset)
        return np.array(self.fh[dataName])
    
    def append(self, dataset):
        """
        Adding a new dataset.
        
        Parameter
        ---------
        dataset: dict
            Dataset to be appened. 
            {'New dataset name':array}
        """
        assert(isinstance(dataset, dict))
        assert(len(dataset) == 1)
        self.fh.create_dataset(name = list(dataset.keys())[0], 
                               data = list(dataset.values())[0])
        self.info()            # update dataset/group info
        
    def xyplot(self, dataName, plot=plt.plot):
        """
        Make a quick x-y plot with a specified spreadsheet data.
        
        Parameters
        ----------
        dataName: str
            Name of dataset.
        plot: function
            Plotting function.
        """
        data = self.get(dataName)
        assert(data.ndim == 2)
        plt.figure()
        for i in range(1, data.shape[1]):
            plot(data[:,0], data[:,i])
        plt.show()
        
    def image(self, dataName):
        """
        Visualize the image.
        
        Parameter
        ---------
        dataName: str
            Name of dataset.
        """
        data = self.get(dataName)
        assert(data.ndim in (2,3))
        plt.figure()
        plt.imshow(data)
        
    def close(self):        
        """Close the HDF5 file."""        
        self.fh.close()
        

        
if __name__ == "__main__":
    import os
    name = 'test.h5'
    data = np.zeros((100,3))
    data[:,0] = np.linspace(0, 2*np.pi, 100)
    data[:,1] = np.sin(data[:,0])
    data[:,2] = np.cos(data[:,0])
    mode = 'a'
    if os.path.isfile(name): 
        mode = 'w'
    a = MyHDF5(name, mode=mode)
    a.append({'a':data})
    a.append({'b':data+5})
    a.append({'c/data':data+10})
    a.concatenate({'b':a.get('a')})
    a.xyplot('a')
    a.xyplot('b', plt.scatter)
    a.close()