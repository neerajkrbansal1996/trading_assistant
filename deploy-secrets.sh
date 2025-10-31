#!/bin/bash
# Script to set Fly.io secrets from .env file
# Usage: ./deploy-secrets.sh

echo "Setting Fly.io secrets..."

fly secrets set TWILIO_ACCOUNT_SID=AC2184e9e831d4c4f6e14c5c91aa94db9e

fly secrets set TWILIO_AUTH_TOKEN=f82bd2c574cf871df4ce4629c91d9013

fly secrets set TWILIO_PHONE_NUMBER=+12185205925

fly secrets set YOUR_PHONE_NUMBER=+918947843932

fly secrets set TIMEZONE=Asia/Kolkata

echo "✅ All secrets have been set!"

