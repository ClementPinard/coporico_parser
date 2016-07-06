import numpy as np
import pandas as pd

def odds_score(match,dataset):
	if match['fscoreAlpha'] == 'None' or match['fscoreBeta'] == 'None' :
		return 0
	matchID = match['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	return (hist[int(match['fscoreAlpha']),int(match['fscoreBeta'])])/numBets


def odds_winner(match,dataset):
	if match['fscoreAlpha'] == 'None' or match['fscoreBeta'] == 'None' :
		return 0
	matchID = match['matchID']
	_,bets,hist = get_bet_hist(matchID,dataset['betDataset'])
	numBets = len(bets)
	numSameBets = 0
	sign = np.sign(int(match['fscoreAlpha']) - int(match['fscoreBeta']))
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
	return np.sign(int(match['fscoreAlpha'].iloc[0]) - int(match['fscoreBeta'].iloc[0])) == np.sign((bet['pronoAlpha'] - bet['pronoBeta']))

def guessed_score(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	if match['fscoreAlpha'].iloc[0] == 'None':
		return 0
	return match['fscoreAlpha'].iloc[0] == bet['pronoAlpha'] and match['fscoreBeta'].iloc[0] == bet['pronoBeta']

def bet_distance(bet,dataset):
	matchData = dataset['matchDataset']
	matchID = bet['matchID']
	match = matchData[matchData['matchID'] == matchID]
	if match['fscoreAlpha'].iloc[0] == 'None':
		return 0
	return np.sqrt(np.power(int(match['fscoreAlpha'].iloc[0])-bet['pronoAlpha'],2) + np.power(int(match['fscoreBeta'].iloc[0])-bet['pronoBeta'],2))




def get_bet_hist(match, dataset):
	matchdata = dataset[dataset['matchID'] == match]
	
	prono_x = matchdata['pronoAlpha']
	prono_y = matchdata['pronoBeta']
	edges = [0,1,2,3,4,5,6]
	hist2d = np.histogram2d(prono_x, prono_y,bins = (edges,edges))
	return prono_x, prono_y, hist2d[0]

def get_scores_hists(dataset):
	return histStandard,histNormalized,histDistances

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
			if k['matchID'] >= 46:
				values = [4,2]
			else:
				values = [3,2]
			score = score + (values[0] if guessed_winner(k,dataset) else 0) + (values[1] if guessed_score(k,dataset) else 0)
		for _,j in questionBets.iterrows():
			if j['answer'] == j['questionBet']:
				score = score + (14 if j['questionID'] == 1 else 7)
		standard_scores.append(score)
	return standard_scores



def compute_normalized_points(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	matchData = dataset['matchDataset']
	questionBetsData = dataset['questionBetsDataset']
	questionData = dataset['questionDataset']
	normalized_scores = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		questionBets = questionBetsData[questionBetsData['userID'] == user['userID']]
		score = 0
		for _,k in bets.iterrows():
			match = matchData[matchData['matchID'] == k['matchID']]
			odds_score = match['odds_score'].iloc[0]
			odds_winner = match['odds_winner'].iloc[0]
			if k['matchID'] >= 46:
				values = [4,2]
			else:
				values = [3,2]
			score = score + (values[0]/odds_winner if guessed_winner(k,dataset) else 0) + (values[1]/odds_score if guessed_score(k,dataset) else 0) - 5

		for _,j in questionBets.iterrows():
			question = questionData[questionData['questionID'] == j['questionID']]
			if type(j['answer']) is str and question['odds_question'].iloc[0] > 0:
				if j['answer'] == j['questionBet']:
					odds = question['odds_question'].iloc[0]
					value = 14 if j['questionID'] == 1 else 7
					score = score + value/odds
				score = score - value

		normalized_scores.append(score)
	return normalized_scores

def compute_bet_distances(dataset):
	betData = dataset['betDataset']
	userData = dataset['userDataset']
	matchData = dataset['matchDataset']
	distances = []
	for _,user in userData.iterrows():
		bets = betData[betData['userID'] == user['userID']]
		distance = 0
		for _,k in bets.iterrows():
			distance = distance + bet_distance(k,dataset)
		distances.append(distance)
	return distances

def compute_unlucky_indeces(users):
	if (not 'standardScore' in users.index) or ('distanceScore' not in users.index):
		print('must first compute distances and standard scores')
		return
	indeces = []
	for _,user in users.iterrows():
		print(1000/(user['standardScore']*user['distanceScore']))
		indeces.append(1000/(user['standardScore']*user['distanceScore']))
	return indeces
	

def get_user_summary(dataset,userID):
	betData = dataset['betDataset']
	questionBetsDataset = dataset['questionBetsDataset']
	userData = dataset['userDataset']
	matchData = dataset['matchDataset']
	questionData = dataset['questionDataset']

	bets = betData[betData['userID'] == userID]
	questionBets = questionBetsDataset[questionBetsDataset['userID'] == userID]
	username = userData[userData['userID'] == userID]['name'].iloc[0]


	print('Questions : \n')
	for _,k in questionBets.iterrows():
		question = questionData[questionData['questionID'] == k['questionID']]
		odds = question['odds_question'].iloc[0]
		rate = 1/odds if odds>0 else 0
		print(k['question'],' : ',(k['answer'] if type(k['answer']) is str else ''),' , cote à ',rate,'\n')
		print(username,' a parié ',k['questionBet'])
		guessed = k['answer'] == k['questionBet']
		if not type(k['answer']) is str:
			value = 0
		else:
			value = 14 if k['questionID'] == 1 else 7
		print((value if guessed else 0 ),' points classiques')

		print((value*rate if guessed else 0) - value, 'points ajustés à la cote')

	print('Match Pronostics: \n')
	for _,j in bets.iterrows():
		match = matchData[matchData['matchID'] == j['matchID']]
		odds_score = match['odds_score'].iloc[0]
		odds_winner = match['odds_winner'].iloc[0]
		rate_winner = 1/odds_winner if odds_winner>0 else 0
		rate_score = 1/odds_score if odds_score>0 else 0
		print(match['countryAlpha'].iloc [0],' vs ',match['countryBeta'].iloc [0], 'score : ',
			    match['fscoreAlpha'].iloc[0], ' - ', match['fscoreBeta'].iloc[0],' , cote à ',
			    rate_winner, ' (winner)', rate_score,' (score)\n')
		print(username,' a parié ',j['pronoAlpha'], ' -',j['pronoBeta'])
	
		value_score = 2
		value_winner = 3
		guessedW = guessed_winner(j,dataset)
		guessedS = guessed_score(j,dataset)
		print((value_score if guessedS else 0 ) + (value_winner if guessedW else 0 ) ,' points classiques')

		print((value_score*rate_score if guessedS else 0) + (value_winner*rate_winner if guessedW else 0)- value_score - value_winner, 'points ajustés à la cote\n')
