import json
import smtplib
import boto3
import logging
from botocore.exceptions import ClientError
import os
from functions import createTeam
from functions import updateTeam
from functions import addTeamMember

# If necessary, replace us-east-1 with the AWS Region you're using for Amazon SES.
AWS_REGION = os.environ.get('REGION')
TEAM_SIZE = os.environ.get('TEAM_SIZE')
TABLE_TEAM = os.environ.get('TEAM_TABLE')

# Create a new DynamoDB resource and specify a region.
client = boto3.client('dynamodb',region_name=AWS_REGION)


def thirdPass(max_team_size, teams, attendee, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp):
    print("Performing the third pass")
    #Scan each team
    notComplete = True
    team_num = 0
    for t in teams:
        #check existing teams first
        if notComplete:
            #If team is full, do not add
            num_members = int(t['Members']['N'])
            high_exp = int(t['HighMembers']['N'])
            mid_exp = int(t['MidMembers']['N'])
            low_exp = int(t['LowMembers']['N'])
            team_num = int(t['Team']['N'])
            #is team full?
            if num_members < int(TEAM_SIZE):
                addTeamMember(attendee, team_num, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp)
                #update Game Day team table metadata
                print("Updated team attributes ", updateTeam(team_num, awsExperience))
                notComplete = False
                return True

    if notComplete:
        team_count = client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
        team_num = team_count+1
        if team_num > max_teams:
            print("no available teams! All teams are full!")
            return False
        else:
            print("no available teams! Creating new team")
            print("New team attributes: ", createTeam(team_num, awsExperience))
            addTeamMember(attendee, team_num, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp)
            return True
    else:
        return True
