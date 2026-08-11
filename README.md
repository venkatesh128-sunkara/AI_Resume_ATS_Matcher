# AI Resume ATS Analyzer

Python + NLP + LLM resume matching and scoring tool. Upload a resume (PDF/DOCX/TXT),
paste a job description, and get a detailed ATS score with keyword/skill matching,
formatting checks, tailored suggestions, and optional LLM-powered feedback.

![theme](https://img.shields.io/badge/Streamlit-1.38-FF4B4B)
![python](https://img.shields.io/badge/Python-3.11-3776AB)

## Features

- **Resume parsing** for PDF, DOCX, and TXT files
- **NLP analysis**: NLTK noun-phrase keyword extraction, TF-IDF semantic similarity (scikit-learn)
- **ATS scoring** across 8 weighted dimensions: contact info, section structure, keyword match,
  skills match, experience, education, ATS formatting, semantic similarity
- **Skill matching** against a built-in database of 20+ skill categories (programming languages,
  cloud/DevOps, data science, etc.)
- **Smart suggestions** to improve your resume
- **Optional LLM feedback** via any OpenAI-compatible API (OpenAI, OpenRouter, local Ollama...)
- Animated light-gradient UI and downloadable analysis report

## Quick Start

```bash
cd resume-ats
pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows you can also double-click `run.bat`.

Then open your browser at `http://localhost:8501`.

## Usage

1. Upload your resume (PDF, DOCX, or TXT)
2. Paste the job description
3. Click **Analyze Resume**
4. Optionally add an OpenAI API key in the sidebar for AI feedback

## Deploy on Render (free)

1. Push this repo to GitHub.
2. Go to https://dashboard.render.com and sign up / log in.
3. Click **New** > **Blueprint**.
4. Connect your GitHub account and select this repository.
5. Render reads `render.yaml`, creates the web service, and deploys automatically.
6. Open the `https://<service>.onrender.com` URL that Render shows.

Notes:
- Free-tier services spin down after inactivity and wake up again on the first visit (takes ~30s).
- `setup.sh` installs dependencies and downloads NLTK data during the build.
- The app listens on `$PORT` provided by Render (default 10000 locally via `.streamlit/config.toml`).

## Project Structure

```
resume-ats/
├── app.py                  # Streamlit web app (gradient UI + animations)
├── run.bat                 # Windows one-click launcher
├── render.yaml             # Render blueprint for free deployment
├── setup.sh                # Render build script (deps + NLTK data)
├── requirements.txt
├── analyzer/
│   ├── parser.py           # PDF/DOCX/TXT text extraction
│   ├── nlp.py              # tokenization, keywords, skill mention detection
│   ├── scorer.py           # ATS matching & scoring engine
│   ├── llm.py              # OpenAI-compatible LLM analysis
│   └── skills_data.py      # skill database, education levels, section headings
├── .streamlit/config.toml  # server config
└── sample/                 # sample resume + job description
```

## Scoring Weights

| Category          | Weight |
|-------------------|--------|
| Keyword Match     | 25     |
| Skills Match      | 25     |
| Experience        | 15     |
| Section Structure | 10     |
| Education         | 10     |
| ATS Formatting    | 10     |
| Contact Info      | 5      |
| Semantic Similarity | up to 10 bonus |

## LLM Setup (optional)

The rule-based analysis works with no API key. For AI feedback, set a key in the
sidebar or via the `OPENAI_API_KEY` environment variable. Any OpenAI-compatible
endpoint works - set a custom Base URL (e.g. `https://openrouter.ai/api/v1`) and
model name (e.g. `openai/gpt-4o-mini`).
