#!/bin/bash
# Script to setup Fly.io project
# Usage: ./setup-fly.sh

echo "🚀 Setting up Fly.io project..."

# Step 1: Login to Fly.io (if not already logged in)
echo "📝 Step 1: Checking Fly.io login..."
fly auth whoami || fly auth login

# Step 2: Launch the app (this will create the app if it doesn't exist)
echo ""
echo "📝 Step 2: Launching app (this creates the app if it doesn't exist)..."
echo "⚠️  When prompted, you can:"
echo "   - Enter a name for the app (or press Enter to use 'trading-assistant')"
echo "   - Choose 'No' for PostgreSQL (we don't need it)"
echo "   - Choose 'No' for Redis (we don't need it)"
echo ""
fly launch --no-deploy

# Step 3: Set secrets
echo ""
echo "📝 Step 3: Setting secrets..."
fly secrets set TWILIO_ACCOUNT_SID=AC2184e9e831d4c4f6e14c5c91aa94db9e
fly secrets set TWILIO_AUTH_TOKEN=f82bd2c574cf871df4ce4629c91d9013
fly secrets set TWILIO_PHONE_NUMBER=+12185205925
fly secrets set YOUR_PHONE_NUMBER=+918947843932
fly secrets set TIMEZONE=Asia/Kolkata

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Review the app configuration in fly.toml"
echo "   2. Deploy the app: fly deploy"
echo "   3. Check status: fly status"
echo "   4. View logs: fly logs"

