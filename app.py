from flask import Flask, request
from twilio.rest import Client
import os
from twilio.twiml.messaging_response import MessagingResponse
from apscheduler.schedulers.blocking import BlockingScheduler

from flask_pymongo import PyMongo

from menu import *

#initialize flask application
app = Flask(__name__)

#initialize scheduler for periodic texts
sched = BlockingScheduler()

#initialize database
app.config['MONGO_URI'] = os.environ['MONGO_URI']
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
        to='+13092654472', #need a list of all users signed up to recieve service
        body= list(verse_dict)[verse_num] + ": " + list(verse_dict.values())[verse_num], #will come from specific verse in database for a user
        # schedule_type='fixed',
        # send_at=send_when.isoformat() + 'Z',
    )

    print(message.sid)



@app.route('/', methods=['GET', 'POST'])
def sms_reply(): 

    #incoming message 
    number = request.form['From']
    message_body = request.form['Body']
    resp = MessagingResponse()
    
    #initial message without signing up
    if(verse_collection.count_documents({"phone_number": number}) == 0): #user is not in system yet and we need to add their number
        verse_collection.insert_one({'phone_number': number, 'name': message_body, 'verses': {"John 11:35" : "Jesus wept.", "test_verse": "ya boi"}}) #add user to the database
        response_message = 'Welcome to The Message!\n\nPaul says in Philippians 4:8: "Finally, brothers and sisters, whatever is true, whatever is noble, whatever is right, whatever is pure, whatever is lovely, whatever is admirable — if anything is excellent or praiseworthy—think about such things."\n\nIt is for this reason that this app was created... to learn more about God\'s Word and help set our thoughts on it consistently.\n\nBy signing up for the service you will receive a message every three hours. The verse will change every week or you can choose one yourself by texting MENU , which also has other options as well. Enjoy!!'
        resp.message(response_message)

    else: #user is already in system 
        #parse what the user sent
        if(message_body == "MENU"):
            response_message = print_menu()
            resp.message(response_message)
        elif(message_body == "STOP"):
            response_message = "You will no longer receive any messages, to resume your account type START"
            resp.message(response_message)
        elif(message_body == "1"):
            doc = verse_collection.find_one({"phone_number" : number})
            obj = doc["verses"]
            response_message = ""
            for x in obj:
                thing = x + ": " + obj[x] + "\n\n"
                response_message += thing
                print(thing)

            
            
        
    #response_message = 'Hello {}, You said: {}'.format(number, message_body) #send intial response 
    
    return str(resp)

    

if __name__ == "__main__":
    sched.start()
    app.run()
