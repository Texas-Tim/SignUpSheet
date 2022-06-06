import json
import smtplib
import boto3
import os
import logging
from botocore.exceptions import ClientError

# The character encoding for the email.
CHARSET = "UTF-8"

AWS_REGION = os.environ.get('REGION')
# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=AWS_REGION)

# This address must be verified with Amazon SES.
SENDER = os.environ.get('SENDER')

def send_email(recipient, subject, body_html, body_text):
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        return(e.response['Error']['Message'])
    else:
        print("Email sent!"),
        return(response['ResponseMetadata'])
