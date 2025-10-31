import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say
from typing import Dict


class PhoneService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.your_phone = os.getenv('YOUR_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.twilio_phone, self.your_phone]):
            raise ValueError(
                "Missing Twilio configuration. Please set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, and YOUR_PHONE_NUMBER in .env file"
            )
        
        self.client = Client(self.account_sid, self.auth_token)
    
    async def make_call(self, message: str) -> Dict:
        """
        Make a phone call using Twilio
        """
        try:
            # Create TwiML for the call
            response = VoiceResponse()
            response.say(message, voice='alice', language='en-US')
            
            # For production, you'd need a webhook URL that returns TwiML
            # For now, we'll use a simpler approach with a message
            # You'll need to set up a webhook endpoint or use Twilio's Twiml Bin
            
            # Use Twilio to call and speak directly
            # Escape message for XML/TwiML
            import html
            escaped_message = html.escape(message)
            call = self.client.calls.create(
                twiml=f'<Response><Say voice="alice">{escaped_message}</Say></Response>',
                to=self.your_phone,
                from_=self.twilio_phone
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "message": "Call initiated successfully"
            }
        except Exception as e:
            print(f"Error making call: {e}")
            raise
    
    def format_candle_message(self, market: str, symbol: str) -> str:
        """
        Format a simple notification message for candle close
        """
        return f"{market} {symbol} candle closed. Check your trading platform for details."
