import pickle

with open('data/o_normal_columns.pkl', 'rb') as f:
    o_normal_columns = pickle.load(f)

with open('data/o_advanced_columns.pkl', 'rb') as f:
    o_advanced_columns = pickle.load(f)

with open('data/d_normal_columns.pkl', 'rb') as f:
    d_normal_columns = pickle.load(f)

with open('data/d_advanced_columns.pkl', 'rb') as f:
    d_advanced_columns = pickle.load(f)

with open('data/other_columns.pkl', 'rb') as f:
    other_columns = pickle.load(f)

with open('data/X_columns.pkl', 'rb') as f:
    X_columns = pickle.load(f)
