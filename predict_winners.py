import pandas as pd
import trueskill as ts
import itertools
import math

winner_cols = ['WPlayer1', 'WPlayer2', 'WPlayer3', 'WPlayer4', 'WPlayer5']
loser_cols = ['LPlayer1', 'LPlayer2', 'LPlayer3', 'LPlayer4', 'LPlayer5']

player_cols = winner_cols + loser_cols
relevant_cols = ['Map', 'Date', 'Score', 'Team'] + winner_cols + loser_cols

region = 'AUS'
df = pd.read_pickle(region + '_combined_midair_games.p')

players = list(set([item for sublist in df[player_cols].values.tolist() for item in sublist]))
players_ts = dict(zip(players, [ts.Rating() for i in players]))
players_ts_time = {player: [] for player in players}


def rankings(df, penalty):
    for i, row in df.iterrows():
    # Find ratings in dictionary
        winner_list = list(filter(None, list(row[winner_cols])))
        loser_list = list(filter(None, list(row[loser_cols])))
        t1 = [players_ts[player] for player in winner_list]
        t2 = [players_ts[player] for player in loser_list]
    # Get ratings after match
        a, b = (ts.rate([t1, t2], ranks=[0, 1]))
    #print (a,b)
        if row['Team'] == 'Tie':
            a, b = (ts.rate([t1, t2], ranks=[0, 0]))
        # Update ratings in dictionary (not necessary to split winners and losers, but easier to read and debug)
        for i, player in list(enumerate(winner_list)):
            players_ts[player] = a[i]
            players_ts_time[player].append(a[i].mu)
        for i, player in list(enumerate(loser_list)):
            players_ts[player] = b[i]
            players_ts_time[player].append(b[i].mu)
    
    return 0

BETA = 4.1666

# Takes in 2 lists of teams: e.g. [player1, player2], [player3, player4]
def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    trueskill = ts.global_env()
    return round(trueskill.cdf(delta_mu / denom), 2)

