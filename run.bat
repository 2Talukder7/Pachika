@echo off

cd /d "%~dp0backend"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing/checking dependencies...
pip install -r requirements.txt -q

start "" http://127.0.0.1:5000

echo Starting Pachika...
python app.py

pause
