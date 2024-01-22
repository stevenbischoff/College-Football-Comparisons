import pickle

with open('static/o_normal_columns.pkl', 'rb') as f:
    o_normal_columns = pickle.load(f)

with open('static/o_advanced_columns.pkl', 'rb') as f:
    o_advanced_columns = pickle.load(f)

with open('static/d_normal_columns.pkl', 'rb') as f:
    d_normal_columns = pickle.load(f)

with open('static/d_advanced_columns.pkl', 'rb') as f:
    d_advanced_columns = pickle.load(f)

with open('static/other_columns.pkl', 'rb') as f:
    other_columns = pickle.load(f)

with open('static/X_columns.pkl', 'rb') as f:
    X_columns = pickle.load(f)
