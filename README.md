# Trading Assistant API

A FastAPI server that monitors candle closes for NSE (Indian Stock Market) and Crypto markets (BTC, ETH) and automatically calls your phone number when candles close.

## Features

- 📊 **NSE Market Monitoring**: Tracks 15-minute candle closes for Indian NSE market
- 🪙 **Crypto Market Monitoring**: Tracks 4-hour candle closes for BTC and ETH
- 📞 **Phone Notifications**: Automatically calls your phone when candles close
- ⏰ **Automated Scheduling**: Runs continuously, checking for candle closes every minute

## Prerequisites

- Python 3.8 or higher
- Twilio account (for phone calls)
- Internet connection for market data

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number
YOUR_PHONE_NUMBER=+1234567890    # Your phone number (E.164 format)
TIMEZONE=Asia/Kolkata             # Your timezone
```

### 4. Get Twilio Credentials

1. Sign up for a [Twilio account](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a Twilio phone number (or use trial number for testing)
4. For production, you may need to verify your phone number in Twilio

### 5. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Root
```
GET /
```

### Test Phone Call
```
POST /test-call
```
Test if the phone service is working correctly.

### Get Last NSE Candle
```
GET /last-nse-candle
```

### Get Last Crypto Candle
```
GET /last-crypto-candle?symbol=BTC
GET /last-crypto-candle?symbol=ETH
```

### Get Next Candle Times
```
GET /next-candle-times
```
Returns the next expected candle close times for debugging and verification.

## How It Works

1. **Time-Based Detection**: Uses deterministic time logic to detect candle closes:
   - **NSE 15-minute candles**: Close at predictable times (9:15, 9:30, 9:45, 10:00, ..., 15:30 IST) during market hours (9:15 AM - 3:30 PM IST, weekdays only)
   - **Crypto 4-hour candles**: Close at predictable times (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 IST - Asia/Kolkata timezone)
2. **Scheduler**: The application uses APScheduler to check for candle closes every minute
3. **Phone Calls**: When a candle close is detected, automatically calls your phone with notification

## Notes

- **Time-Based Logic**: The system uses deterministic time calculations to detect candle closes, making it efficient and reliable
- **NSE Market Hours**: Only monitors during market hours (9:15 AM - 3:30 PM IST) on weekdays
- **Crypto Markets**: Crypto markets run 24/7, so 4-hour candles are monitored continuously using Asia/Kolkata timezone
- **No External Data Required**: The system works purely based on time logic, no market data APIs needed
- The application runs continuously once started
- Phone calls are made using Twilio's Voice API
- Candle detection checks run every minute, but calls are only made when a candle actually closes based on time logic
- Make sure your Twilio account has sufficient credits for phone calls
- For production use, consider adding error handling, logging, and monitoring

## Troubleshooting

1. **No calls received**: 
   - Verify Twilio credentials in `.env`
   - Check Twilio account balance
   - Verify phone numbers are in E.164 format (+country code + number)

2. **No market data**:
   - Check internet connection
   - Verify NSE symbol is correct
   - For crypto, ensure Binance API is accessible

3. **Import errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

## Deployment to Fly.io

### Prerequisites

1. Install [Fly CLI](https://fly.io/docs/getting-started/installing-flyctl/)
2. Sign up for a [Fly.io account](https://fly.io/app/sign-up)

### Deploy Steps

1. **Login to Fly.io**:
   ```bash
   fly auth login
   ```

2. **Set up secrets** (environment variables):
   ```bash
   fly secrets set TWILIO_ACCOUNT_SID=your_twilio_account_sid
   fly secrets set TWILIO_AUTH_TOKEN=your_twilio_auth_token
   fly secrets set TWILIO_PHONE_NUMBER=+1234567890
   fly secrets set YOUR_PHONE_NUMBER=+1234567890
   fly secrets set TIMEZONE=Asia/Kolkata
   ```

3. **Deploy the application**:
   ```bash
   fly deploy
   ```

4. **Check status**:
   ```bash
   fly status
   ```

5. **View logs**:
   ```bash
   fly logs
   ```

The application will be available at `https://trading-assistant.fly.dev` (or your custom domain).

### Configuration

- The `fly.toml` file is configured to:
  - Run in Mumbai region (`bom`) for better latency with Asia/Kolkata timezone
  - Use 512MB RAM and 1 shared CPU
  - Auto-start machines and keep at least 1 running
  - Health check on `/health` endpoint

## License

MIT

