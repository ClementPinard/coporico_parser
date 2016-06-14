'''A simple script to make some nice statistics with your corporico team !
Hopefully, more to come you're welcomed to contribute !

usage : python --company <string> --cookie <string>
'''



from __future__ import unicode_literals
import requests
import bs4 as BeautifulSoup
import pandas as pd #LOL
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
nullfmt = NullFormatter()         # no labels
import argparse

parser = argparse.ArgumentParser(description='A simple script to make some nice statistics with your corporico team')
parser.add_argument('--company',required=True, help='url of your corporico will be <company>.corporico.fr')
parser.add_argument('--cookie',required=True, help='cookie of your corporico session')

args = parser.parse_args()



cookies = dict(_korpobet_session=args.cookie)

pronos = dict()
matches = []
teams= dict()
scores= dict()

def get_match_pronos(match_ids):
    names = []
    teams = []
    fscoresAlpha = []
    fscoresBeta = []
    pronosAlpha = []
    pronosBeta = []
    countriesAlpha = []
    countriesBeta = []
    match_IDs = []
    for k in match_ids:
        j=1
        while True:
            payload = {'page': j}
            r=requests.get('http://'+args.company+'.corporico.fr/matches/' + str(k),cookies=cookies, params=payload)
            print(r.url)
            if r.url == 'http://' + args.company + '.corporico.fr/sessions/new':
                print("cookie or company error")
                exit()
                 
            soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
            
            if j==1:
                countries = soup.findAll('div', attrs={'class': 'match-item-team-name'})
                countries = [country.text.strip() for country in countries]
                final_score = soup.findAll('div',attrs={'class': 'has-score'})
                final_score = [int(score.text.strip()) for score in final_score]
            
            
            entries = soup.findAll('div', attrs={'class': 'leaderboard-item'})
            if(len(entries) == 0):
                break
            for soup in entries :
                #print soup
                nameAndTeam = soup.find('div', attrs={'class': 'leaderboard-item-cell-team'}).find_next('div', attrs={'class': 'leaderboard-item-label'}).text.strip()
                name = nameAndTeam[:nameAndTeam.find('\n')]
                if 'TEAM' in nameAndTeam:
                    team = nameAndTeam[nameAndTeam.find('TEAM ') + 5:]
                else:
                    team = 'None'
                prono = soup.find('div', attrs={'class': 'leaderboard-item-cell-bet-count'}).find_next(True).find_next(True).text
                prono = prono.split('-')
                prono = [int(prono[0]),int(prono[1])]
                pronosAlpha.append(prono[0])
                pronosBeta.append(prono[1])
                teams.append(team)
                names.append(name)
                fscoresAlpha.append(final_score[0])
                fscoresBeta.append(final_score[1])
                countriesAlpha.append(countries[0])
                countriesBeta.append(countries[1])
                match_IDs.append(k)
                
            j = j+1
    data = {'name':names,
            'team':teams,
            'fscoreAlpha':fscoresAlpha,
            'fscoreBeta':fscoresBeta,
            'pronoAlpha':pronosAlpha,
            'pronoBeta':pronosBeta,
            'countryAlpha':countriesAlpha,
            'countryBeta':countriesBeta,
            'matchID':match_IDs
            }
    dataset = pd.DataFrame(data)
    return dataset
        
#dataset = get_match_pronos([1,2,3,4,5,6,7,8,39,40,11,12])
#dataset.to_csv('test.csv',encoding='utf-8', index=False)
dataset = pd.read_csv('test.csv')

def plot_histograms():
    for match in dataset['matchID'].unique() :
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
    plt.show()
    
plot_histograms()
