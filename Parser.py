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
import advanced_stats

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

def request_page(payload,url):
    r = requests.get(url,cookies=cookies, params=payload)
    print(r.url)
    if r.url == 'http://' + args.company + '.corporico.fr/sessions/new':
        print("cookie or company error")
        exit()
    return r

def get_bets():
    matchList = []
    fscoresAlpha = []
    fscoresBeta = []
    countriesAlpha = []
    countriesBeta = []
            
    questionList=[]
    scopes = ['futur','past']
    for scope in scopes:
        j=1
        while True:
            payload = {'page':j,'scope':scope}
            url = 'http://'+args.company+'.corporico.fr/bets'
            r=request_page(payload,url) 
                     
            soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
            matchEntries = soup.findAll('div', attrs={'class': 'match-item-container'})
            questionEntries = soup.findAll('div', attrs={'class':'question-item-container'})
            if len(matchEntries) ==0:
                break
            for match in matchEntries:
                if(match.find('form')):
                    break
                matchURL = match.a['href']
                matchID = int(matchURL[matchURL.rfind('/')+1:])
                matchList.append(matchID)
                countries = match.findAll('div', attrs={'class': 'match-item-team-name'})
                countries = [country.text.strip() for country in countries]
                countriesAlpha.append(countries[0])
                countriesBeta.append(countries[1])
                final_score = match.find('span',attrs={'class': 'form-match-cta-detail-alpha'}).text.strip()
                #final_score = ['None' if '_' in final_score else int(score.text.strip()) for score in final_score]
                if 'final' in final_score:
                    final_score = final_score[final_score.find(': ')+2:].split('-')
                    fscoresAlpha.append(int(final_score[0]))
                    fscoresBeta.append(int(final_score[1]))
                else:
                    fscoresAlpha.append('None')
                    fscoresBeta.append('None')

            for question in questionEntries:
                questionURL = question.a['href']
                questionList.append(int(questionURL[questionURL.rfind('/')+1:]))

            j=j+1
    data = {'matchID':matchList,
            'fscoreAlpha':fscoresAlpha,
            'fscoreBeta':fscoresBeta,
            'countryAlpha':countriesAlpha,
            'countryBeta':countriesBeta,
            }
    matchDataset = pd.DataFrame(data)

    return matchDataset, questionList

def get_match_bets(matchList):
    names = []
    teams = []
    pseudos = []
    userIDs = []
    pronoUserID = []
    pronosAlpha = []
    pronosBeta = []
    match_IDs = []
    for k in matchList['matchID']:
        j=1
        while True:
            payload = {'page':j}
            url = 'http://'+args.company+'.corporico.fr/matches/' + str(k)
            r=request_page(payload,url)
                 
            soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
            
            entries = soup.findAll('div', attrs={'class': 'leaderboard-item'})
            if(len(entries) == 0):
                break
            for soup in entries :
                identity = soup.find('div', attrs={'class': 'leaderboard-item-cell-team'})
                pseudo = identity.find_next('div', attrs={'class':'leaderboard-item-value-name'}).text.strip()
                userID = identity.find_next('div', attrs={'class':'leaderboard-item-value-name'}).a['href']
                userID = userID[userID.rfind('/') +1 :]
                if userID not in userIDs:
                    userIDs.append(userID)
                    nameAndTeam = identity.find_next('div', attrs={'class': 'leaderboard-item-label'}).text.strip()
                    if 'TEAM' in nameAndTeam:
                        name = nameAndTeam[:nameAndTeam.find('\n')]
                        team = nameAndTeam[nameAndTeam.find('TEAM ') + 5:]
                    else:
                        name = nameAndTeam
                        team = 'None'
                    names.append(name)
                    pseudos.append(pseudo)
                    teams.append(team)
                pronoUserID.append(userID)
                prono = soup.find('div', attrs={'class': 'leaderboard-item-cell-bet-count'}).find_next(True).find_next(True).text
                prono = prono.split('-')
                prono = [int(prono[0]),int(prono[1])]
                pronosAlpha.append(prono[0])
                pronosBeta.append(prono[1])
                match_IDs.append(k)
                
            j = j+1
    data = {'userID':pronoUserID,
            'pronoAlpha':pronosAlpha,
            'pronoBeta':pronosBeta,
            'matchID':match_IDs
            }
    matchDataset = pd.DataFrame(data)
    userData = {'name':names,
                'pseudo':pseudos,
                'team':teams,
                'userID':userIDs}
    userDataset = pd.DataFrame(userData)
    return matchDataset, userDataset



def get_question_pronos(questionList):
    pseudos = []
    questions=[]
    answers = []
    question_IDs = []
    for k in questionList:
        j=1
        while True:
            payload = {'page': j}
            url = 'http://'+args.company+'.corporico.fr/questions/' + str(k)
            r=request_page(payload,url)
            
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
    matchDataset,questionList = get_bets()
    questionDataset = get_question_pronos(questionList)
    betDataset, userDataset = get_match_bets(matchDataset)
    betDataset.to_csv('bets.csv',encoding='utf-8', index=False)
    matchDataset.to_csv('matches.csv',encoding='utf-8', index=False)
    questionDataset.to_csv('questions.csv',encoding='utf-8',index=False)
    userDataset.to_csv('users.csv',encoding='utf-8',index=False)

dataset = dict(userDataset = pd.read_csv('users.csv'),
questionDataset = pd.read_csv('questions.csv'),
matchDataset = pd.read_csv('matches.csv'),
betDataset = pd.read_csv('bets.csv'))


userIDs = dataset['userDataset']['userID']
names = dataset['userDataset']['name']
standard = advanced_stats.compute_standard_points(dataset)
normalized = advanced_stats.compute_normalized_points(dataset)

scoreDataset = pd.DataFrame({'name':names,
                             'userID':userIDs,
                             'standardScore':standard,
                             'normalizedScore':normalized})
scoreDataset.to_csv('scores.csv',encoding='utf-8',index=False)




#data_plots.plot_question_answers(questionDataset,False)  
#data_plots.plot_histograms(dataset,matchList=args.matchList)
