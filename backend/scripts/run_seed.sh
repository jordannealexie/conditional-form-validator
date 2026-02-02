#!/bin/bash

# Database seeding script runner
# This script helps initialize the database with users

echo "🌱 Database Seeding Script"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please create one with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env with your database settings!"
fi

# Run the unified, non-destructive seed script
echo "🚀 Running unified template seeder..."
echo ""

python scripts/seed_all_templates.py

echo ""
echo "✅ Seeding done!"
echo ""
echo "💡 Next steps:"
echo "   1. Start the API: uvicorn app.main:app --reload"
echo "   2. Access docs: http://localhost:8000/api/v1/docs"
