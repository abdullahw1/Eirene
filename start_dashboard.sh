#!/bin/bash

echo "🌿 Starting Project Eirene Dashboard..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Start the dashboard
PYTHONPATH=. python dashboard.py
