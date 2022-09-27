from email import message
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
sched = BlockingScheduler(timezone="America/Chicago")

#initialize database
app.config['MONGO_URI'] = os.environ['MONGO_URI']
mongo = PyMongo(app)
verse_collection = mongo.db.messaging


@sched.scheduled_job('cron', hour='9,12,15,18,21')
def send_verse():

    #twilio init
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']
    client = Client(account_sid, auth_token)

    #get all numbers that want daily texts and send them their current daily text verse
    docs = verse_collection.find()
    format_verse = ""
    for user_profile in docs: 
        if(user_profile["on_text_chain"] == True):
            #send daily verse to users on text chain
            obj = user_profile["daily_verse"]
            for x in obj:
                format_verse = x + ": " + obj[x]
            user_number = user_profile["phone_number"]
            message = client.messages.create(
                from_=messaging_service_sid,
                to=user_number, #need a list of all users signed up to recieve service
                body= format_verse
            )
    
    print(message.sid)



@app.route('/', methods=['GET', 'POST'])
def sms_reply(): 

    #incoming message 
    number = request.form['From']
    message_body = request.form['Body']
    resp = MessagingResponse()
    
    #initial message when signing up
    verse_init = {"1 Thessalonians 5:16-18" : "Rejoice always, pray without ceasing, give thanks in all circumstances; for this is the will of God in Christ Jesus for you."}
    if(verse_collection.count_documents({"phone_number": number}) == 0): #user is not in system yet and we need to add their number
        verse_collection.insert_one({'phone_number': number, 'name': message_body, 'daily_verse': verse_init, 'verses': verse_init, 'on_text_chain': True}) #add user to the database
        response_message = 'Welcome to The Message!\n\nPaul says in Philippians 4:8: "Finally, brothers and sisters, whatever is true, whatever is noble, whatever is right, whatever is pure, whatever is lovely, whatever is admirable — if anything is excellent or praiseworthy—think about such things."\n\nIt is for this reason that this app was created... to learn more about God\'s Word and help set our thoughts on it consistently.\n\nBy signing up for the service you will receive a message every three hours. The verse will change every week or you can choose one yourself by texting MENU , which also has other options as well. Enjoy!!'
        

    else: #user is already in system 
        #parse what the user sent
        #check to see if incoming message is new verse - we will know this by whether or not an equals sign is present 
        split_verse = message_body.split('=')
        message_body.strip() #get rid of any uninteded whitespace
        if(len(split_verse) == 2):
            user_doc = verse_collection.find_one({"phone_number": number})
            user_obj = user_doc["verses"] #get verses specific user has
            user_obj[split_verse[0].strip()] = split_verse[1].strip()
            verse_collection.update_one({"phone_number": number}, {"$set": {"verses": user_obj}})
            response_message = "{} added to my verses".format(split_verse[0])
        elif(message_body == "MENU"):
            response_message = print_menu()
        elif(message_body == "STOP"):
            verse_collection.update_one({"phone_number": number}, {"$set": {"on_text_chain": False}})
            response_message = "You will no longer receive any messages, to resume your account type START" 
        elif(message_body == "START"):
            verse_collection.update_one({"phone_number": number}, {"$set": {"on_text_chain": True}})
            response_message = "Welcome back, type MENU to see options."
        elif(message_body == "1"):
            doc = verse_collection.find_one({"phone_number" : number})
            obj = doc["verses"]
            for x in obj:
                format_verse = x + ": " + obj[x] + "\n\n"
                response_message += format_verse
        elif(message_body == "2"):
            response_message = "Stats still being constructed"
        elif(message_body == "3"):
            admin_doc = verse_collection.find_one({"name": "admin"})
            user_doc = verse_collection.find_one({"phone_number": number})
            admin_obj = admin_doc["verses"] #get all verses in database
            user_obj = user_doc["verses"] #get verses specific user has
            #go through all available verses, the first one that isn't in the user verses we add 
            for admin_verse_reference in admin_obj: 
                if(admin_verse_reference not in user_obj):
                    user_obj[admin_verse_reference] = admin_obj[admin_verse_reference]
                    verse_collection.update_one({"phone_number": number}, {"$set": {"verses": user_obj}})
                    response_message = "{} added to my verses".format(admin_verse_reference)
                    break
        elif(message_body == "4"):
            response_message = "To add a custom verse, send a text with the verse reference and the verse content separated by an equals sign. For example:\n\nJohn 11:35 = Jesus Wept."
            #need to check if front part of text is a book in the Bible, if it is, then it will be a custom verse
            #split string on equals at this point
            #put a new verse in user's verses
        else:
            response_message = "Couldn't understand request, please try again"


    #response_message = 'Hello {}, You said: {}'.format(number, message_body) #send intial response 
    resp.message(response_message)
    return str(resp)

    

if __name__ == "__main__":
    sched.start()
    app.run()
