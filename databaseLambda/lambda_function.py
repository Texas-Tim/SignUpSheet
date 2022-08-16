import json
import smtplib
import boto3
import logging
logger = logging.getLogger()
from botocore.exceptions import ClientError
import os
import math
from first_pass import firstPass
from second_pass import secondPass
from third_pass import thirdPass


# If necessary, replace us-east-1 with the AWS Region you're using for Amazon SES.
AWS_REGION = os.environ.get('REGION')
TEAM_SIZE = int(os.environ.get('TEAM_SIZE'))
MAX_TEAMS = int(os.environ.get('MAX_NUM_TEAMS'))

# ensure these table names are set correctly as environment variables
TABLE_REGISTER = os.environ.get('REGISTRATION_TABLE')
TABLE_TEAM = os.environ.get('TEAM_TABLE')

EVENT_ROOM_BUCKET = os.environ.get('EVENT_ROOM_BUCKET')
EVENT_ROOM_KEY = os.environ.get('EVENT_ROOM_KEY')
HASH_LIST_BUCKET = os.environ.get('HASH_LIST_BUCKET')
HASH_LIST_KEY = os.environ.get('HASH_LIST_KEY')

MAIN_CONFERENCE_ROOM = os.environ.get('MAIN_CONFERENCE_ROOM')


# Create a new DynamoDB resource and specify a region.
ddb_client = boto3.client('dynamodb', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)

print('Loading function')


def lambda_handler(event, context):

    count = ddb_client.scan(TableName=TABLE_REGISTER, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
    attendeeId = count+1
    team_distribution_round = 1
    max_teams = math.ceil(MAX_TEAMS*0.5)


    try:
        #Built in logic: fill up the first half of of teams first, then add 25% more teams, then open up all teams (might provide even more rounds in the future)
        #Not everyone shows up and we want to limit the first 50% of teams to fill up first. To add additional rounds, simply change the logic so that max teams is a percentage
        #of the inputted Max Teams

        #Determine Distribution Round
        print("Attendee: ", attendeeId)
        while math.ceil(attendeeId/TEAM_SIZE) > max_teams:
            if team_distribution_round == 1:
                team_distribution_round += 1
                max_teams = math.ceil(MAX_TEAMS*0.75)
            elif team_distribution_round == 2:
                team_distribution_round +=1
                max_teams = MAX_TEAMS
            else:
                return 'All teams are full, failed to add attendee {} to the event.'.format(event['firstName'])
        #attempt to find a team, using less strict rules each pass
        print(f"Team distribution round: {team_distribution_round}")

        #Run up to three passes over the databases
        result, team_num = team_registration(event, attendeeId, max_teams)

        #Start pulling hash data from s3 table
        key_exists = s3_client.list_objects_v2(Bucket=HASH_LIST_BUCKET, Prefix=HASH_LIST_KEY)['KeyCount']
        EEHash = None
        if key_exists:
            #normalize the table information and sort by table number
            hash_index = 5
            obj = s3_client.get_object(Bucket=HASH_LIST_BUCKET, Key=HASH_LIST_KEY)
            hash_ = obj['Body'].read().decode('utf-8').splitlines()
            for i, h in enumerate(hash_):
                hash_[i] = h.split(",")
            if hash_[0][0] == 'game-id':
                hash_.pop(0)
            if len(hash_) > 0:
                hash_.sort(key=lambda hashes: int(hashes[3]))
                #remove everything but the hash url
                for i, h in enumerate(hash_):
                    hash_[i] = h[hash_index]
                #assign the event room hash
                EEHash = hash_[int(team_num)-1]


        #Start pulling room data from s3 table
        key_exists = s3_client.list_objects_v2(Bucket=EVENT_ROOM_BUCKET, Prefix=EVENT_ROOM_KEY)['KeyCount']
        room = None
        if key_exists:
            obj = s3_client.get_object(Bucket=EVENT_ROOM_BUCKET, Key=EVENT_ROOM_KEY)
            event_rooms = obj['Body'].read().decode('utf-8').splitlines()

            if len(event_rooms) > 0:
                room = event_rooms[int(team_num)-1]


        json = {
            "result": result,
            "team": team_num,
            "hash": EEHash,
            "team_room": room,
            "main_room": MAIN_CONFERENCE_ROOM,
            "attendee": attendeeId
        }
        return json





    except ClientError as err:
        logger.error(
            f"Couldn't update table {TABLE_REGISTER}")
        raise
    #all teams are full or all passes failed
    else:
        print("Failure! Something is wrong with the code!")
        return 'Something wrong occurred in the code. All Teams are full or all passes failed'


def team_registration(event, attendeeId, max_teams):

    #Grab the information from Sign up sheet
    firstName = event["firstName"]
    lastName = event["lastName"]
    customer = event["customer"]
    role = event["jobFunction"]
    awsExperience = int(event["experience"])
    print(f"registree has {awsExperience} experience")
    language = event["language"]
    timeStamp = event["optTimestamp"]
    virtual = bool(event["virtual"])


    #initialize some useful variables
    fullName = firstName + " " + lastName
    teams = ddb_client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Items']
    response = firstPass(max_teams, teams, attendeeId, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)

    #firstPass, strict team requirements
    if response[0]:
        print("first Pass Success!")
        return ['Successfully added attendee {} to the event.'.format(event['firstName']), response[1]]

    response = secondPass(max_teams, teams, attendeeId, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
    #secondPass, avoids all low experience teams
    if response[0]:
        print("second pass Success!")
        return ['Successfully added attendee {} to the event.'.format(event['firstName']), response[1]]

    response = thirdPass(max_teams, teams, attendeeId, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
    if response[0]:
    #finalPass, just fill the teams
        print("third pass Success!")
        return ['Successfully added attendee {} to the event.'.format(event['firstName']), response[1]]
    else:
        print("Code not working, should not reach this text!")
        return "Failed"
