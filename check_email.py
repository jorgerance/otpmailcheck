#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import imaplib
import email
from email.header import decode_header
import os
import base64
import html2text
import re
import requests
import json
import pandas as pd
import time
import sys
import datetime
import pytz
import configparser


import configparser
import time

config_file = "{}/{}".format(os.path.dirname(os.path.realpath(__file__)), 'config.ini')

config = configparser.ConfigParser()
config.read(config_file)


# account credentials
username = config['credentials']['OTP_EMAIL_USER']
password = config['credentials']['OTP_EMAIL_PASS']

print(username)

email_archive = "emails.json"


def todays_date(seconds=True):
    today = datetime.datetime.now(pytz.timezone('Europe/Madrid'))
    today_str = today.strftime("%d/%m/%Y - %H:%M")
    if seconds:
        today_str = today.strftime("%d/%m/%Y - %H:%M:%S.%f")[:-3]
    return(today_str)

def animated_loading():
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r'+'Running...'+char)
        time.sleep(.1)
        sys.stdout.flush()



def fetch_previous_emails(file=email_archive):
    id_list = []
    try:
        df = pd.read_json(file)
        for email_id in df['id']:
            if email_id not in id_list:
                id_list.append(email_id)
    except:
        pass

    return(id_list)


def save_email(data):
    a = []
    if not os.path.isfile(email_archive):
        a.append(data)
        with open(email_archive, mode='w') as f:
            f.write(json.dumps(a, indent=4))
    else:
        with open(email_archive) as feedsjson:
            feeds = json.load(feedsjson)

        feeds.append(data)
        with open(email_archive, mode='w') as f:
            f.write(json.dumps(feeds, indent=4))

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)



def send_pushover(message='testing', title='Binance Email OTP', priority='1', sound='intermission'):
    app_token = config['credentials']['PUSHOVER_APP_TOKEN']
    user_token = config['credentials']['PUSHOVER_USER_TOKEN']
    r = requests.post("https://api.pushover.net/1/messages.json", data={"token":app_token,"user":user_token,"message":message, "title": title, "priority": priority, "sound": sound})

    return r.status_code


def run():

  # create an IMAP4 class with SSL
  imap = imaplib.IMAP4_SSL(config['credentials']['OTP_IMAP_SERVER'])
  # authenticate
  imap.login(username, password)


  status, messages = imap.select("INBOX")
  # number of top emails to fetch
  N = 3
  # total number of emails
  messages = int(messages[0])


  for i in range(messages, messages-N, -1):
      # fetch the email message by ID
      res, msg = imap.fetch(str(i), "(RFC822)")
      for response in msg:
          if isinstance(response, tuple):
              # parse a bytes email into a message object
              msg = email.message_from_bytes(response[1])

              # decode the email subject
              subject, encoding = decode_header(msg["Subject"])[0]
              if isinstance(subject, bytes):
                  # if it's a bytes, decode to str
                  subject = subject.decode(encoding)

              # decode email sender
              From, encoding = decode_header(msg.get("From"))[0]
              if isinstance(From, bytes):
                  From = From.decode(encoding)

              # decode email sender
              Date, encoding = decode_header(msg.get("Date"))[0]
              if isinstance(Date, bytes):
                  Date = Date.decode(encoding)

              Message_id, encoding = decode_header(msg.get("Message-ID"))[0]
              if isinstance(Message_id, bytes):
                  Message_id = Message_id.decode(encoding)

              rich_body = msg.get_payload()

              try:
                body = html2text.html2text(base64.urlsafe_b64decode(rich_body.replace('-_', '+/').encode('ASCII')).decode())
              except:
                body = ""
                pass

              for line in body.splitlines():

                otps = re.findall(r'^\d{6,6}\s', line)

                if len(otps) == 1 and 'erification code' in body:

                  otp = otps[0]

                  data = {
                    'subject': subject,
                    'from': From,
                    'date': Date,
                    'id': Message_id,
                    'otp': otp
                  }

                  previous_emails_list = fetch_previous_emails()

                  if Message_id not in previous_emails_list:
                    for k,v in data.items():
                      print(k,v)
                    save_email(data)
                    send_pushover(message=otp)

                  break

  # close the connection and logout
  imap.close()
  imap.logout()


if __name__ == "__main__":

  print('Running...')

  while True:
    run()


    time.sleep(7)
    print(todays_date())