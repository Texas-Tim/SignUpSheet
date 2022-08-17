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
MAX_TEAMS = int(os.environ.get('MAX_NUM_TEAMS'))

# Create a new DynamoDB resource and specify a region.
ddb_client = boto3.client('dynamodb',region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)

#Conference Room, Hash, list of x flags

def createNewTeam(team_num, awsExperience, EEHash, room_list, language):
    """
    creates a new team with 0 members

    Variables:

    team_num:     [int] - team number
    awsExperience: [int] - experience of the registree [0 - none, 1 - low, 2 - low_mid, 3 - medium, 4 - mid_high, 5 - high]
    """
    ddb_dict = {
        "Team":{"N":str(team_num)},
        "Hash": {"S": EEHash},
        "Members":{"N":"0"},
        "LowMembers":{"N":"0"},
        "MidMembers":{"N":"0"},
        "HighMembers":{"N":"0"},
        "Language": {"S": language}
    }
    #Grab the Event Room if applicable
    if len(room_list) > 0:
        ddb_dict["EventRoom"] = {"S": f"{room_list[team_num-1]}"}

    try:
        if team_num > MAX_TEAMS:
            raise Exception("team number is out of bounds")

        print("Creating Team " + str(team_num))
        #add new team to ddb
        try:
            response = ddb_client.put_item(
                TableName = TABLE_TEAM,
                Item=ddb_dict)

        except ClientError as err:
            logger.error(
                "Couldn't update table")
            raise
        else:
            time.sleep(1)
            return updateTeam(team_num, awsExperience)

    except:
        return False

def updateTeamTable(team_num, awsExperience):
    """
    Updates the existing team member count

    Variables:

    team_num:     [int] - team number
    awsExperience: [int] - experience of the registree [0 - none, 1 - low, 2 - low_mid, 3 - medium, 4 - mid_high, 5 - high]
    """
    print("Updating Team " + str(team_num))

    #update tables total team member count
    #update tables relative experience
    try:
        #Set the correct experience attribute
        exp_level = ""
        if awsExperience <= 2:
            exp_level = "LowMembers"
        elif awsExperience == 3:
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

def registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp):
    """
    Adds an attendee to the Game Day
    Variables

    attendee:    [int] - registree counter
    team:        [int] - team number
    customer:    [string] - customer's company Name
    firstName:   [string] - registree's first name
    fullName:    [string] - registree's full name
    language:    [string] - registree's preferred language
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
                'AttendeeID': {"N": str(attendeeId)},
                'Team': {"N": str(team_num)},
                'Company': {"S": customer},
                'FirstName': {"S": firstName},
                'FullName': {"S": fullName},
                'Language': {"S": language},
                'Role': {"S": role},
                'AWSExperience': {"N": str(awsExperience)},
                'Virtual': {"BOOL": virtual},
                'TimeStamp': {"S": timeStamp}
                })['ResponseMetadata']
    except ClientError as err:
        logger = logging.getLogger()
        logger.error(
            "Couldn't add attendee " +
            str(attendee) + " to table " +
            TABLE_REGISTER + " ")
        raise
    else:
        return response
