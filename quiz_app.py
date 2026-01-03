import streamlit as st
import pandas as pd
import altair as alt
import os
from datetime import datetime
from multiple_options import get_questions, load_questions
from ml_part import get_adaptive_quiz

# -------- Config ----------
st.set_page_config(page_title="IAS Quiz Platform", layout="wide")
RESULTS_FILE = "results.csv"
USERS_FILE = "users.csv"
RESOURCES_FILE = "resources.csv"

# -------- Init helper files/headers (safe) ----------
def ensure_file(path, header_cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=header_cols).to_csv(path, index=False)

ensure_file(USERS_FILE, ["username", "fullname", "password"])
ensure_file(RESULTS_FILE, ["timestamp", "user", "subject", "subtopic", "score", "total"])

# -------- Session-state defaults ----------
for key, val in {
    "logged_in": False, "username": None, "fullname": None,
    "quiz_started": False, "questions": [], "answers": {}, "submitted": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------- Utility: safe read & normalize results.csv ----------
def read_results_safe():
    expected_cols = ["timestamp", "user", "subject", "subtopic", "score", "total"]
    if not os.path.exists(RESULTS_FILE):
        return pd.DataFrame(columns=expected_cols)
    try:
        df = pd.read_csv(RESULTS_FILE)
        if "username" in df.columns and "user" not in df.columns:
            df = df.rename(columns={"username": "user"})
        if set(expected_cols).issubset(df.columns):
            df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
            df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0).astype(int)
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df[expected_cols]
    except Exception:
        lines = []
        with open(RESULTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.rstrip("\n\r") for ln in f if ln.strip()]
        if not lines:
            return pd.DataFrame(columns=expected_cols)
        header = lines[0].split(",")
        data_lines = lines[1:]
        rows = []
        for ln in data_lines:
            parts = ln.split(",")
            if len(parts) == 6:
                rows.append(parts)
            elif len(parts) == 5:
                rows.append([parts[0], "", parts[1], parts[2], parts[3], parts[4]])
            elif len(parts) > 6:
                user = ",".join(parts[1:-4])
                subject, subtopic, score, total = parts[-4], parts[-3], parts[-2], parts[-1]
                rows.append([parts[0], user, subject, subtopic, score, total])
            else:
                continue
        df = pd.DataFrame(rows, columns=expected_cols)
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
        df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0).astype(int)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df

# -------- Auth: signup & login ----------
def signup_user(username, fullname, password):
    users = pd.read_csv(USERS_FILE)
    if username in users["username"].values:
        return False, "Username already exists."
    new = pd.DataFrame([[username, fullname, password]], columns=["username", "fullname", "password"])
    users = pd.concat([users, new], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)
    return True, "Signup successful."

def login_user(username, password):
    users = pd.read_csv(USERS_FILE)
    mask = (users["username"] == username) & (users["password"] == password)
    if mask.any():
        fullname = users.loc[mask, "fullname"].values[0]
        return True, fullname
    return False, None

# -------- Navigation (dynamic) ----------
if st.session_state.logged_in:
    # Show welcome message above sidebar
    st.markdown(f"### 👋 Welcome, {st.session_state.fullname}!")
    menu = ["Quiz", "Resources", "Analytics", "Logout"]
else:
    menu = ["Login", "Sign Up", "Resources"]

choice = st.sidebar.selectbox("Navigate to:", menu)

# -------- PAGE: Sign Up ----------
if choice == "Sign Up":
    st.title("🆕 Create an account")
    col1, col2 = st.columns(2)
    with col1:
        new_fullname = st.text_input("Full name")
        new_username = st.text_input("Username")
    with col2:
        new_password = st.text_input("Password", type="password")
    if st.button("Create account"):
        if not (new_fullname and new_username and new_password):
            st.warning("Fill all fields.")
        else:
            ok, msg = signup_user(new_username.strip(), new_fullname.strip(), new_password)
            if not ok:
                st.error(msg)
            else:
                st.success(msg)
                st.info("Now go to Login and sign in.")
                st.rerun()

