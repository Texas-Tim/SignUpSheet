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


def secondPass(max_team_size, teams, attendee, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp):
    print("Performing the second pass")
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
            if num_members < int(TEAM_SIZE):
                #If user is highly experienced >= 4 (0,1,2,3,4,5)
                if awsExperience >= 4:
                    #Then check if team has 2 highly experienced players
                    if int(high_exp) < 2:
                        #if no, then add to team
                        addTeamMember(attendee, team_num, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeam(team_num, awsExperience))
                        notComplete = False
                        return True

                #else if user has middle experience = 3
                elif awsExperience == 3:
                    #Then check if team has 3 middle experienced players
                    if int(mid_exp) < 3:
                        #if no, then add to team
                        addTeamMember(attendee, team_num, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeam(team_num, awsExperience))
                        notComplete = False
                        return True

                #else user has < 2 experience
                else:
                    #check if team has 3 low experienced players
                    if int(low_exp) < 3:
                        #if no, then add to team
                        addTeamMember(attendee, team_num, customer, firstName, fullName, recipient, location, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeam(team_num, awsExperience))
                        notComplete = False
                        return True

    if notComplete:
        team_count = ddb_client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
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
