from datetime import datetime, time, timedelta
import pytz
from typing import Optional, Tuple
import os


class CandleTimeService:
    """
    Service to determine candle closing times based on deterministic time logic
    """
    
    def __init__(self):
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Kolkata'))
        self.utc = pytz.UTC
    
    def get_current_time(self) -> datetime:
        """Get current time in configured timezone"""
        return datetime.now(self.timezone)
    
    def is_weekday(self, dt: datetime) -> bool:
        """Check if the date is a weekday (Monday=0, Sunday=6)"""
        return dt.weekday() < 5
    
    def get_nse_market_hours(self, dt: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get NSE market opening and closing times for a given date
        NSE hours: 9:15 AM to 3:30 PM IST
        """
        if not self.is_weekday(dt):
            return None, None
        
        market_open = dt.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = dt.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open, market_close
    
    def is_nse_market_open(self, dt: Optional[datetime] = None) -> bool:
        """Check if NSE market is currently open"""
        if dt is None:
            dt = self.get_current_time()
        
        if not self.is_weekday(dt):
            return False
        
        market_open, market_close = self.get_nse_market_hours(dt)
        
        if market_open is None:
            return False
        
        return market_open <= dt <= market_close
    
    def get_nse_15min_candle_close_time(self, dt: datetime) -> Optional[datetime]:
        """
        Get the 15-minute candle close time for NSE
        Candles close at: 9:15, 9:30, 9:45, 10:00, ..., 15:15, 15:30
        """
        if not self.is_nse_market_open(dt):
            return None
        
        # Round down to the nearest 15-minute mark
        minute = (dt.minute // 15) * 15
        candle_close = dt.replace(second=0, microsecond=0, minute=minute)
        
        # Check if we're past the market close
        _, market_close = self.get_nse_market_hours(dt)
        if candle_close > market_close:
            return None
        
        return candle_close
    
    def get_next_nse_15min_candle_close_time(self, dt: Optional[datetime] = None) -> Optional[datetime]:
        """Get the next 15-minute candle close time for NSE"""
        if dt is None:
            dt = self.get_current_time()
        
        # Get current candle close time
        current_candle = self.get_nse_15min_candle_close_time(dt)
        
        if current_candle is None:
            # Market is closed, get next market day's first candle
            next_day = dt + timedelta(days=1)
            next_day = next_day.replace(hour=9, minute=15, second=0, microsecond=0)
            
            # Skip weekends
            while not self.is_weekday(next_day):
                next_day += timedelta(days=1)
            
            return next_day
        
        # Add 15 minutes to get next candle
        next_candle = current_candle + timedelta(minutes=15)
        
        # Check if within market hours
        if self.is_nse_market_open(next_candle):
            return next_candle
        
        return None
    
    def get_crypto_4h_candle_close_time(self, dt: Optional[datetime] = None, use_utc: bool = True) -> Optional[datetime]:
        """
        Get the 4-hour candle close time for crypto
        Crypto 4h candles close at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (UTC)
        """
        if dt is None:
            dt = self.get_current_time()
        
        if use_utc:
            # Convert to UTC for crypto
            if dt.tzinfo is None:
                dt = self.timezone.localize(dt)
            dt_utc = dt.astimezone(self.utc)
        else:
            dt_utc = dt
        
        # Round down to the nearest 4-hour mark
        hour = (dt_utc.hour // 4) * 4
        candle_close = dt_utc.replace(minute=0, second=0, microsecond=0, hour=hour)
        
        return candle_close
    
    def get_next_crypto_4h_candle_close_time(self, dt: Optional[datetime] = None, use_utc: bool = True) -> Optional[datetime]:
        """Get the next 4-hour candle close time for crypto"""
        if dt is None:
            dt = self.get_current_time()
        
        current_candle = self.get_crypto_4h_candle_close_time(dt, use_utc)
        
        if current_candle is None:
            return None
        
        # Add 4 hours to get next candle
        next_candle = current_candle + timedelta(hours=4)
        
        return next_candle
    
    def has_nse_candle_closed_since(self, last_check: Optional[datetime], current_time: Optional[datetime] = None) -> Tuple[bool, Optional[datetime]]:
        """
        Check if an NSE 15-minute candle has closed since last check
        Returns: (has_closed, candle_close_time)
        """
        if current_time is None:
            current_time = self.get_current_time()
        
        if last_check is None:
            # First check - get current candle if market is open
            current_candle = self.get_nse_15min_candle_close_time(current_time)
            if current_candle and current_candle <= current_time:
                return True, current_candle
            return False, None
        
        # Get the candle close time that would be after last_check
        last_candle = self.get_nse_15min_candle_close_time(last_check)
        next_candle = self.get_next_nse_15min_candle_close_time(last_check)
        
        if next_candle is None:
            return False, None
        
        # Check if we've passed the next candle close time
        if current_time >= next_candle:
            return True, next_candle
        
        return False, None
    
    def has_crypto_candle_closed_since(self, last_check: Optional[datetime], current_time: Optional[datetime] = None) -> Tuple[bool, Optional[datetime]]:
        """
        Check if a crypto 4-hour candle has closed since last check
        Returns: (has_closed, candle_close_time)
        """
        if current_time is None:
            current_time = self.get_current_time()
        
        if last_check is None:
            # First check - get current candle
            current_candle = self.get_crypto_4h_candle_close_time(current_time)
            if current_candle and current_candle <= current_time:
                return True, current_candle
            return False, None
        
        # Convert last_check to UTC for comparison
        if last_check.tzinfo is None:
            last_check = self.timezone.localize(last_check)
        last_check_utc = last_check.astimezone(self.utc)
        
        # Get the next 4-hour candle after last_check
        next_candle_utc = self.get_next_crypto_4h_candle_close_time(last_check_utc, use_utc=True)
        
        if next_candle_utc is None:
            return False, None
        
        # Convert current_time to UTC for comparison
        if current_time.tzinfo is None:
            current_time = self.timezone.localize(current_time)
        current_time_utc = current_time.astimezone(self.utc)
        
        # Check if we've passed the next candle close time
        if current_time_utc >= next_candle_utc:
            return True, next_candle_utc.astimezone(self.timezone)
        
        return False, None

