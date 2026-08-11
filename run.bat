@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting AI Resume ATS Analyzer...
python -m streamlit run app.py
pause
