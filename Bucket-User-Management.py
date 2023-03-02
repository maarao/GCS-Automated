import os

# from google.cloud import storage
# from google.oauth2 import service_account
# import googleapiclient.discovery

project_id = "skona-tech-p1"


# def enable_bucket_lifecycle_management(bucket_name):
#     """Enable lifecycle management for a bucket"""
#     # bucket_name = "my-bucket"
#
#     storage_client = storage.Client()
#
#     bucket = storage_client.get_bucket(bucket_name)
#     rules = bucket.lifecycle_rules
#
#     print(f"Lifecycle management rules for bucket {bucket_name} are {list(rules)}")
#     bucket.add_lifecycle_delete_rule(age=30)
#     bucket.patch()
#
#     rules = bucket.lifecycle_rules
#     print(f"Lifecycle management is enable for bucket {bucket_name} and the rules are {list(rules)}")
#
#     return bucket


def create_bucket(user):
    """
    Create a new bucket in the US-EAST1 region with the NEARLINE storage
    class
    """
    bucket_name = "st-" + user
    #
    # bucket = storage.Client().bucket(bucket_name)
    # bucket.storage_class = "NEARLINE"
    # new_bucket = storage.Client().create_bucket(bucket, location="US-EAST1")
    # enable_bucket_lifecycle_management(bucket_name)
    #
    # print(
    #     "Created bucket {} in {} with storage class {}".format(
    #         new_bucket.name, new_bucket.location, new_bucket.storage_class
    #     )
    # )
    # return new_bucket

    # TODO Make type of bucket and lifecycle variables
    os.system("gsutil mb -p" + project_id + " -c NEARLINE -l US-EAST1 -b on gs://st-$user")
    os.system("gsutil lifecycle set lifecylce.json gs://" + bucket_name)


# def list_blobs(bucket_name):
#     """ Returns a list of blobs containing the prefix """
#     return storage.Client().list_blobs(bucket_name)
#
#
# def delete_blob(bucket_name, blob_name):
#     """Deletes a blob from the bucket."""
#     # bucket_name = "your-bucket-name"
#     # blob_name = "your-object-name"
#
#     storage_client = storage.Client()
#
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     blob.delete()
#
#     print(f"Blob {blob_name} deleted.")


def delete_bucket(user):
    """Deletes a bucket."""
    # # bucket_name = "your-bucket-name"
    #
    # storage_client = storage.Client()
    #
    # for blob in list_blobs(bucket_name):
    #     delete_blob(bucket_name, blob.name)
    #
    # bucket = storage_client.get_bucket(bucket_name)
    # bucket.delete()

    bucket_name = "st-" + user

    # This is so much faster with gsutil it's sad
    os.system("gsutil -m rm -r gs://" + bucket_name)

    print(f"Bucket {bucket_name} deleted")


# def create_key(user):
#     """Creates a key for a service account."""
#
#     service_account_email = user + "@" + project_id + ".iam.gserviceaccount.com"
#
#     credentials = service_account.Credentials.from_service_account_file(
#         filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
#         scopes=['https://www.googleapis.com/auth/cloud-platform'])
#
#     service = googleapiclient.discovery.build(
#         'iam', 'v1', credentials=credentials)
#
#     key = service.projects().serviceAccounts().keys().create(
#         name='projects/-/serviceAccounts/' + service_account_email, body={}
#     ).execute()
#
#     # The privateKeyData field contains the base64-encoded service account key
#     # in JSON format.
#     import base64
#
#     json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')
#
#     with open(user + ".json", "w") as outfile:
#         outfile.write(json_key_file)
#
#     if not key['disabled']:
#         print('Created json key')


def create_service_account(project_id, user):
    """Creates a service account."""

    # credentials = service_account.Credentials.from_service_account_file(
    #     filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
    #     scopes=['https://www.googleapis.com/auth/cloud-platform'])
    #
    # service = googleapiclient.discovery.build(
    #     'iam', 'v1', credentials=credentials)

    # my_service_account = service.projects().serviceAccounts().create(
    #     name='projects/' + project_id,
    #     body={
    #         'accountId': name,
    #         'serviceAccount': {
    #             'displayName': display_name
    #         }
    #     }).execute()

    # THERE IS NO WAY TO DO THIS IN CLIENT LIBRARIES. THE AMOUNT OF ESCAPE CHARACTERS IS ACTUALLY MAKING ME MAD!!!

    # Almost KMS after I thought I could have done it with a multi-line comment. Realized I couldn't :)
    email = user + "@" + project_id + ".iam.gserviceaccount.com"

    os.system("gcloud iam service-accounts create " + user + " \\" + "\n    --description=\"\" \\" + "\n    --display-name=\""+ user + "\"")

    os.system("gcloud projects add-iam-policy-binding skona-tech-p1 \\" + "\n    --member=\"serviceAccount:" + email + "\" \\" + "\n    --role=\"roles/storage.objectAdmin\" \\" + "\n    --condition=\"expression=resource.name.startsWith(\\" + "\"projects/_/buckets/st-"+ user + "\\" + "\"),title=st-" + user + ",description=\"")

    # create_key(name)
    os.system("gcloud iam service-accounts keys create " + user + ".json \\" + "\n    --iam-account=" + email)

    print('Created service account: ' + email)

def delete_service_account(user):
    """Deletes a service account."""

    email = user + "@" + project_id + ".iam.gserviceaccount.com"

    # Useless for now
    # credentials = service_account.Credentials.from_service_account_file(
    #     filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
    #     scopes=['https://www.googleapis.com/auth/cloud-platform'])
    #
    # service = googleapiclient.discovery.build(
    #     'iam', 'v1', credentials=credentials)

    # iam permissions management (nightmare to do this :(  )
    os.system("gcloud projects remove-iam-policy-binding " + project_id + " \\" + "\n    --member=\"serviceAccount:" + email + "\""+ " \\" + "\n    --role=\"roles/storage.objectAdmin\" " + "\\" + "\n    --all")

    # service.projects().serviceAccounts().delete(
    #     name='projects/-/serviceAccounts/' + email).execute()

    # account management
    os.system("gcloud iam service-accounts delete " + email)

    # print('Deleted service account: ' + email)


answer = int(input("Do you want to:\n[1] Create a Bucket\n[2] Delete a Bucket\n"))

if answer == 1:
    user = input("Username: ")
    create_bucket(user)
    create_service_account(project_id, user)

elif answer == 2:
    user = input("Username: ")
    delete_bucket(user)
    delete_service_account(user)
