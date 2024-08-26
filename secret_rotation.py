import json
import boto3

def lambda_handler(event, context):
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    client = boto3.client("secretsmanager")
    
    metadata = client.describe_secret(SecretId=arn)
    
    if not metadata["RotationEnabled"]:
        raise ValueError(f"Secret {arn} is not enabled for rotation")
        
        
    print (f"Step: {step}")
    
    if step == "createSecret":
        create_secret(client, arn, token)
    elif step == "setSecret":
        set_secret(client, arn, token)
    elif step == "testSecret":
        test_secret(client, arn, token)
    elif step == "finishSecret":
        finish_secret(client, arn, token)
    else:
        raise ValueError(f"Unknown step: {step}")
    
    
def create_secret(client, arn, token):
    client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    print(f"Im Here")
    
    current_secret = client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")["SecretString"]
    secret_dict = json.loads(current_secret)
    
    try:
        client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
        print(f"Retrieving AWSPENDING: {client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")}")
    except client.exceptions.ResourceNotFoundException:
        
        password = client.get_random_password(ExcludeCharacters='/@"\'\\')
        secret_dict['password'] = password["RandomPassword"]


        client.put_secret_value(SecretId=arn, ClientRequestToken=token, SecretString=json.dumps(secret_dict), VersionStages=["AWSPENDING"])
        
        
def set_secret(client, arn, token):
    print("No database credentials to update...")
    
def test_secret(client, arn, token):
    print("No need for testing against any service...")
    
def finish_secret(client, arn, token):
    metadata = client.describe_secret(SecretId=arn)
    
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                return
            
            client.update_secret_version_stage(SecretId=arn, VersionStage="AWSCURRENT", MoveToVersionId=token, RemoveFromVersionId=version)
            client.update_secret_version_stage(SecretId=arn, VersionStage="AWSPENDING", RemoveFromVersionId=token)
            break
