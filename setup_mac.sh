#!/bin/bash
set -e

echo "=============================================="
echo "Setting up Game Platform API on macOS/Linux..."
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
    echo "[1/5] Creating virtual environment (env)..."
    python3 -m venv env
else
    echo "[1/5] Virtual environment already exists."
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "[3/5] Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run migrations
echo "[4/5] Running database migrations..."
python manage.py migrate

# Seed sample data and superuser
echo "[5/5] Seeding sample data and admin account..."
python manage.py seed_data

echo "=============================================="
echo "Setup complete! Starting server..."
echo "Admin Login: admin / admin123"
echo "Root API:    http://127.0.0.1:8000/"
echo "Admin:       http://127.0.0.1:8000/admin/"
echo "=============================================="
python manage.py runserver
