#!/bin/bash

cd "$(dirname "$0")/backend" || exit 1

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing/checking dependencies..."
pip install -r requirements.txt -q

python app.py &
FLASK_PID=$!

sleep 2
( open http://127.0.0.1:5000 2>/dev/null || xdg-open http://127.0.0.1:5000 2>/dev/null ) 

echo "Pachika is running. Press Ctrl+C to stop."
wait $FLASK_PID
