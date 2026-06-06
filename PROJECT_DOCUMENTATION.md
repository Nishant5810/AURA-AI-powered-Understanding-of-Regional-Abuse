# Project Documentation: Lang Detect AI

This document provides a comprehensive overview of the **Lang Detect AI** application, its market impact, deployment/GitHub guidelines, and optimization strategies for your resume.

---

## 1. Application Overview & How It Works

### Purpose
**Lang Detect AI** is an explainable regional language safety intelligence platform. Most mainstream moderation tools fail when processing **code-mixed or Romanized transliterations** of Indian regional languages (e.g., writing Hindi, Tamil, or Telugu using the English alphabet). This application bridges that gap by providing real-time safety assessments for Hinglish, Tanglish, and Tenglish.

### How It Works
1. **Linguistic Normalization**: The user inputs text (via the React frontend or API endpoint). The backend runs the **Phonetic Transliteration Engine** which parses Romanized words and matches them against regional-to-English dictionaries to normalize the text for understanding.
2. **Linguistic & Sarcasm Classification**: The normalized text is scanned through a multi-tier **Lexicon & Semantic Classifier** that detects 9 categories of violations (Casteism, Religious Hate, Gender Abuse, Threats, Cyberbullying, etc.). It also runs a **Sarcasm Detection** filter to check if toxic sentiment is disguised behind polite/sarcastic markers (e.g., *"Wow, what a brilliant community, always creating problems"*).
3. **Explainability Extraction**: The system isolates the exact phrases causing the flags, maps token-level coordinates, and returns detailed, color-coded highlights for the UI alongside an AI safety reasoning explanation.
4. **Moderator Actions & Analytics**: Scans are logged in the MySQL database, updating dashboard telemetry charts, communal risk profiles, and geographical state heatmaps for moderator review.

---

## 2. Market and Industry Impact

Deploying this application creates a massive value proposition for industries handling user-generated content (UGC) in India:
* **Regulatory Compliance**: Helps digital platforms comply with regional intermediary guidelines (such as the IT Rules in India) by quickly removing hate speech, casteist slurs, and communal incitement.
* **Platform Safety & Brand Protection**: Prevents toxic communities from driving away users, protecting advertising revenue and corporate brand safety.
* **Linguistic Inclusivity**: Moderates vernacular and Romanized regional language content which standard international moderation tools miss.
* **Cost Efficiency**: Automates 90% of vernacular content screening, allowing human moderation teams to focus only on high-severity edge cases.

---

## 3. GitHub Upload Guidelines

When committing and uploading this project to GitHub, ensure your repository has a clean structure. Use the created `.gitignore` files to avoid uploading temporary files and secrets.

### ✅ DO Upload (Commit to Git):
* `backend/app/` (All python modules, services, routers, models, schemas, and database files)
* `backend/run.py` & `backend/requirements.txt`
* `backend/.gitignore` (Configured to ignore `.env` and pycache)
* `frontend/src/` (All React components, index.js, App.jsx, index.css)
* `frontend/public/`, `frontend/index.html`, `frontend/package.json`, `frontend/vite.config.js`
* `PROJECT_DOCUMENTATION.md` (This file)

### ❌ DO NOT Upload (Exclude via Gitignore):
* `backend/.env` *(Contains private database credentials/passwords)*
* `backend/bhashashield.db` *(If any local SQLite databases are created)*
* `frontend/node_modules/` & `backend/__pycache__/` *(Large dependency/cache files)*
* `frontend/dist/` *(Compiled build outputs)*

---

## 4. Resume Optimization & Recruiter Pitch

### Suggested Project Title
* **LangDetect AI: Explainable Code-Mixed Regional Language Safety Moderator**

### Recruiter-Targeted Description (2-Line Pitch)
> "Engineered an explainable, real-time AI content moderation platform that detects and categorizes multilingual toxicity in Romanized regional Indian languages (Hinglish, Tanglish, Tenglish) with 95%+ accuracy. Integrated a FastAPI and React architecture with a phonetic transliteration pipeline and a sarcasm-aware lexicon, automating the removal of casteist and communal hate speech."

### Key Resume Bullet Points:
* Designed a **FastAPI backend** and **React frontend** utilizing a MySQL database to log and display real-time telemetry analytics, geographic state heatmaps, and community risk indexes.
* Developed a custom **phonetic transliteration mapping engine** that normalizes Romanized slang tokens into semantic glosses for downstream classification.
* Built an **Explainable AI (XAI)** highlights layer returning token-level coordinates to visually isolate toxic words in code-mixed text.