# -------- PAGE: Login ----------
elif choice == "Login":
    st.title("🔐 Login")
    user_in = st.text_input("Username")
    pwd_in = st.text_input("Password", type="password")
    if st.button("Login"):
        ok, fullname = login_user(user_in.strip(), pwd_in)
        if ok:
            st.session_state.logged_in = True
            st.session_state.username = user_in.strip()
            st.session_state.fullname = fullname
            st.success(f"Welcome, {fullname}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# -------- PAGE: Logout ----------
elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.fullname = None
    st.success("Logged out.")
    st.rerun()

# -------- PAGE: Resources ----------
elif choice == "Resources":
    st.title("📚 IAS Preparation Resources")
    if not os.path.exists(RESOURCES_FILE):
        st.error("⚠️ 'resources.csv' file not found in current directory.")
    else:
        try:
            res = pd.read_csv(RESOURCES_FILE)
            if "subject" not in res.columns or "subtopic" not in res.columns:
                st.error("resources.csv must contain columns: subject, subtopic, youtube_link/link")
            else:
                link_col = "youtube_link" if "youtube_link" in res.columns else ("link" if "link" in res.columns else None)
                expected_cols = {"subject", "subtopic"}
                if link_col:
                    expected_cols.add(link_col)
                if not expected_cols.issubset(res.columns):
                    st.error(f"⚠️ The CSV must have these columns: {expected_cols}")
                else:
                    for subj in sorted(res["subject"].dropna().unique()):
                        with st.expander(f"📘 {subj}"):
                            subset = res[res["subject"] == subj]
                            for _, row in subset.iterrows():
                                yt = row.get(link_col, "")
                                yt_link = f"[▶️ Watch Playlist]({yt})" if pd.notna(yt) and str(yt).strip() else ""
                                st.markdown(f"**{row['subtopic']}** — {yt_link}")
        except Exception as e:
            st.error(f"Error reading resources.csv: {e}")

# -------- PAGE: Quiz ----------
elif choice == "Quiz":
    if not st.session_state.logged_in:
        st.warning("Please log in first to take quizzes.")
        st.stop()

    st.title("🧠 IAS Adaptive Quiz Platform")

    try:
        master_df = load_questions()
    except Exception as e:
        st.error(f"Could not load questions dataset: {e}")
        st.stop()

    subjects = master_df["subject"].dropna().unique().tolist()
    if not subjects:
        st.error("No subjects found in question bank.")
        st.stop()
    subject = st.selectbox("Select Subject", subjects)

    subtopics = master_df[master_df["subject"] == subject]["subtopic"].dropna().unique().tolist()
    if not subtopics:
        st.error("No subtopics found for this subject.")
        st.stop()
    subtopic = st.selectbox("Select Topic", subtopics)

    num_qs = st.slider("Number of Questions", 5, 20, 10)

    if st.button("Start Quiz"):
        try:
            qdf = get_questions(subject=subject, subtopic=subtopic, n=num_qs)
            q_list = qdf.reset_index(drop=True).to_dict(orient="records") if isinstance(qdf, pd.DataFrame) else qdf
        except Exception as e:
            st.error(f"Error obtaining questions: {e}")
            q_list = []

        if not q_list:
            st.warning("No questions available for the selected subject/topic.")
        else:
            st.session_state.quiz_started = True
            st.session_state.questions = q_list
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.rerun()

    if st.session_state.quiz_started and st.session_state.questions:
        st.subheader(f"Quiz: {subject} — {subtopic}")
        for idx, row in enumerate(st.session_state.questions):
            qid = f"q{idx}"
            st.write(f"**Q{idx+1}: {row.get('question','(no question text)')}**")
            options = row.get("options") if isinstance(row.get("options"), (list, tuple)) else [
                row.get(k) for k in ("optionA","optionB","optionC","optionD") if pd.notna(row.get(k))
            ]
            if not options:
                st.warning("No options found for this question.")
                continue

            # NO preselection
            choice = st.radio("Choose:", options, key=qid, index=None)
            if choice:  # only save if user chooses
                st.session_state.answers[qid] = choice

        if st.button("Submit Quiz"):
            st.session_state.submitted = True

        if st.session_state.submitted:
            score = 0
            correct_easy = total_easy = 0
            correct_med = total_med = 0
            correct_hard = total_hard = 0

            st.subheader("Review & Results")
            for idx, row in enumerate(st.session_state.questions):
                qid = f"q{idx}"
                chosen = st.session_state.answers.get(qid, None)
                ans_letter = str(row.get("answer","")).strip().upper()
                correct_text = row.get(f"option{ans_letter}") if ans_letter in ("A","B","C","D") else row.get("correct") or row.get("answer_text") or row.get("answer")
                d = int(row.get("difficulty",2))
                if d==1: total_easy+=1
                elif d==2: total_med+=1
                elif d==3: total_hard+=1

                if not chosen:
                    st.warning(f"Q{idx+1}: No answer selected. Correct: **{correct_text}**. {row.get('explanation','')}")
                    continue

                if chosen == correct_text:
                    score += 1
                    if d==1: correct_easy+=1
                    elif d==2: correct_med+=1
                    elif d==3: correct_hard+=1
                    st.success(f"Q{idx+1}: ✅ Correct — {row.get('explanation','')}")
                else:
                    st.error(f"Q{idx+1}: ❌ Wrong. You chose **{chosen}**. Correct: **{correct_text}**. {row.get('explanation','')}")

            total_qs = len(st.session_state.questions)
            st.markdown(f"### 🎯 Final Score: **{score}/{total_qs}**  ({round(score/total_qs*100,2)}%)")

            # Save result
            result_row = {
                "user": st.session_state.username,
                "subject": subject,
                "subtopic": subtopic,
                "score": int(score),
                "total": int(total_qs)
            }
            row_df = pd.DataFrame([result_row])
            if not os.path.exists(RESULTS_FILE):
                row_df.to_csv(RESULTS_FILE, index=False)
            else:
                row_df.to_csv(RESULTS_FILE, mode="a", index=False, header=False)

            st.subheader("Performance by Difficulty")
            st.write(f"Easy: {correct_easy}/{total_easy}")
            st.write(f"Medium: {correct_med}/{total_med}")
            st.write(f"Hard: {correct_hard}/{total_hard}")

            try:
                suggested = get_adaptive_quiz(master_df, score=score*100/total_qs)
                if isinstance(suggested, pd.DataFrame) and not suggested.empty:
                    st.subheader("Suggested Next Quiz (sample)")
                    cols = [c for c in ["question","subject","subtopic","difficulty"] if c in suggested.columns]
                    st.dataframe(suggested[cols].reset_index(drop=True).head())
                else:
                    st.info("No adaptive suggestion available right now. Great work!")
            except Exception:
                pass

# -------- PAGE: Analytics ----------
elif choice == "Analytics":
    if not st.session_state.logged_in:
        st.warning("Please log in to view analytics.")
        st.stop()

    st.title("📊 Progress Dashboard")

    results = read_results_safe()
    if results.empty:
        st.info("No quiz results yet. Take a quiz to populate analytics.")
        st.stop()

    username = st.session_state.username
    fullname = st.session_state.fullname
    user_mask = (results["user"] == username) | (results["user"] == fullname)
    user_results = results[user_mask].copy()
    if user_results.empty:
        st.info("No results found for your account.")
        st.dataframe(results.sort_values(by="timestamp", ascending=False).head(10))
        st.stop()

    user_results["timestamp"] = pd.to_datetime(user_results["timestamp"], errors="coerce")
    user_results["accuracy"] = (user_results["score"]/user_results["total"])*100
    user_results = user_results.sort_values("timestamp")

    st.subheader("Recent Results")
    st.dataframe(user_results.assign(timestamp=user_results["timestamp"].dt.strftime("%d-%b-%Y %H:%M")).reset_index(drop=True).head(10))

    score_chart = alt.Chart(user_results).mark_line(point=True).encode(
        x=alt.X("timestamp:T", title="Time"),
        y=alt.Y("score:Q", title="Score"),
        color=alt.Color("subject:N", title="Subject")
    ).properties(title="Score Trend Over Time")
    st.altair_chart(score_chart, use_container_width=True)

    weak = user_results.groupby("subtopic")["accuracy"].mean().sort_values().head(8)
    if not weak.empty:
        weak_chart = alt.Chart(weak.reset_index()).mark_bar().encode(
            x=alt.X("subtopic:N", sort="-y", title="Subtopic"),
            y=alt.Y("accuracy:Q", title="Average Accuracy")
        ).properties(title="Weakest Topics (by avg accuracy)")
        st.altair_chart(weak_chart, use_container_width=True)

    st.subheader("Summary")
    st.write(f"Quizzes taken: {len(user_results)}")
    st.write(f"Average accuracy: {round(user_results['accuracy'].mean(),2)}%")
