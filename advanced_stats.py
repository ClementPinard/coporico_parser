import numpy as np
import pandas as pd

def guessed_winner(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	print(match)
	print(match['fscoreAlpha'] == 0)
	return np.sign(match['fscoreAlpha'] - match['fscoreBeta'][1]) == np.sign(bet['pronoAlpha'] - bet['pronoBeta'])

def guessed_score(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	print(match)
	return match['fscoreAlpha'][1] == match['pronoAlpha'][1] and bet['fscoreBeta'] == bet['pronoBeta']

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
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			score = score + (3 if guessed_winner(k,dataset) else 0) + (2 if guessed_score(k,dataset) else 0)

		print(user['name'], score)

def compute_normalized_points(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	for _,user in userData.iterrows():
		bets = matchData[matchData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			score = score + (3 if guessed_winner(k) else 0) + (2 if guessed_score(k) else 0)

		print(user['name'], score)