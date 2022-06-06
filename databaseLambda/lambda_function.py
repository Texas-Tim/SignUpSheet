import json
import smtplib
import boto3
import logging
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


# Create a new DynamoDB resource and specify a region.
client = boto3.client('dynamodb',region_name=AWS_REGION)

print('Loading function')


def lambda_handler(event, context):

    count = client.scan(TableName=TABLE_REGISTER, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
    attendee = count+1
    print(event)
    print(context)
    team_distribution_round = 1
    max_teams = math.ceil(MAX_TEAMS*0.5)


    try:
        #Built in logic: fill up the first half of of teams first, then add 25% more teams, then open up all teams (might provide even more rounds in the future)
        #Not everyone shows up and we want to limit the first 50% of teams to fill up first. To add additional rounds, simply change the logic so that max teams is a percentage
        #of the inputted Max Teams

        #Determine Distribution Round
        while math.ceil(attendee/TEAM_SIZE) > max_teams:
            print("Attendee: ", attendee)
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
        return team_registration(event, attendee, max_teams)


    except ClientError as err:
        logger.error(
            f"Couldn't update table {TABLE_REGISTER}",
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    #all teams are full or all passes failed
    else:
        print("Failure! Something is wrong with the code!")
        return 'Something wrong occurred in the code. All Teams are full or all passes failed'


def team_registration(event, attendee, max_teams):

    #Grab the information from Sign up sheet
    firstName = event["firstName"]
    lastName = event["lastName"]
    recipient = event["email"]
    location = event["location"]
    role = event["jobFunction"]
    awsExperience = int(event["experience"])
    print(f"registree has {awsExperience} experience")
    timeStamp = event["optTimestamp"]
    virtual = bool(event["virtual"])
    customer = event["customer"]





    #initialize some useful variables
    fullName = firstName + " " + lastName
    teams = client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Items']

    #firstPass, strict team requirements
    if firstPass(max_teams, teams, attendee, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp):
        print("first Pass Success!")
        return 'Successfully added attendee {} to the event.'.format(event['firstName'])

    #secondPass, avoids all low experience teams
    elif secondPass(max_teams, teams, attendee, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp):
        print("second pass Success!")
        return 'Successfully added attendee {} to the event.'.format(event['firstName'])

    #finalPass, just fill the teams
    elif thirdPass(max_teams, teams, attendee, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp):
            print("third pass Success!")
            return 'Successfully added attendee {} to the event.'.format(event['firstName'])
    else:
        print("Code not working, should not reach this text!")
        return "Failed"
