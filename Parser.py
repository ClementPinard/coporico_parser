'''A simple script to make some nice statistics with your corporico team !
Hopefully, more to come you're welcomed to contribute !

usage : python --company <string> --cookie <string>
'''



from __future__ import unicode_literals
import requests
import bs4 as BeautifulSoup
import pandas as pd #LOL
import argparse
import data_plots

parser = argparse.ArgumentParser(description='A simple script to make some nice statistics with your corporico team')
parser.add_argument('--company',required=True, help='url of your corporico will be <company>.corporico.fr')
parser.add_argument('--cookie',required=True, help='cookie of your corporico session')
parser.add_argument('--matchList',default=[],help='List of match you want to get insight info on')
parser.add_argument('--load_csv',help='load csv file instead of parsing website')

args = parser.parse_args()



cookies = dict(_korpobet_session=args.cookie)

pronos = dict()
matches = []
teams= dict()
scores= dict()

def get_bets():
    j=1
    matchList = []
    questionList=[]
    while True:
        payload = {'page':j,'scope':'past'}
        r=requests.get('http://'+args.company+'.corporico.fr',cookies=cookies, params=payload)
        print(r.url)
        if r.url == 'http://' + args.company + '.corporico.fr/sessions/new':
            print("cookie or company error")
            exit()
                 
        soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        matchEntries = soup.findAll('div', attrs={'class': 'form-match'})
        questionEntries = soup.findAll('div', attrs={'class':'question-item-container'})
        if len(matchEntries) ==0:
            break
        for match in matchEntries:
            matchURL = match.a['href']
            matchList.append(int(matchURL[matchURL.rfind('/')+1:]))
        for question in questionEntries:
            questionURL = question.a['href']
            questionList.append(int(questionURL[questionURL.rfind('/')+1:]))

        j=j+1
    print (matchList)
    print(questionList)
    return matchList, questionList

def get_match_pronos(matchList):
    names = []
    teams = []
    pseudos = []
    fscoresAlpha = []
    fscoresBeta = []
    pronosAlpha = []
    pronosBeta = []
    countriesAlpha = []
    countriesBeta = []
    match_IDs = []
    for k in matchList:
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
                final_score = ['None' if '_' in final_score else int(score.text.strip()) for score in final_score]
            
            
            entries = soup.findAll('div', attrs={'class': 'leaderboard-item'})
            if(len(entries) == 0):
                break
            for soup in entries :
                identity = soup.find('div', attrs={'class': 'leaderboard-item-cell-team'})
                pseudo = identity.find_next('div', attrs={'class':'leaderboard-item-value-name'}).text.strip()
                nameAndTeam = identity.find_next('div', attrs={'class': 'leaderboard-item-label'}).text.strip()
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
                pseudos.append(pseudo)
                fscoresAlpha.append(final_score[0])
                fscoresBeta.append(final_score[1])
                countriesAlpha.append(countries[0])
                countriesBeta.append(countries[1])
                match_IDs.append(k)
                
            j = j+1
    data = {'name':names,
            'pseudo':pseudos,
            'team':teams,
            'fscoreAlpha':fscoresAlpha,
            'fscoreBeta':fscoresBeta,
            'pronoAlpha':pronosAlpha,
            'pronoBeta':pronosBeta,
            'countryAlpha':countriesAlpha,
            'countryBeta':countriesBeta,
            'matchID':match_IDs
            }
    matchDataset = pd.DataFrame(data)
    return matchDataset



def get_question_pronos(questionList):
    pseudos = []
    questions=[]
    answers = []
    question_IDs = []
    for k in questionList:
        j=1
        while True:
            payload = {'page': j}
            r=requests.get('http://'+args.company+'.corporico.fr/questions/' + str(k),cookies=cookies, params=payload)
            print(r.url)
            if r.url == 'http://' + args.company + '.corporico.fr/sessions/new':
                print("cookie or company error")
                exit()
                 
            soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
            
            if j==1:
                question = soup.find('div', attrs={'class': 'question-detail-title'})
                question = question.text.strip()
            
            
            entries = soup.findAll('div', attrs={'class': 'leaderboard-item'})
            if(len(entries) == 0):
                break
            for soup in entries :
                result= soup.findAll('div', attrs={'class': 'leaderboard-item-value'})
                pseudo = result[0].text.strip()
                answer = result[1].text.strip()
                pseudos.append(pseudo)
                answers.append(answer)
                questions.append(question)
                question_IDs.append(k)
                
            j = j+1
    data = {'pseudo':pseudos,
            'question':questions,
            'answer':answers,
            'questionID':question_IDs
            }
    dataset = pd.DataFrame(data)
    return dataset
        
if not args.load_csv:
    matchList,questionList = get_bets()
    questionDataset = get_question_pronos(questionList)
    matchDataset = get_match_pronos(matchList)
    matchDataset.to_csv('matches.csv',encoding='utf-8', index=False)
    questionDataset.to_csv('questions.csv',encoding='utf-8',index=False)
questionDataset = pd.read_csv('questions.csv')
matchDataset = pd.read_csv('matches.csv')
print(questionDataset)
print(matchDataset)

    
#data_plots.plot_histograms(dataset,matchList=args.matchList)
