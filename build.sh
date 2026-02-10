#!/bin/bash
# Build script for Railway deployment
# Installs Python deps, builds React frontend, then starts the server

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
cd web && npm install

echo "🔨 Building React frontend..."
npm run build

echo "✅ Build complete! Frontend at web/dist/"
cd ..
