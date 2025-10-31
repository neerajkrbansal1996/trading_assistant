from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import pytz
from datetime import datetime, timedelta
from typing import Optional
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.phone_service import PhoneService
from services.candle_tracker import CandleTracker

# Load environment variables
load_dotenv()

# Initialize services
phone_service = PhoneService()
candle_tracker = CandleTracker(phone_service)

# Scheduler
scheduler = AsyncIOScheduler(timezone=pytz.timezone(os.getenv('TIMEZONE', 'Asia/Kolkata')))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler
    scheduler.start()
    
    # Schedule NSE 15-minute candle checks (every minute, will check if candle closed)
    scheduler.add_job(
        candle_tracker.check_nse_candle_close,
        trigger=CronTrigger(second=0),  # Every minute at 0 seconds
        id='nse_15min_check',
        replace_existing=True
    )
    
    # Schedule Crypto 4-hour candle checks (every minute, will check if candle closed)
    scheduler.add_job(
        candle_tracker.check_crypto_candle_close,
        trigger=CronTrigger(second=0),  # Every minute at 0 seconds
        id='crypto_4h_check',
        replace_existing=True
    )
    
    print("🚀 Candle tracking service started!")
    print("📊 Monitoring NSE 15-minute candles")
    print("🪙 Monitoring Crypto 4-hour candles (BTC, ETH)")
    
    yield
    
    # Shutdown: Stop scheduler
    scheduler.shutdown()


app = FastAPI(
    title="Trading Assistant API",
    description="API for tracking candle closes and making phone calls",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Trading Assistant API is running",
        "status": "active",
        "features": {
            "nse_15min_candles": "Tracking 15-minute candle closes for NSE",
            "crypto_4h_candles": "Tracking 4-hour candle closes for BTC and ETH"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/test-call")
async def test_call():
    """Test endpoint to verify phone service is working"""
    try:
        result = await phone_service.make_call("Test call from Trading Assistant")
        return {"success": True, "message": "Call initiated", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/next-candle-times")
async def get_next_candle_times():
    """Get the next expected candle close times"""
    try:
        from services.candle_time import CandleTimeService
        candle_time = CandleTimeService()
        current_time = candle_time.get_current_time()
        
        next_nse = candle_time.get_next_nse_15min_candle_close_time(current_time)
        next_btc = candle_time.get_next_crypto_4h_candle_close_time(current_time)
        next_eth = candle_time.get_next_crypto_4h_candle_close_time(current_time)
        
        return {
            "success": True,
            "current_time": current_time.isoformat(),
            "next_nse_15min": next_nse.isoformat() if next_nse else None,
            "next_btc_4h": next_btc.isoformat() if next_btc else None,
            "next_eth_4h": next_eth.isoformat() if next_eth else None,
            "nse_market_open": candle_time.is_nse_market_open(current_time)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

