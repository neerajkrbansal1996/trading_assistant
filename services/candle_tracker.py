from datetime import datetime
import pytz
from typing import Optional
import os

from services.phone_service import PhoneService
from services.candle_time import CandleTimeService


class CandleTracker:
    def __init__(self, phone_service: PhoneService):
        self.phone_service = phone_service
        self.candle_time = CandleTimeService()
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Kolkata'))
        
        # Track last checked candle times
        self.last_nse_candle_time: Optional[datetime] = None
        self.last_btc_candle_time: Optional[datetime] = None
        self.last_eth_candle_time: Optional[datetime] = None
    
    async def check_nse_candle_close(self):
        """
        Check if a 15-minute NSE candle has closed using time-based logic
        """
        try:
            current_time = self.candle_time.get_current_time()
            
            # Check if a candle has closed since last check
            has_closed, candle_close_time = self.candle_time.has_nse_candle_closed_since(
                self.last_nse_candle_time,
                current_time
            )
            
            if not has_closed or candle_close_time is None:
                return
            
            # Candle has closed
            print(f"✅ NSE 15-minute candle closed at {candle_close_time}")
            
            # Format message
            message = self.phone_service.format_candle_message(
                "NSE",
                "NSE"
            )
            
            # Make the call
            print(f"📞 Making call for NSE 15-minute candle close at {candle_close_time}")
            await self.phone_service.make_call(message)
            
            # Update last checked time
            self.last_nse_candle_time = candle_close_time
            
        except Exception as e:
            print(f"❌ Error checking NSE candle: {e}")
            import traceback
            traceback.print_exc()
    
    async def check_crypto_candle_close(self):
        """
        Check if a 4-hour crypto candle has closed for BTC and ETH using time-based logic
        """
        for symbol in ['BTC', 'ETH']:
            try:
                current_time = self.candle_time.get_current_time()
                
                # Get the appropriate last checked time
                last_checked = self.last_btc_candle_time if symbol == 'BTC' else self.last_eth_candle_time
                
                # Check if a candle has closed since last check
                has_closed, candle_close_time = self.candle_time.has_crypto_candle_closed_since(
                    last_checked,
                    current_time
                )
                
                if not has_closed or candle_close_time is None:
                    continue
                
                # Candle has closed
                print(f"✅ {symbol} 4-hour candle closed at {candle_close_time}")
                
                # Format message
                message = self.phone_service.format_candle_message(
                    "Crypto",
                    symbol
                )
                
                # Make the call
                print(f"📞 Making call for {symbol} 4-hour candle close at {candle_close_time}")
                await self.phone_service.make_call(message)
                
                # Update last checked time
                if symbol == 'BTC':
                    self.last_btc_candle_time = candle_close_time
                else:
                    self.last_eth_candle_time = candle_close_time
                    
            except Exception as e:
                print(f"❌ Error checking {symbol} candle: {e}")
                import traceback
                traceback.print_exc()
