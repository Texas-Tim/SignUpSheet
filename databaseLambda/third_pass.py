import json
import smtplib
import boto3
import logging
logger = logging.getLogger()
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
ddb_client = boto3.client('dynamodb',region_name=AWS_REGION)



def thirdPass(max_teams, teams, attendeeId, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp):
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
                addTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                #update Game Day team table metadata
                print("Updated team attributes ", updateTeam(team_num, awsExperience))
                notComplete = False
                return [True, team_num]

    if notComplete:

        #number of teams in the database
        size = ddb_client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
        team_num = 1

        if size == max_teams:
            print("no available teams! All teams are full!")
            return [False, team_num]
        else:
            print("no available teams! Creating new team")
            while team_num <= size+1:
                # check if team exists, if yes, increment team number (must be done this way in the case that event moderator created teams using the move participant team API)
                try:
                    check = ddb_client.get_item(TableName=TABLE_TEAM, Key={'Team': {'N': str(team_num)}})['Item']
                    team_num += 1

                # If team doesn't exist, continue as normal
                except KeyError:
                    print("New team attributes: ", createTeam(team_num, awsExperience))
                    addTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                    return [True, team_num]

    else:
        return [True, team_num]
