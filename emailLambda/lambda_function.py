import json
import smtplib
import boto3
import os
import logging
from botocore.exceptions import ClientError
from sendEmail import send_email


eventRoom = os.environ.get('MAIN_CONFERENCE_ROOM')

print('Loading function')


def lambda_handler(event, context):
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
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
    EEHash = 'https://aws.amazon.com/ses/'
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
