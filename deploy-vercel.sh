#!/bin/bash

# BSE Swing Trading Platform - Vercel Deployment Script
# This script automates the deployment to Vercel

set -e

echo "🚀 BSE Swing Trading Platform - Vercel Deployment"
echo "=================================================="
echo ""

# Check if in correct directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Make sure you're in the swing_trading_app directory."
    exit 1
fi

echo "✅ Project directory verified"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git config user.email "admin@bse-swing-trading.dev"
    git config user.name "BSE Swing Trading Admin"
    git add .
    git commit -m "Initial commit: BSE Swing Trading Platform"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Committing changes..."
    git add .
    git commit -m "Update: Deployment updates" || true
fi

echo ""
echo "🔑 Checking for Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
    echo "✅ Vercel CLI installed"
else
    echo "✅ Vercel CLI found"
fi

echo ""
echo "🚀 Deploying to Vercel..."
echo "=================================================="
echo ""

if [ -n "$VERCEL_TOKEN" ]; then
    echo "Using Vercel API key from environment..."
    vercel --token "$VERCEL_TOKEN"
else
    echo "No API key provided. Using interactive deployment..."
    echo ""
    echo "You will be prompted to:"
    echo "1. Authorize Vercel (if needed)"
    echo "2. Select or create a project"
    echo "3. Confirm deployment settings"
    echo ""
    read -p "Press enter to continue..."
    vercel
fi

echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo ""
echo "📊 Your app is now live on Vercel!"
echo ""
echo "💡 Next steps:"
echo "1. Check your deployment: vercel logs"
echo "2. Visit your dashboard at the provided URL"
echo "3. Test the API endpoints"
echo "4. Share with team members!"
echo ""
echo "📖 For more info, see VERCEL_DEPLOYMENT.md"
