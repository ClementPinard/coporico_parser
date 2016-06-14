'''A simple script to make some nice statistics with your corporico team !
Hopefully, more to come you're welcomed to contribute !

usage : python --company <string> --cookie <string>
'''

import requests
import bs4 as BeautifulSoup
import numpy as np
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

k=1
while True:
    j=1
    pronos_match = []
    while True:
        payload = {'page': j}
        r=requests.get('http://'+args.company+'.corporico.fr/matches/' + str(k),cookies=cookies, params=payload)
        print r.url
        if r.url == 'http://' + args.company + '.corporico.fr/sessions/new':
            print("cookie or company error")
            exit()
             
        soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        '''
        <div class="leaderboard-item-value">
                    2 - 0
                  </div>
        '''
        #print soup.div
        i=0
        if j==1:
            countries = soup.findAll('div', attrs={'class': 'match-item-team-name'})
            countries = [country.text.strip() for country in countries]
            final_score = soup.findAll('div',attrs={'class': 'has-score'})
            final_score = [int(score.text.strip()) for score in final_score]
        
        
        entries = soup.findAll('div', attrs={'class': 'leaderboard-item'})
        for soup in entries :
            #print soup
            nameAndTeam = soup.find('div', attrs={'class': 'leaderboard-item-cell-team'}).find_next('div', attrs={'class': 'leaderboard-item-label'}).text.strip()
            name = nameAndTeam[13:nameAndTeam.find('\n')]
            team = nameAndTeam[nameAndTeam.find('TEAM ') + 5]
            #print name
            #print team
            prono = soup.find('div', attrs={'class': 'leaderboard-item-cell-bet-count'}).find_next(True).find_next(True).text
            prono = prono.split('-')
            prono = [int(prono[0]),int(prono[1])]
            pronos_match.append(prono)
            #print (prono)
            i=i+1
            #print(i)
        if i == 0:
            break
        j = j+1
    if j==1:
        break
    else:
        matches.append(k)
        pronos[k] = pronos_match
        teams[k] = countries
        scores[k] = final_score
    k=k+1
    
    
for match in matches :
    countries = teams[match]
    score = scores[match]
    prono_x = np.array([k[0] for k in pronos[match]])
    prono_y = np.array([k[1] for k in pronos[match]])
    
    edges = [0,1,2,3,4,5,6]
    
    histx = np.histogram(prono_x,bins = edges)
    histy = np.histogram(prono_y,bins = edges)
    hist2d = np.histogram2d(prono_x, prono_y,bins = (edges,edges))
    
    print countries[0] + ' vs ' + countries[1]
    print str(score[0]) + ' - ' + str(score[1])
    print histx[0]
    print histy[0]
    print hist2d[0]
