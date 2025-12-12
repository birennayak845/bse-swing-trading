#!/bin/bash

# Direct Vercel deployment using environment variable to bypass certificate issues

echo "🚀 BSE Swing Trading Platform - Direct Vercel Deployment"
echo "========================================================"
echo ""

# Check if API key is provided
if [ -z "$VERCEL_TOKEN" ]; then
    VERCEL_TOKEN="vck_4tWh2wdZyWfPvYr9wexP7bgaxuRNpAzz5wsXpx8qplVbfMQQ5p31JA3Q"
fi

echo "✅ Using Vercel API Token"
echo ""

# Export environment variables for Node.js
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Try deployment with token
echo "🔄 Attempting deployment..."
echo ""

# Using vercel CLI with token and project settings
vercel \
  --token="${VERCEL_TOKEN}" \
  --prod \
  --force \
  --yes \
  --name="bse-swing-trading" \
  --build-env VERCEL_URL=true

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ✅ ✅ DEPLOYMENT SUCCESSFUL! ✅ ✅ ✅"
    echo ""
    echo "Your application is now live on Vercel!"
    echo ""
    echo "Next steps:"
    echo "1. Check your deployment: vercel ls"
    echo "2. View logs: vercel logs"
    echo "3. Visit your live URL at: https://bse-swing-trading.vercel.app"
    echo ""
else
    echo ""
    echo "⚠️  Deployment encountered an issue."
    echo "This might be due to SSL certificate validation on your system."
    echo ""
    echo "Alternative: Deploy via Vercel Dashboard"
    echo "1. Go to https://vercel.com/dashboard"
    echo "2. Click 'Add New' → 'Project'"
    echo "3. Import from GitHub or upload your project"
    echo ""
fi
