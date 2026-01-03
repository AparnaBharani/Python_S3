import pandas as pd

def get_adaptive_quiz(df, score=None):
    if score is None:  # first quiz
        easy = df[df["difficulty"] == 1].sample(min(5, len(df[df["difficulty"] == 1])))
        med = df[df["difficulty"] == 2].sample(min(3, len(df[df["difficulty"] == 2])))
        hard = df[df["difficulty"] == 3].sample(min(2, len(df[df["difficulty"] == 3])))
    elif score >= 70:
        easy = df[df["difficulty"] == 1].sample(min(2, len(df[df["difficulty"] == 1])))
        med = df[df["difficulty"] == 2].sample(min(3, len(df[df["difficulty"] == 2])))
        hard = df[df["difficulty"] == 3].sample(min(5, len(df[df["difficulty"] == 3])))
    else:
        easy = df[df["difficulty"] == 1].sample(min(6, len(df[df["difficulty"] == 1])))
        med = df[df["difficulty"] == 2].sample(min(3, len(df[df["difficulty"] == 2])))
        hard = df[df["difficulty"] == 3].sample(min(1, len(df[df["difficulty"] == 3])))
    return pd.concat([easy, med, hard])
