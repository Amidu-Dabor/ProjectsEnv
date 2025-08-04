# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

proxy_client = TwilioHttpClient(proxy={'http': os.environ['http_proxy'], 'https': os.environ['https_proxy']})
account_sid = os.environ['ACC_SID']
auth_token = os.environ['AUTH_TOKEN']

client = Client(account_sid, auth_token, http_client=proxy_client)

message = client.messages.create(
                     body="Hello Amid. I hope you're well; I'm just checking on you.",
                     from_='+16185912908',
                     to='+254795455796',
                    )

print(message.sid)
