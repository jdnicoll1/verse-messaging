from flask import Flask
import os
from twilio.rest import Client

app = Flask(__name__)

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages.create(
                              body='Hi there',
                              from_='+19793254225',
                              to='+13092654472'
                          )

print(message.sid)

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()