# Python_S3
#  IAS Quiz Platform & Smart Study Assistant

**An Adaptive Learning System for IAS Exam Preparation**

##  Overview
This project is a web-based **adaptive quiz platform** designed to optimize preparation for the IAS (Indian Administrative Service) exam. Unlike static quiz applications, this system utilizes a difficulty-based adaptive algorithm to adjust to the learner's proficiency level in real-time.

The platform provides immediate feedback, tracks performance metrics across different difficulty levels (Easy, Medium, Hard), and integrates curated study resources (YouTube playlists) to help students address weak areas.

---


##  Key Features

### 1.  Adaptive Quiz Engine
* **Dynamic Question Selection:** The system fetches questions based on Subject and Subtopic.
* **Adaptive Logic:** Based on previous scores, the system intelligently recommends the next set of questions with varying difficulty ratios (e.g., scoring >70% triggers more Hard questions).

### 2.  Real-Time Evaluation
* **Instant Feedback:** Users receive immediate validation for their answers.
* **Detailed Explanations:** Whether correct or incorrect, the system provides explanations to reinforce learning.

### 3.  Analytics & Dashboard
* **Progress Tracking:** Visualizes score trends over time using interactive line charts.
* **Weakness Identification:** Identifies specific subtopics where accuracy is low.
* **Performance Breakdown:** Categorizes performance by difficulty (Easy vs. Medium vs. Hard).

### 4.  Resource Repository
* **Curated Content:** Provides direct links to YouTube playlists and study materials relevant to specific subjects and subtopics.

---

##  Tech Stack
* **Language:** Python
* **Frontend Framework:** Streamlit (for responsive, interactive UI)
* **Data Manipulation:** Pandas (for CSV handling and analytics)
* **Visualization:** Altair (for generating performance charts)
* **Storage:** CSV Files (Lightweight database for users, questions, and results)

---

## 📂 Project Structure

```text
├── quiz_app.py           # Main application entry point (Streamlit)
├── ml_part.py            # Contains the adaptive logic algorithm
├── multiple_options.py   # Helper functions to load and filter questions
├── questions.csv         # Database of quiz questions (Must be created)
├── resources.csv         # Database of study links (Must be created)
├── users.csv             # Stores user credentials (Auto-generated)
├── results.csv           # Stores quiz history and scores (Auto-generated)
└── README.md             # Project documentation
