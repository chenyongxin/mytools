# -*- coding: utf-8 -*-
"""
Customize matplotlib settings.

@author: CHEN Yongxin
"""

import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager as fm

__all__ = ["MyMPL", "mypreset"]

class MyMPL(object):
    """
    Customized matplotlib interface. It includes basic functions to set up and
    get properies. It is recommended to use it as a container/template to all
    figures and/or axes once things have been set up. This object is designed 
    for the figure customization to meet the need of publication quality. Only 
    the essential parts in the plot are covered, such as font, axis, and label.
    The settings which are not covered should be set up manually in the 
    plotting scripts. 
    
    Calling order/checklist: 
         (1) Set font properties. Load a preset if we have.
         (2) Set figure size.
         (3) New a figure.
         (4) Make subplots (optional).
         (5) Plot.
         (6) Set invisible spines (optional). 
         (7) Set labels (optional).
         (8) Set legends (optional).
         (9) Set ticks (optional).
        (10) Save figure.
    
    Remember: Write 1 Python script with 1 MyMPL object to plot 1 figure.
    """
    
    def __init__(self, preset=None):
        self.family   = 'sans-serif'    # font.family
        self.fname    = None            # font path
        self.usetex   = False           # use latex font
        self.mathtext = 'dejavusans'    # mathtext.fontset
        self.fontsize = 10              # font.size
        self.tick_dir = 'out'           # tick direction
        self.frameon  = True            # legend frame
        self.nospines = {}              # invisible spines, set
        self.fig      = None            # Figure object
        self.ax       = None            # Axes object, current axes
        self.axes     = None            # multiple axes for subplots
        self.prop     = None            # font properties
        self.figsize  = (6, 4)          # tuple with size 2 in inches
        self.figratio = 0.66667         # figure height width ratio
        self.width    = 0.51313         # ratio used in width\linewidth (LaTeX)
        if preset is not None:
            self.load_preset(preset)
        
    # Figure size
    def set_figsize(self, figsize):
        """Set figure size with a tuple of 2 in inch."""
        self.figsize = figsize
        
    def set_figure_size(self, w=0.7, rb=0.95, wp=210, ratio=0.6):
        """Set figure size by specifying parameters.
        
        Parameters
        ----------
        w: float
            Ratio of figure width to text width. For example, w=0.7 is 
            equivalent to width=0.7\textwidth in LaTeX.
        rb: float
            Ratio of text width to page width. E.g. rb=0.95 for the ratio of 
            text to the page width is 0.95.
        wp: int, float
            Width of page in millimeter. Default 210 is for a A4 paper.
        ratio: float
            Ratio of height to wdith. Default 0.6.
        """
        width = get_figure_width(w, rb, wp)
        self.figratio = ratio
        self.width = w
        self.figsize = (width, get_figure_height(width, ratio))
    
    def get_figure_size_info(self):
        """Print figure size info."""
        print("Figure width to text width ratio:", self.width)
        print("Figure heigh to width ratio:", self.figratio)
        print("Figure size in inch:", self.figsize)
    
    # Figure
    def figure(self):
        """Create a new figure object."""
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = plt.gca()
        
    def set_fig(self, fig):
        """
        Set an active figure. This enables the current settings to be applied 
        to another figure as a template. However, this is not encouraged.
        """
        self.fig = fig
        
    def get_fig(self):
        """Return current Figure object."""
        return self.fig
        
    def subplots(self, nrows=1, ncols=1, sharex=False, sharey=False):
        """Add a set of subplots to this figure."""
        self.axes = self.fig.subplots(nrows=nrows, ncols=ncols, 
                                      sharex=sharex, sharey=sharey)
        
    def savefig(self, name, suf='pdf', dpi=300):
        """
        Save figure with info.
        Save XY plots with pdf format, and contour with png. Default pdf.
        """
        self.fig.savefig(name+"_wa{}.".format(self.width)+suf)

    # Font
    def set_file(self, file=None):
        """Set font file path."""
        self.fname = file
        
    def load_preset(self, preset):
        """Load a preset dict."""
        self.family   = preset['family']
        self.fname    = preset['fname']
        self.usetex   = preset['usetex']
        self.mathtext = preset['mathtext']
        self.fontsize = preset['fontsize']
        self.tick_dir = preset['tick_dir']
        self.frameon  = preset['frameon']
        self.nospines = preset['nospines']
        
        mpl.rc('text', usetex=self.usetex)
        rcParams['mathtext.fontset'] = self.mathtext
        
        self.set_prop()
      
    def set_prop(self, prop=None):
        """Set font properties."""
        rcParams['mathtext.fontset'] = self.mathtext
        mpl.rc('text', usetex=self.usetex)
        
        if prop is not None:
            assert(isinstance(prop, mpl.font_manager.FontProperties))
            self.prop = prop
            return
        else:
            self.prop = fm.FontProperties(family = self.family, 
                                          size   = self.fontsize,
                                          fname  = self.fname)

    # Axes
    def set_ax(self, ax):
        """Set an active axes."""
        plt.sca(ax)     # activate plot axes
        self.ax = ax    # change object
    
    def get_ax(self):
        """Get current axes."""
        return self.ax
    
    def get_axes(self):
        """Get axes for subplots."""
        return self.axes
    
    # Labels
    def xlabel(self, xlabel, **kwargs):
        """Set the label for the x-axis."""
        plt.xlabel(xlabel, fontProperties=self.prop, **kwargs)
    
    def ylabel(self, ylabel, **kwargs):
        """Set the label for the y-axis."""
        plt.ylabel(ylabel, fontProperties=self.prop, **kwargs)
    
    def zlabel(self, zlabel, **kwargs):
        """Set the label for the z-axis."""
        plt.zlabel(zlabel, fontProperties=self.prop, **kwargs)
    
    # Ticks
    def set_tick_dir(self, direction='out'):
        """Set tick direction in one of {in, out, inout}."""
        self.tick_dir = direction
        
    def set_tick_params(self, **kwargs):
        """Set tick parameters to current active axes."""
        self.ax.tick_params(direction=self.tick_dir, **kwargs)
        
    def set_xticks_fontproperties(self):
        """Set font properties for x-ticks of current axes."""
        for label in self.ax.get_xticklabels(): 
            label.set_fontproperties(self.prop)
    
    def set_yticks_fontproperties(self):
        """Set font properties for y-ticks of current axes."""
        for label in self.ax.get_yticklabels(): 
            label.set_fontproperties(self.prop)
            
    def set_zticks_fontproperties(self):
        """Set font properties for z-ticks of current axes."""
        for label in self.ax.get_zticklabels(): 
            label.set_fontproperties(self.prop)
        
    def set_xyticks(self, **kwargs):
        """Set font properties for x and y ticks of current axes in one go. """
        self.set_tick_params(**kwargs)
        self.set_xticks_fontproperties()
        self.set_yticks_fontproperties()
    
    # Title
    def title(self, text, **kwargs):
        """Set title for the current axes."""
        plt.title(text, fontProperties=self.prop, **kwargs)
            
    # Spines
    def diable_spines(self):
        for spine in self.nospines:
            self.ax.spines[spine].set_visible(False)
            
    # Legends
    def legend(self, fancybox=True, *args, **kwargs):
        self.ax.legend(frameon=self.frameon, fancybox=fancybox, prop=self.prop,
                       *args, **kwargs)
    

