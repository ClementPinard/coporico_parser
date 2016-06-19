import numpy as np
import matplotlib.pyplot as plt
import operator
from matplotlib.ticker import NullFormatter
import advanced_stats
nullfmt = NullFormatter()         # no labels

def plot_histograms(dataset,matchList):
    print(matchList)
    if not matchList:
        matchList = dataset['matchID'].unique()
    for match in matchList :
        print(match)
        
        prono_x,prono_y,hist2d = advanced_stats.get_bet_hist(match,dataset)
        matchdata = dataset[dataset['matchID'] == match]
        
        countryAlpha = matchdata['countryAlpha'].iloc[0]
        countryBeta = matchdata['countryBeta'].iloc[0]
        
        scoreAlpha = matchdata['fscoreAlpha'].iloc[0]
        scoreBeta = matchdata['fscoreBeta'].iloc[0]
        
        
        hist2d[hist2d==0] = -10
        
        matchTitle = countryAlpha + ' vs ' + countryBeta
        print(matchTitle)
        print(str(scoreAlpha) + ' - ' + str(scoreBeta))
        
        # definitions for the axes
        left, width = 0.1, 0.62
        bottom, height = 0.1, 0.62
        bottom_h = left_h = left + width + 0.02
        
        
        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]
        # start with a rectangular Figure
        plt.figure(matchTitle,figsize=(5, 5))
        axScatter = plt.axes(rect_scatter)
        axHistx = plt.axes(rect_histx)
        axHisty = plt.axes(rect_histy)
        
        # no labels
        axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)
        
        # the scatter plot:
        axScatter.imshow(np.transpose(hist2d),interpolation = 'nearest')
        
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
        print(hist2d)
    plt.show()


def plot_question_answers(dataset,questionList):
    if not questionList:
        questionList = dataset['questionID'].unique()
    for question in questionList :
        questionData = dataset[dataset['questionID'] == question]
        questionText = questionData['question'].iloc[0]        
        
        answers = questionData['answer']
        countries = answers.unique()
        hist = dict((x, answers[answers == x].count()) for x in countries)
        sorted_hist = sorted(hist.items(), key=operator.itemgetter(1), reverse = True)
        sorted_hist_labels = [k[0] for k in sorted_hist]
        sorted_hist_values = [k[1] for k in sorted_hist]
        print(questionText)
        print(hist)
        fig,ax = plt.subplots()
        ax.set_title(questionText)
        ax.bar(np.arange(len(sorted_hist)),sorted_hist_values,1)
        ax.set_xticks(np.arange(len(sorted_hist)) + 0.5)
        ax.set_xticklabels(sorted_hist_labels,rotation=60 if len(countries)>4 else 0,ha ='center') 
        plt.subplots_adjust(bottom=0.15)
    plt.show()