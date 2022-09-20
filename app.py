from flask import Flask, request
from twilio.rest import Client
import os
from twilio.twiml.messaging_response import MessagingResponse
from apscheduler.schedulers.blocking import BlockingScheduler

from flask_pymongo import PyMongo

import setup

sched = BlockingScheduler()
mongo = PyMongo()
app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb+srv://jdnicoll1:mongo@cluster0.dj2jkov.mongodb.net/jacobdb?retryWrites=true&w=majority"
mongo = PyMongo(app)
verse_collection = mongo.db.messaging




@sched.scheduled_job('interval', hours=2)
def send_verse():
    verse_dict = {"2 Corinthians 5:21" : "For our sake he made him to be sin who knew no sin, so that in him we might become the righteousness of God", 
                "1 Thessalonians 5:16-18" : "Rejoice always, pray without ceasing, give thanks in all circumstances; for this is the will of God in Christ Jesus for you.", 
                "1 Peter 1:13" : "Therefore, preparing your minds for action, and being sober-minded, set your hope fully on the grace that will be brought to you at the revelation of Jesus Christ.", 
                "Ezekiel 36:26" : "And I will give you a new heart, and a new spirit I will put within you. And I will remove the heart of stone from your flesh and give you a heart of flesh.",
                "Proverbs 3:5-6" : "Trust in the LORD with all your heart, And lean not on your own understanding; In all your ways acknowledge Him, And He shall direct your paths.",
                "Mark 10:45" : "For even the Son of Man did not come to be served, but to serve, and to give His life a ransom for many.",
                "Romans 8:32" : "He who did not spare His own Son, but delivered Him up for us all, how shall He not with Him also freely give us all things?"
    }

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']

   
    

    client = Client(account_sid, auth_token)
    verse_num = 2

    message = client.messages.create(
        from_=messaging_service_sid,
        to='+13092654472',
        body= list(verse_dict)[verse_num] + ": " + list(verse_dict.values())[verse_num],
        # schedule_type='fixed',
        # send_at=send_when.isoformat() + 'Z',
    )

    print(message.sid)



@app.route('/', methods=['GET', 'POST'])
def sms_reply(): 

    #handle initial incoming message 
    #if(request.method == 'POST')
    #make a call to the database and see if number is already in system 
    #if in database
        #check what they are messaging about 

    #if not in database
    number = request.form['From']
    message_body = request.form['Body']
    resp = MessagingResponse()
    response_message = 'Hello {}, You said: {}'.format(number, message_body)
    resp.message(response_message)

   
    verse_collection.insert_one({'text': "yo", 'complete': 'yes'})

    
    



    #if number is not in the system - send the intro message
    # else if(None):
    #     response_message = ('Welcome to The Message!! To sign up send a text with your name')

    #if user is in system, read what the message is 

    #if menu - show menu, menu can be a separate class once we have all the info 
        #subset of menu - they will send a number, need to be able to handle each of the numbers
        
    #if verse_response - determine if we sent a verse and if it matches the response 

    # if STOP - stop sending messages 
    # user_setup = setup.Setup_User("Jacob", "2")
    

    

    return str(resp)

    

if __name__ == "__main__":
    sched.start()
    app.run()
