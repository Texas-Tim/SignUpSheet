import boto3
import os
import json
import cfnresponse

SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET')
DESTINATION_BUCKET = os.environ.get('DESTINATION_BUCKET')

API_GATEWAY_FIRST_ENDPOINT = os.environ.get('API_GATEWAY_FIRST')
API_GATEWAY_SECOND_ENDPOINT = os.environ.get('API_GATEWAY_SECOND')
l_flag = eval(os.environ.get('LANGUAGE_FLAG'))

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Create a reusable Paginator
    paginator = s3_client.get_paginator('list_objects_v2')

    # Create a PageIterator from the Paginator

    request_type = event.get('RequestType', False)
    result = {}

    if request_type == 'Create':
        # Loop through each object, looking for ones older than a given time period
        page_iterator = paginator.paginate(Bucket=SOURCE_BUCKET)
        for page in page_iterator:
            for object in page['Contents']:
                try:
                    key = object['Key']

                    if key == "js/formHandler.js":
                        print(f"re-writing {key}")

                        #replace Api Endpoint in backend
                        response = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=key)
                        data = response['Body'].read().decode('utf-8')
                        data = data.replace("Api_Gateway_Endpoint", API_GATEWAY_FIRST_ENDPOINT)
                        if l_flag:
                            data = data.replace("$('#languageid').prop('hidden', 'l_flag');", "$('#languageid').prop('hidden', false);")
                            data = data.replace("$('#languagelabel').prop('hidden', 'l_flag');", "$('#languagelabel').prop('hidden', false);")
                        else:
                            data = data.replace("$('#languageid').prop('hidden', 'l_flag');", "$('#languageid').prop('hidden', true);")
                            data = data.replace("$('#languagelabel').prop('hidden', 'l_flag');", "$('#languagelabel').prop('hidden', true);")
                        result = s3_client.put_object(
                            Body=data,
                            Bucket=DESTINATION_BUCKET,
                            Key=key)['ResponseMetadata']
                    elif key == "js/updateParticipant.js":
                        print(f"re-writing {key}")

                        #replace Api Endpoint in backend
                        response = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=key)
                        data = response['Body'].read().decode('utf-8')
                        data = data.replace("Api_Gateway_Endpoint", API_GATEWAY_SECOND_ENDPOINT)
                        result = s3_client.put_object(
                            Body=data,
                            Bucket=DESTINATION_BUCKET,
                            Key=key)['ResponseMetadata']
                    else:
                        print(f"Moving {key}")

                        # Copy object
                        result = s3_client.copy_object(
                            Bucket=DESTINATION_BUCKET,
                            Key=key,
                            CopySource={'Bucket':SOURCE_BUCKET, 'Key':key}
                        )['ResponseMetadata']

                except AssertionError as error:
                    print("Error: " + str(error))
                    result['Status'] = 'Failed'
                    # Respond to CloudFormation with a failure to process request
                    cfnresponse.send(event, context, cfnresponse.FAILED, result)
                    return result
    elif request_type == 'Delete':
        page_iterator = paginator.paginate(Bucket=DESTINATION_BUCKET)
        for page in page_iterator:
            for object in page['Contents']:
                try:
                    key = object['Key']

                    print(f"Deleting {key}")

                    # Copy object
                    result = s3_client.delete_object(
                        Bucket=DESTINATION_BUCKET,
                        Key=key
                    )['ResponseMetadata']

                except AssertionError as error:
                    print("Error: " + str(error))
                    result['Status'] = 'Failed'
                    # Respond to CloudFormation with a failure to process request
                    cfnresponse.send(event, context, cfnresponse.FAILED, result)
                    return result
    else:
        print("Error in CFTCode")

    result['Status'] = 'Success'
    cfnresponse.send(event, context, cfnresponse.SUCCESS, result)
    return result
