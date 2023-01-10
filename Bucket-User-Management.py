import os

from google.cloud import storage
from google.oauth2 import service_account
import googleapiclient.discovery

project_id = "skona-tech-p1"

def enable_bucket_lifecycle_management(bucket_name):
    """Enable lifecycle management for a bucket"""
    # bucket_name = "my-bucket"

    storage_client = storage.Client()

    bucket = storage_client.get_bucket(bucket_name)
    rules = bucket.lifecycle_rules

    print(f"Lifecycle management rules for bucket {bucket_name} are {list(rules)}")
    bucket.add_lifecycle_delete_rule(age=30)
    bucket.patch()

    rules = bucket.lifecycle_rules
    print(f"Lifecycle management is enable for bucket {bucket_name} and the rules are {list(rules)}")

    return bucket

def create_bucket(bucket_name):
    """
    Create a new bucket in the US-EAST1 region with the NEARLINE storage
    class
    """
    # bucket_name = "your-new-bucket-name"

    bucket = storage.Client().bucket(bucket_name)
    bucket.storage_class = "NEARLINE"
    new_bucket = storage.Client().create_bucket(bucket, location="US-EAST1")
    enable_bucket_lifecycle_management(bucket_name)

    print(
        "Created bucket {} in {} with storage class {}".format(
            new_bucket.name, new_bucket.location, new_bucket.storage_class
        )
    )
    return new_bucket

def list_blobs(bucket_name):
    """ Returns a list of blobs containing the prefix """
    return storage.Client().list_blobs(bucket_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f"Blob {blob_name} deleted.")

def delete_bucket(bucket_name):
    """Deletes a bucket. The bucket must be empty."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()

    for blob in list_blobs(bucket_name):
        delete_blob(bucket_name, blob.name)

    bucket = storage_client.get_bucket(bucket_name)
    bucket.delete()

    print(f"Bucket {bucket.name} deleted")

def create_key(user):
    """Creates a key for a service account."""

    service_account_email = user + "@" + project_id + ".iam.gserviceaccount.com"
    
    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    key = service.projects().serviceAccounts().keys().create(
        name='projects/-/serviceAccounts/' + service_account_email, body={}
        ).execute()

    # The privateKeyData field contains the base64-encoded service account key
    # in JSON format.
    import base64

    json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')

    with open(user + ".json", "w") as outfile:
        outfile.write(json_key_file)


    if not key['disabled']:
        print('Created json key')

def create_service_account(project_id, name, display_name):
    """Creates a service account."""

    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    my_service_account = service.projects().serviceAccounts().create(
        name='projects/' + project_id,
        body={
            'accountId': name,
            'serviceAccount': {
                'displayName': display_name
            }
        }).execute()
    
    # THERE IS NO WAY TO DO THIS IN CLIENT LIBRARIES. THE AMOUNT OF ESCAPE CHARACTERS IS ACTUALLY MAKING ME MAD!!!
    os.system("gcloud projects add-iam-policy-binding " + project_id + " --member=\"serviceAccount:\" +  user + \"@" + project_id + ".iam.gserviceaccount.com\" --role=\"roles/storage.objectAdmin\" --condition=\"expression=resource.name.startsWith(\\\"projects/_/buckets/st-\" +  user + \"\\\"),title=st-\" +  user + \",description=\"")
    
    create_key(name)

    print('Created service account: ' + my_service_account['email'])
    return my_service_account

def delete_service_account(user):
    """Deletes a service account."""

    email = user + "@" + project_id + ".iam.gserviceaccount.com"
    
    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    os.system("gcloud projects remove-iam-policy-binding " + project_id + " --member=\"serviceAccount:\" +  user + \"@" + project_id + ".iam.gserviceaccount.com\" --role=\"roles/storage.objectAdmin\" --all")

    service.projects().serviceAccounts().delete(
        name='projects/-/serviceAccounts/' + email).execute()

    print('Deleted service account: ' + email)






answer = int(input("Do you want to:\n[1] Create a Bucket\n[2] Delete a Bucket\n"))

if answer == 1:
    user = input("Username: ")
    create_bucket("st-" + user)
    create_service_account(project_id, user, user)

elif answer == 2:
    user = input("Username: ")
    delete_bucket("st-" + user)
    delete_service_account(user)