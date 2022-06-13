import json
import boto3
import logging
logger = logging.getLogger()
from botocore.exceptions import ClientError
import os
from functions import createTeam
from functions import createTeamNoRoom
from functions import createParticipant
from functions import deleteParticipant
from functions import incrementTeam
from functions import decrementTeam

# If necessary, replace us-east-1 with the AWS Region you're using for Amazon SES.
AWS_REGION = os.environ.get('REGION')
# ensure these table names are set correctly as environment variables
TABLE_REGISTER = os.environ.get('REGISTRATION_TABLE')
TABLE_TEAM = os.environ.get('TEAM_TABLE')

MAX_TEAMS = int(os.environ.get('MAX_NUM_TEAMS'))

# Create a new DynamoDB resource and specify a region.

ddb_client = boto3.client('dynamodb', region_name=AWS_REGION)

def lambda_handler(event, context):


    attendeeId = event['id']
    oldTeamId = event['currentTeam']
    newTeamId = event['newTeam']
    if oldTeamId == newTeamId:
        print("Error, same team")
        return "Old team input and New team input are the same. Please submit a new team to move the participant to"

    try:
        #  Confirm participant exists and is assigned to the indicated team
        participantData = ddb_client.get_item(TableName=TABLE_REGISTER, Key={'AttendeeID': {'N': attendeeId}, 'Team': {'N': oldTeamId}})['Item']

        #Gather relevant participant data
        customer = participantData['Company']['S']
        firstName = participantData['FirstName']['S']
        fullName = participantData['FullName']['S']
        email = participantData['Email']['S']
        location = participantData['Location']['S']
        role = participantData['Role']['S']
        attendee_exp = participantData['AWSExperience']['N']
        virtual = participantData['Virtual']['BOOL']
        timeStamp = event['optTimestamp']

        #  If new team exists, add participant to team, if team does not currently exist, create team in table
        try:
            participantTeamData = ddb_client.get_item(TableName=TABLE_TEAM, Key={'Team': {'N': newTeamId}})['Item']

            # no error thrown means team exists. Continue as normal.
            #  Delete the participants information from the table
            deleteParticipant(attendeeId, oldTeamId)

            #  Deprecate the number in the old teams stats
            decrementTeam(int(oldTeamId), int(attendee_exp))

            #  Create the participants information from the table
            createParticipant(attendeeId, newTeamId, customer, firstName, fullName, email, location, role, attendee_exp, virtual, timeStamp)

            #  Deprecate the number in the old teams stats
            incrementTeam(int(newTeamId), int(attendee_exp))

        except KeyError:
            # error thrown means team doesn't exist. Create new team
            # Check if new team number is outside of max team size
            if int(newTeamId) > MAX_TEAMS:
                print("Error! Team should not be created, input outside of Event parameters")
                return f"Please input a team number <= {MAX_TEAMS}"
            else:
                #  Delete the participants information from the table
                deleteParticipant(attendeeId, oldTeamId)

                #  Deprecate the number in the old teams stats
                decrementTeam(int(oldTeamId), int(attendee_exp))

                #  Create the participants information from the table
                createParticipant(attendeeId, newTeamId, customer, firstName, fullName, email, location, role, attendee_exp, virtual, timeStamp)

                #  Create the new team and update team info
                createTeam(int(newTeamId), int(attendee_exp))



        """
        return a success code
        """
        print("Successfully updated new teams. Sending email to participant with new team information")
        return "Successfully updated new teams. Sending email to participant with new team information"


    except KeyError:
        print("Failure to change participant teams. No such participant on that team or team doesn't exist")
        return "Incorrect Participant Info. Please submit the correct AttendeeID and Team Number"
