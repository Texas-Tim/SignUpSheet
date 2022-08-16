import json
import smtplib
import boto3
import logging
logger = logging.getLogger()
from botocore.exceptions import ClientError
import os
from functions import createNewTeam
from functions import updateTeamTable
from functions import registerTeamMember

# If necessary, replace us-east-1 with the AWS Region you're using for Amazon SES.
AWS_REGION = os.environ.get('REGION')
TEAM_SIZE = os.environ.get('TEAM_SIZE')
TABLE_TEAM = os.environ.get('TEAM_TABLE')

# Create a new DynamoDB resource and specify a region.
ddb_client = boto3.client('dynamodb',region_name=AWS_REGION)



def firstPass(max_teams, teams, attendeeId, customer, hash_l, room_list, firstName, fullName, language, role, awsExperience, virtual, timeStamp, l_flag):
    #added a comment
    #Check for any flags
    if l_flag:
        return firstLanguagePass(max_teams, teams, attendeeId, customer, hash_l, room_list, firstName, fullName, language, role, awsExperience, virtual, timeStamp)


    print("Performing the first pass")
    #Scan each team
    notComplete = True
    team_num = 0
    for t in teams:
        #check existing teams first
        # print("Team: ", t['Team']['N'])
        if notComplete:
            #If team is full, do not add
            num_members = int(t['Members']['N'])
            high_exp = int(t['HighMembers']['N'])
            mid_exp = int(t['MidMembers']['N'])
            low_exp = int(t['LowMembers']['N'])
            team_num = int(t['Team']['N'])
            # print("NotComplete: ", notComplete)
            if num_members < int(TEAM_SIZE):
                #If user is highly experienced >= 4 (0,1,2,3,4,5)
                # print("NumMembers: ", num_members)
                if awsExperience >= 4:
                    #Then check if team has 1 highly experienced player
                    if int(high_exp) == 0:
                        #if no, then add to team
                        registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                        notComplete = False
                        return [True, team_num]

                #else if user has middle experience = 3
                elif awsExperience == 3:
                    #Then check if team has 2 middle experienced players
                    if int(mid_exp) < 2:
                        #if no, then add to team
                        registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                        notComplete = False
                        return [True, team_num]

                #else user has < 2 experience
                else:
                    #check if team has 2 low experience players
                    # print("AWSExperience:", awsExperience)
                    if int(low_exp) < 2:
                        #if no, then add to team
                        registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                        #update Game Day team table metadata
                        print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                        notComplete = False
                        return [True, team_num]

    if notComplete:

        #number of teams in the database
        size = ddb_client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
        team_num = 1

        print("Max Teams: ", max_teams)
        print("Size: ", size)
        if size >= max_teams:
            print("no available teams! All teams are full!")
            return [False, 0]
        else:
            print("no available teams! Creating new team")
            while team_num <= size+1 or size == 0:
                # check if team exists, if yes, increment team number (must be done this way in the case that event moderator created teams using the move participant team API)
                # print("Size: ", size)
                try:
                    check = ddb_client.get_item(TableName=TABLE_TEAM, Key={'Team': {'N': str(team_num)}})['Item']
                    # print("Check: ", check)
                    team_num += 1

                # If team doesn't exist, continue as normal
                except KeyError:
                    EEHash = hash_l[int(team_num)-1]
                    print("New team attributes: ", createNewTeam(team_num, awsExperience, EEHash, room_list, language))
                    registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                    return [True, team_num]

    else:
        return [True, team_num]

def firstLanguagePass(max_teams, teams, attendeeId, customer, hash_l, room_list, firstName, fullName, language, role, awsExperience, virtual, timeStamp):
    print("Performing the first language pass")
    #Scan each team
    notComplete = True
    team_num = 0
    for t in teams:
        #check existing teams first
        # print("Team: ", t['Team']['N'])
        if notComplete:
            #If team is full, do not add
            num_members = int(t['Members']['N'])
            high_exp = int(t['HighMembers']['N'])
            mid_exp = int(t['MidMembers']['N'])
            low_exp = int(t['LowMembers']['N'])
            team_num = int(t['Team']['N'])
            # print("NotComplete: ", notComplete)
            if num_members < int(TEAM_SIZE):
                #Check language gap
                if t['Language']['S'] == language:
                    #If user is highly experienced >= 4 (0,1,2,3,4,5)
                    if awsExperience >= 4:
                        #Then check if team has at least 1 highly experienced player
                        if int(high_exp) == 0:
                            #if no, then add to team
                            registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                            #update Game Day team table metadata
                            print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                            notComplete = False
                            return [True, team_num]
                    #else if user has middle experience = 3
                    elif awsExperience == 3:
                        #Then check if team has 2 middle experienced players
                        if int(mid_exp) < 2:
                            #if no, then add to team
                            registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                            #update Game Day team table metadata
                            print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                            notComplete = False
                            return [True, team_num]
                    #else user has < 2 experience
                    else:
                        #check if team has 2 low experience players
                        # print("AWSExperience:", awsExperience)
                        if int(low_exp) < 2:
                            #if no, then check language
                            registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                            #update Game Day team table metadata
                            print("Updated team attributes ", updateTeamTable(team_num, awsExperience))
                            notComplete = False
                            return [True, team_num]

    if notComplete:

        #number of teams in the database
        size = ddb_client.scan(TableName=TABLE_TEAM, ConsistentRead=True)['Count'] #ConsistentRead ensures the latest table information
        team_num = 1

        print("Max Teams: ", max_teams)
        print("Size: ", size)
        if size >= max_teams:
            print("no available teams! All teams are full!")
            return [False, 0]
        else:
            print("no available teams! Creating new team")
            while team_num <= size+1 or size == 0:
                # check if team exists, if yes, increment team number (must be done this way in the case that event moderator created teams using the move participant team API)
                # print("Size: ", size)
                try:
                    check = ddb_client.get_item(TableName=TABLE_TEAM, Key={'Team': {'N': str(team_num)}})['Item']
                    # print("Check: ", check)
                    team_num += 1

                # If team doesn't exist, continue as normal
                except KeyError:
                    EEHash = hash_l[int(team_num)-1]
                    print("New team attributes: ", createNewTeam(team_num, attendee_exp, EEHash, room_list, language))
                    registerTeamMember(attendeeId, team_num, customer, firstName, fullName, language, role, awsExperience, virtual, timeStamp)
                    return [True, team_num]

    else:
        return [True, team_num]
