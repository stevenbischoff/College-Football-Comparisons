import pickle

o_normal_columns = {
    'points/game': 'Points',
    'totalYards/game': 'Total Yards',
    'firstDowns/game': 'First Downs',
    'netPassingYards/game': 'Net Passing Yards',
    'passAttempts/game': 'Pass Attempts',
    'passCompletions/game': 'Pass Completions',
    'passingTDs/game': 'Passing TDs',
    'rushingYards/game': 'Rushing Yards',
    'rushingAttempts/game': 'Rush Attempts',
    'rushingTDs/game': 'Rushing TDs',
    'turnovers/game': 'Turnovers',
    #'fumblesLost/game',
    #'thirdDownConversions/game',
    #'fourthDowns/game',
    #'fourthDownConversions/game', 
    #'fourthDownPercent',
    'thirdDownPct': '3rd Down Conversion Rate',
    'rushingPct': 'Rushing Plays (% total)',
    'rushingYardsPct': 'Rushing Yards (% total)',
    'completionPct': 'Pass Completion Rate',
    'rushingYards/attempt': 'Yards per Rush',
    'passingYards/attempt': 'Yards per Pass',
}

with open('static/o_normal_columns.pkl', 'wb') as f:
    pickle.dump(o_normal_columns, f)

o_advanced_columns = {
    'o_ppa': 'PPA/Play', 
    'o_success_rate': 'Success Rate',
    'o_explosiveness': 'Explosiveness',
    'o_power_success': 'Power Success Rate',   
    'o_stuff_rate': 'Stuff Rate',
    'o_standard_downs_rate': 'Standard Downs Rate',
    'o_line_yards': 'Line Yards/Rush',
    'o_open_field_yards': 'Open Field Yards/Rush',
    'o_second_level_yards': 'Second Level Yards/Rush',
    #'o_standard_downs_success_rate',
    #'o_standard_downs_explosiveness', 
    #'o_passing_downs_success_rate',
    #'o_passing_downs_explosiveness',
    'o_rushing_plays_success_rate': 'Rushing Success Rate',
    'o_rushing_plays_explosiveness': 'Rushing Explosiveness',
    'o_rushing_plays_ppa': 'PPA/Rush',
    'o_passing_plays_success_rate': 'Passing Success Rate',
    'o_passing_plays_explosiveness': 'Passing Explosiveness',
    'o_passing_plays_ppa': 'PPA/Pass',
    #'o_plays/drive': 'Plays/Drive' # maybe bad play and drive data
    #'o_points_per_opportunity', # bad data <=2013
}

with open('static/o_advanced_columns.pkl', 'wb') as f:
    pickle.dump(o_advanced_columns, f)

d_normal_columns = {
    'points_opp/game': 'Opp. Points',
    'totalYards_opp/game': 'Opp. Total Yards',
    'firstDowns_opp/game': 'Opp. First Downs',
    'netPassingYards_opp/game': 'Opp. Net Passing Yards',
    'passingAttempts_opp/game': 'Opp. Pass Attempts',
    'passingCompletions_opp/game': 'Opp. Pass Completions',
    'passingTDs_opp/game': 'Opp. Passing TDs',
    'rushingYards_opp/game': 'Opp. Rushing Yards',
    'rushingAttempts_opp/game': 'Opp. Rush Attempts',
    'rushingTDs_opp/game': 'Opp. Rushing TDs',
    'turnovers_opp/game': 'Opp. Turnovers',
    #'fumblesLost/game',
    #'thirdDownConversions/game',
    #'fourthDowns/game',
    #'fourthDownConversions/game', 
    #'fourthDownPercent',
    'thirdDownPct_opp': 'Opp. 3rd Down Conversion Rate',
    'rushingPct_opp': 'Opp. Rushing Plays (% total)',
    'rushingYardsPct_opp': 'Opp. Rushing Yards (% total)',
    'completionPct_opp': 'Opp. Pass Completion Rate',
    'rushingYards/attempt_opp': 'Opp. Yards per Rush',
    'passingYards/attempt_opp': 'Opp. Yards per Pass',
}

with open('static/d_normal_columns.pkl', 'wb') as f:
    pickle.dump(d_normal_columns, f)

d_advanced_columns = {
    'd_ppa': 'Opp. PPA/Play', 
    'd_success_rate': 'Opp. Success Rate',
    'd_explosiveness': 'Opp. Explosiveness',
    'd_power_success': 'Opp. Power Success Rate',   
    'd_stuff_rate': 'Opp. Stuff Rate',
    'd_standard_downs_rate': 'Opp. Standard Downs Rate',
    'd_line_yards': 'Opp. Line Yards/Rush',
    'd_open_field_yards': 'Opp. Open Field Yards/Rush',
    'd_second_level_yards': 'Opp. Second Level Yards/Rush',
    #'d_standard_downs_success_rate',
    #'d_standard_downs_explosiveness', 
    #'d_passing_downs_success_rate',
    #'d_passing_downs_explosiveness',
    'd_rushing_plays_success_rate': 'Opp. Rushing Success Rate',
    'd_rushing_plays_explosiveness': 'Opp. Rushing Explosiveness',
    'd_rushing_plays_ppa': 'Opp. PPA/Rush',
    'd_passing_plays_success_rate': 'Opp. Passing Success Rate',
    'd_passing_plays_explosiveness': 'Opp. Passing Explosiveness',
    'd_passing_plays_ppa': 'Opp. PPA/Pass',
    #'d_plays/drive': 'Opp. Plays/Drive' # maybe bad play and drive data
    #'d_points_per_opportunity', # bad data <=2013
}

with open('static/d_advanced_columns.pkl', 'wb') as f:
    pickle.dump(d_advanced_columns, f)
    
other_columns = {
    'wins/game': 'Wins',
    'penalties/game': 'Penalties'
}

with open('static/other_columns.pkl', 'wb') as f:
    pickle.dump(other_columns, f)

X_columns = {**o_normal_columns, **o_advanced_columns,
             **d_normal_columns, **d_advanced_columns, **other_columns}

with open('static/X_columns.pkl', 'wb') as f:
    pickle.dump(X_columns, f)
