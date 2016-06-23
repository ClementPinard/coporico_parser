import numpy as np
import pandas as pd

def odds_score(match,dataset):
	matchID = match['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	return (hist[match['fscoreAlpha'],match['fscoreBeta']])/numBets


def odds_winner(match,dataset):
	matchID = match['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	numSameBets = 0
	sign = np.sign(match['fscoreAlpha'] - match['fscoreBeta'])
	if sign == 0:
		for i in range(6):
			numSameBets = numSameBets + hist[i,i]
	else:
		for i in range(6):
			for j in range(i):
				numSameBets = numSameBets + (hist[j,i] if sign == -1 else hist[i,j])
	return numSameBets/numBets

def odds_question(question,dataset):
	questionID = question['questionID']
	answer = question['answer']
	questionsBets = dataset['questionBetsDataset']
	questionBets = questionsBets[questionsBets['questionID'] == questionID]
	numBets = len(questionBets)
	numGoodBets = len(questionBets[questionBets['questionBet'] == answer])
	
	return numGoodBets/numBets
	


def guessed_winner(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	if match['fscoreAlpha'].iloc[0] == 'None':
		return 0
	return np.sign((match['fscoreAlpha'] - match['fscoreBeta']).iloc[0]) == np.sign((bet['pronoAlpha'] - bet['pronoBeta']))

def guessed_score(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	if match['fscoreAlpha'].iloc[0] == 'None':
		return 0
	return match['fscoreAlpha'].iloc[0] == bet['pronoAlpha'] and match['fscoreBeta'].iloc[0] == bet['pronoBeta']

def get_bet_hist(match, dataset):
	matchdata = dataset[dataset['matchID'] == match]
	
	prono_x = matchdata['pronoAlpha']
	prono_y = matchdata['pronoBeta']
	edges = [0,1,2,3,4,5,6]
	hist2d = np.histogram2d(prono_x, prono_y,bins = (edges,edges))
	return prono_x, prono_y, hist2d[0]

def compute_odds(dataset):
	matchData = dataset['matchDataset']
	questionData =dataset['questionDataset']
	odds_scores = []
	odds_winners = []
	odds_questions = []
	for _,match in matchData.iterrows():
		odds_scores.append(odds_score(match, dataset))
		odds_winners.append(odds_winner(match, dataset))
		
	for _,question in questionData.iterrows():
		odds_questions.append(odds_question(question,dataset))
		
	return odds_scores,odds_winners,odds_questions

def compute_standard_points(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	questionBetsData = dataset['questionBetsDataset']
	standard_scores = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		questionBets = questionBetsData[questionBetsData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			score = score + (3 if guessed_winner(k,dataset) else 0) + (2 if guessed_score(k,dataset) else 0)
		for _,j in questionBets.iterrows():
			if j['answer'] == j['questionBet']:
				score = score + (14 if j['questionID'] == 1 else 7)
		standard_scores.append(score)
	return standard_scores



def compute_normalized_points(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	matchData = dataset['matchDataset']
	normalized_scores = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			match = matchData[matchData['matchID'] == k['matchID']]
			odds_score = match['odds_score'].values[0]
			odds_winner = match['odds_winner'].values[0]
			score = score + (3/odds_winner if guessed_winner(k,dataset) else 0) + (2/odds_score if guessed_score(k,dataset) else 0) - 5

		normalized_scores.append(score)
	return normalized_scores