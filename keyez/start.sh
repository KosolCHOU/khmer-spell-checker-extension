#!/bin/bash
# Quick start script for KeyEZ Django server

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Run Django development server
python manage.py runserver
