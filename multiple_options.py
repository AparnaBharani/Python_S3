import pandas as pd
import random

QUESTIONS_FILE = "questions.csv"

def load_questions():
    try:
        df = pd.read_csv(
            "questions.csv",
            quotechar='"',      # handle quoted text properly
            on_bad_lines="skip" # skip badly formatted rows
        )
        return df
    except FileNotFoundError:
        raise FileNotFoundError("questions.csv not found. Please create it first.")


def get_questions(subject=None, subtopic=None, difficulty=None, n=10):
    df = load_questions()
    if subject:
        df = df[df["subject"] == subject]
    if subtopic:
        df = df[df["subtopic"] == subtopic]
    if difficulty:
        df = df[df["difficulty"] == difficulty]
    return df.sample(n=min(n, len(df)), random_state=random.randint(0, 10000))
