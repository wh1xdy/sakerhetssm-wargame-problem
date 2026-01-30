import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from aiosmtpd.smtp import SMTP

class NoLimitSMTP(SMTP):
    def _validate_line_length(self, line):
        return line

class CustomHandler(Message):
    async def handle_message(self, message):
        print("Received mail:")
        print(message)
        
if __name__ == "__main__":
     handler = CustomHandler()
     controller = Controller(handler, hostname="0.0.0.0", port=1025)
     controller.start()
     print("SMTP server started on port 1025")
     try:
     	asyncio.get_event_loop().run_forever()
     except:
     	controller.stop()
