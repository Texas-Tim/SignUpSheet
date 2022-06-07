import json
import smtplib
import boto3
import csv
import logging
logger = logging.getLogger()
from botocore.exceptions import ClientError
import os
import time

# If necessary, replace us-east-1 with the AWS Region you're using for Amazon SES.
AWS_REGION = os.environ.get('REGION')
# ensure these table names are set correctly as environment variables
TABLE_REGISTER = os.environ.get('REGISTRATION_TABLE')
TABLE_TEAM = os.environ.get('TEAM_TABLE')
EVENT_ROOM_BUCKET = os.environ.get('EVENT_ROOM_BUCKET')
EVENT_ROOM_KEY = os.environ.get('EVENT_ROOM_KEY')

# Create a new DynamoDB resource and specify a region.
ddb_client = boto3.client('dynamodb',region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)



def createTeam(team_num, attendee_exp):
    """
    creates a new team with 0 members

    Variables:

    team_num:     [int] - team number
    attendee_exp: [int] - experience of the registree [0 - none, 1 - low, 2 - low_mid, 3 - medium, 4 - mid_high, 5 - high]
    """
    print("Creating Team " + str(team_num))

    key_exists = s3_client.list_objects_v2(Bucket=EVENT_ROOM_BUCKET, Prefix=EVENT_ROOM_KEY)['KeyCount']

    if key_exists:
        obj = s3_client.get_object(Bucket=EVENT_ROOM_BUCKET, Key=EVENT_ROOM_KEY)
        teams = obj['Body'].read().decode('utf-8').splitlines()
        if len(teams) > 0:

            #add new team to ddb
            try:
                response = ddb_client.put_item(
                    TableName = TABLE_TEAM,
                    Item={"Team":{"N":str(team_num)},
                    "Members":{"N":"0"},
                    "LowMembers":{"N":"0"},
                    "MidMembers":{"N":"0"},
                    "HighMembers":{"N":"0"},
                    "EventRoom": {"S": f"{teams[team_num-1]}"}
                    })

            except ClientError as err:
                logger.error(
                    "Couldn't update table")
                raise
            else:
                time.sleep(1)
                return updateTeam(team_num, attendee_exp)

def createTeamNoRoom(team_num, attendee_exp):
    """
    creates a new team with 0 members

    Variables:

    team_num:     [int] - team number
    attendee_exp: [int] - experience of the registree [0 - none, 1 - low, 2 - low_mid, 3 - medium, 4 - mid_high, 5 - high]
    """
    print("Creating Team " + str(team_num) + " With no Event Room Link")

    #add new team to ddb
    try:
        response = ddb_client.put_item(
            TableName = TABLE_TEAM,
            Item={"Team":{"N":str(team_num)},
            "Members":{"N":"0"},
            "LowMembers":{"N":"0"},
            "MidMembers":{"N":"0"},
            "HighMembers":{"N":"0"}
            })

    except ClientError as err:
        logger.error(
            "Couldn't update table")
        raise
    else:
        time.sleep(1)
        return updateTeam(team_num, attendee_exp)

def updateTeam(team_num, attendee_exp):
    """
    Updates the existing team member count

    Variables:

    team_num:     [int] - team number
    attendee_exp: [int] - experience of the registree [0 - none, 1 - low, 2 - low_mid, 3 - medium, 4 - mid_high, 5 - high]
    """
    print("Updating Team " + str(team_num))

    #update tables total team member count
    #update tables relative experience
    try:
        #Set the correct experience attribute
        exp_level = ""
        if attendee_exp <= 2:
            exp_level = "LowMembers"
        elif attendee_exp == 3:
            exp_level = "MidMembers"
        else:
            exp_level = "HighMembers"

        #increment the table information
        response = ddb_client.update_item(
            TableName = TABLE_TEAM,
            Key={'Team': {"N": str(team_num)}},
            UpdateExpression= f"set Members = Members + :i, {exp_level} = {exp_level} + :i",
            ExpressionAttributeValues={':i': {"N": "1"}},
            ReturnValues="ALL_NEW")

    except ClientError as err:
        logger.error(
            "Couldn't update table")
        raise
    else:
        return response['Attributes']

def addTeamMember(attendee, team, customer, firstName, fullName, email, location, role, experience, virtual, timeStamp):
    """
    Adds an attendee to the Game Day
    Variables

    attendee:    [int] - registree counter
    team:        [int] - team number
    customer:    [string] - customer's company Name
    firstName:   [string] - registree's first name
    fullName:    [string] - registree's full name
    email:       [string] - registree's email
    location:    [string] - location of the registree
    role:        [string] - job role of the registree
    experience:  [int] - experience level of the registree on a scale of 0-5 with 0 being none and 5 being expert
    virtual:     [bool]   - status of the registrees attendance in person or virtual (for hybrid events)
    timeStamp:   [string] - DateTime stamp of the registrees registration
    """
    print("Inserting team member into table: ", TABLE_REGISTER)

    try:
        response = ddb_client.put_item(
            TableName = TABLE_REGISTER,
            Item={
                'AttendeeID': {"N": str(attendee)},
                'Team': {"N": str(team)},
                'Company': {"S": customer},
                'FirstName': {"S": firstName},
                'FullName': {"S": fullName},
                'Email': {"S": email},
                'Location': {"S": location},
                'Role': {"S": role},
                'AWSExperience': {"N": str(experience)},
                'Virtual': {"BOOL": virtual},
                'TimeStamp': {"S": timeStamp}
                })
    except ClientError as err:
        logger = logging.getLogger()
        logger.error(
            "Couldn't add attendee " +
            str(attendee) + " to table " +
            TABLE_REGISTER + " ")
        raise
    else:
        return
