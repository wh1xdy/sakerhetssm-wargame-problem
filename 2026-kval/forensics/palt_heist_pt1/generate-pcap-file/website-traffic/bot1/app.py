import smtplib
import time
from email.message import EmailMessage

SMTP_HOST = "smtp"
SMTP_PORT = 1025

USER = "hugh@great-ai-creations"

def send_mail():
    to_addr = "paltoverflow@paltoverflow.com"
    from_addr = "hugh@amazing-ai-creations.ctf"
    subject = "Re: Re: Re: Re: Re: Re: Re: An exiting oppertunity!"
    body = "Hi PaltOverflow,\r\n\r\nYour Pitepalt Image Review Bot is ready to go! 🎉\r\n\r\n⚡ Instant 1–100 ratings\r\n\r\n🎯 Focused scoring with bilinear downscaling\r\n\r\n💻 Fully integrated and smooth on your site\r\n\r\nGive it a try, share with your users, and watch the engagement roll in! 😄\r\n\r\nBest,\r\nHugh Man, Sales Person for Amazing AI Creations"
    
    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.set_content(body, charset="utf-8", cte="8bit")
    
    # Send email
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.send_message(msg)
    except Exception as e:
        print("error")

if __name__ == "__main__":
    time.sleep(5)
    send_mail()
