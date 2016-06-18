import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
nullfmt = NullFormatter()         # no labels

def plot_histograms(dataset,matchList):
    print(matchList)
    if not matchList:
        matchList = dataset['matchID'].unique()
    for match in matchList :
        print(match)
        matchdata = dataset[dataset['matchID'] == match]
        
        countryAlpha = matchdata['countryAlpha'].iloc[0]
        countryBeta = matchdata['countryBeta'].iloc[0]
        
        scoreAlpha = matchdata['fscoreAlpha'].iloc[0]
        scoreBeta = matchdata['fscoreBeta'].iloc[0]
        
        
        prono_x = matchdata['pronoAlpha']
        prono_y = matchdata['pronoBeta']
        
        edges = [0,1,2,3,4,5,6]
        hist2d = np.histogram2d(prono_x, prono_y,bins = (edges,edges))
        
        print(countryAlpha + ' vs ' + countryBeta)
        print(str(scoreAlpha) + ' - ' + str(scoreBeta))
        
        # definitions for the axes
        left, width = 0.1, 0.62
        bottom, height = 0.1, 0.62
        bottom_h = left_h = left + width + 0.02
        
        
        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]
        # start with a rectangular Figure
        plt.figure(match,figsize=(5, 5))
        axScatter = plt.axes(rect_scatter)
        axHistx = plt.axes(rect_histx)
        axHisty = plt.axes(rect_histy)
        
        # no labels
        axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)
        
        # the scatter plot:
        axScatter.imshow(np.transpose(hist2d[0]),interpolation = 'nearest')
        
        # now determine nice limits by hand:
        binwidth = 1
        lim = 5.5
        
        axScatter.set_xlim((-0.5, lim))
        axScatter.set_ylim((-0.5, lim))
        
        bins = np.arange(-lim, lim + binwidth, binwidth)
        axHistx.hist(prono_x, bins=bins)
        axHisty.hist(prono_y, bins=bins, orientation='horizontal')
        axHistx.set_xlim(axScatter.get_xlim())
        axHisty.set_ylim(axScatter.get_ylim())
        axHisty.set_xticks([125,250])
        axHistx.set_yticks([125,250])
        
        axHistx.set_title(countryAlpha + ' - ' + str(scoreAlpha))
        axHisty.set_title(countryBeta + '\n' + str(scoreBeta))
        print(hist2d[0])
    plt.show()