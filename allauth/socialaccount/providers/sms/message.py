from typing import List, Union
from django.conf import settings

class Message:
    def __init__(self, content: str, from_phone: str, to_phone: Union[str, List[str]]):
        self.content = content
        self.from_phone = from_phone
        self.to_phone = to_phone if isinstance(to_phone, list) else [to_phone]

    def send(self) -> bool:
        # Here you would integrate with your SMS provider
        # Example using Twilio:
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        success = True
        for phone in self.to_phone:
            try:
                message = client.messages.create(
                    body=self.content,
                    from_=self.from_phone,
                    to=phone
                )
            except Exception:
                success = False
                
        return success