# Set figure size
def mm2inch(mm):
    """Convert mm to inch."""
    return 0.0393701 * mm

def get_figure_width(w=0.7, rb=0.9, wp=210):
    """Compute and return figure width in inch."""
    return mm2inch(w*rb*wp)
    
def get_figure_height(width, ratio=0.6):
    """Compute and return figure height with a ratio."""
    return width*ratio

def get_figure_size(w=0.7, rb=1.0, wp=210, ratio=0.6):
    """Compute and return figure size in tuple."""
    width = get_figure_width(w, rb, wp)
    return width, get_figure_height(width, ratio)

# Preset based on my taste. I often install additional font in mpl-data folder.
# This is similar with Matlab plot.
mypreset = {
    'family'   : None,
    'fname'    : os.path.join(rcParams["datapath"], "fonts/ttf/Helvetica.ttf"),
    'usetex'   : False,
    'mathtext' : 'cm',
    'fontsize' : 10,
    'tick_dir' : 'in',
    'frameon'  : False,
    'nospines' : {},           # {"top", "bottom", "left", "right"}
    'tick_params': {"bottom":True, "left":True, "top":True, "right":True} 
    }


if __name__ == '__main__':
    import numpy as np
    n = 100
    t = np.linspace(0, np.pi*2, n)
    sin = np.sin(t)
    cos = np.cos(t)
    #mypreset['fname'] = None                # disable the rendering font
    a = MyMPL(mypreset)
    #a = MyMPL()                             # use the default one
    a.set_prop()                             # this is needed
    a.set_figure_size()
    a.figure()
    plt.plot(t, sin, label="sin")
    plt.plot(t, cos, label="cos")
    a.xlabel(r"Time $t$")
    a.ylabel(r"sin($t$), cos($t$)")
    #plt.margins(x=0., y=0.)                  # 2 ways to define margin
    #plt.gca().margins(x=0, y=0)
    #a.set_xyticks()                          # with preset
    a.set_xyticks(**mypreset['tick_params'])  # with additional preset
    a.legend()
    a.get_ax().yaxis.set_major_locator(plt.MaxNLocator(3))
    plt.xticks([0, np.pi, np.pi*2], ["0", r"$\pi$", r"2$\pi$"])
    a.savefig("test")