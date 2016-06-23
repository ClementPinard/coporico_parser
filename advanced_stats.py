import numpy as np
import pandas as pd

def odds_score(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	return (hist[bet['pronoAlpha'],bet['pronoBeta']])/numBets


def odds_winner(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	numSameBets = 0
	sign = np.sign(bet['pronoAlpha'] - bet['pronoBeta'])
	if sign == 0:
		for i in range(6):
			numSameBets = numSameBets + hist[i,i]
	else:
		for i in range(6):
			for j in range(i):
				numSameBets = numSameBets + (hist[j,i] if sign == -1 else hist[i,j])
	return numSameBets/numBets


def guessed_winner(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	if match['fscoreAlpha'].iloc[0] == 'None':
		return 0
	a = np.sign(match['fscoreAlpha'] - match['fscoreBeta'])
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

def compute_standard_points(dataset):
	matchData = dataset['matchDataset']
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	standard_scores = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			score = score + (3 if guessed_winner(k,dataset) else 0) + (2 if guessed_score(k,dataset) else 0)

		standard_scores.append(score)
	return standard_scores



def compute_normalized_points(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	normalized_scores = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			score = score + (3*(-1 + 1/odds_winner(k,dataset)) if guessed_winner(k,dataset) else 0) + (2*(-1 + 1/odds_score(k,dataset)) if guessed_score(k,dataset) else 0)

		normalized_scores.append(score)
	return normalized_scores