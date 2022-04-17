# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# SMS Message to 911


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="You get no b*****s",
                     from_='+19853045873',
                     to='+15714356878'
                 )

print(message.sid)



