from datetime import date
from datetime import timedelta

from google.cloud import storage


def get_buckets():
    """ Gets all buckets """

    buckets = storage.Client().list_buckets()

    return buckets

'''
# For differentiating between different backup systems
def filter_buckets(label):
    for bucket in get_buckets():
        print(f"Name: {bucket.name}")
'''

def blobs_with_prefix(bucket_name, prefix):
    """ Returns a list of blobs containing the prefix """
    return storage.Client().list_blobs(bucket_name, prefix=prefix)



buckets = get_buckets()

prefix = "RecordFile/" + (date.today() - timedelta(days = 1)).strftime("%Y%m%d")

# print(prefix) # Debug
# print(list(blobs_with_prefix("st-manjit-singh-01", prefix)))


for bucket in buckets:
    if list(blobs_with_prefix(bucket.name, prefix)) == []:
        print(bucket.name)
