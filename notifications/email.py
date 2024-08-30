from django.core import mail
from django.template.loader import  render_to_string
import threading
import os

class  EmailThread(threading.Thread):
    def __init__(self, subject, from_email, reciever, plain_message,  html_message):
        threading.Thread.__init__(self)
        self.subject = subject
        self.from_email = from_email
        self.reciever = reciever
        self.plain_message = plain_message
        self.html_message = html_message


    def run(self):
        mail.send_mail(
            subject=self.subject,
            from_email= self.from_email,
            recipient_list= [self.reciever],
            message=str(self.plain_message),
            html_message=self.html_message,
        )


class Email:

    def __init__(
            self,
            subject: str= "Ecommerce",
            reciever: str = "",
            plain_message: str = "",
            template: str = "",
            data = {}
    ) -> None:
        self.subject = subject
        self.reciever = reciever
        self.from_email = "From <abdullateefyusuf80@gmail.com>"
        self.plain_message = plain_message
        self.template = template
        self.data = data

    def send(self):
        try:
            html_message = render_to_string(f"{self.template}", self.data)
            EmailThread(
                self.subject,
                self.from_email,      
                self.reciever,        
                self.plain_message,   
                html_message       
            ).start()
        except Exception as e:
            print(f"Error sending email: {e}")