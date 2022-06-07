import json
import smtplib
import boto3
import os
import logging
from botocore.exceptions import ClientError
from sendEmail import send_email


eventRoom = os.environ.get('MAIN_CONFERENCE_ROOM')
EVENT_ROOM_BUCKET = os.environ.get('EVENT_ROOM_BUCKET')
EVENT_ROOM_KEY = os.environ.get('EVENT_ROOM_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

s3_client = boto3.client('s3', region_name=AWS_REGION)
print('Loading function')


def lambda_handler(event, context):
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.

    key_exists = s3_client.list_objects_v2(Bucket=EVENT_ROOM_BUCKET, Prefix=EVENT_ROOM_KEY)['KeyCount']

    if key_exists:
        obj = s3_client.get_object(Bucket=EVENT_ROOM_BUCKET, Key=EVENT_ROOM_KEY)
        teams = obj['Body'].read().decode('utf-8').splitlines()

        if len(teams) > 0:
          sendEmailWithLink(event, teams)
        else:
          sendEmailWithoutLink(event)
    else:
      sendEmailWithoutLink(event)






def sendEmailWithLink(event, teams):
    recipient = event["Records"][0]['dynamodb']['NewImage']["Email"]["S"]
    team = event["Records"][0]['dynamodb']['Keys']["Team"]["N"]
    name = event["Records"][0]['dynamodb']['NewImage']["FirstName"]["S"]

    # The subject line for the email.
    subject = "Team" + team + " Game Day Info"

    # The email body for recipients with non-HTML email clients.
    body_text = ("Hello " + name + "! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:"
                 "Main Chime room"
                 "Team EE Hash"
                )


    #Pull this value from a ddb table eventually
    EEHash = teams[int(team)-1]
    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Hello {name}! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:</h1>
      <p>
        Main Event Room: <a href={eventRoom}>Event Room</a>
        <br>
        <br>
        Provided AWS Account: <a href={EEHash}>Team EE Hash</a>
      </p>
    </body>
    </html>
                """
    return send_email(recipient, subject, body_html, body_text)


def sendEmailWithoutLink(event):
    recipient = event["Records"][0]['dynamodb']['NewImage']["Email"]["S"]
    team = event["Records"][0]['dynamodb']['Keys']["Team"]["N"]
    name = event["Records"][0]['dynamodb']['NewImage']["FirstName"]["S"]

    # The subject line for the email.
    subject = "Team" + team + " Game Day Info"

    # The email body for recipients with non-HTML email clients.
    body_text = ("Hello " + name + "! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:"
                 "Main Chime room"

                )

    # The HTML body of the email.
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Hello {name}! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:</h1>
      <p>
        Main Event Room: <a href={eventRoom}>Event Room</a>
      </p>
    </body>
    </html>
                """
    return send_email(recipient, subject, body_html, body_text)
