
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class S3Page(MenuPage):
    def items(self):
        return [("buckets", S3BucketsPage)]

class S3BucketsPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("s3")
        ls = client.list_buckets()
        items = []
        for elem in ls["Buckets"]:
            items.append([elem["Name"]])
        return items

    def detailPage(self, item):
        return S3DirPage(item[0], "")

class S3BucketMetaPage(MenuPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def items(self):
        return [
            ("versioning", S3BucketMetaVersioningPage),
            ("policy", S3BucketMetaPolicyPage),
        ]

    def detailPage(self, item):
        return item[1](self.bucket_name)

class S3BucketMetaVersioningPage(ObjectPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def object(self):
        client = session.client("s3")
        meta = client.get_bucket_versioning(
            Bucket = self.bucket_name,
        )
        del(meta["ResponseMetadata"])
        return meta

class S3BucketMetaPolicyPage(ObjectPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def object(self):
        client = session.client("s3")
        try:
            meta = client.get_bucket_policy(
                Bucket = self.bucket_name,
            )
            json_str = meta["Policy"]
            meta2 = json.loads(json_str)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
                meta2 = None
            else:
                raise e
        return meta2

class S3DirPage(TablePage):
    def __init__(self, bucket_name, path):
        self.bucket_name = bucket_name
        self.path = path

    def alt(self):
        if self.path == "":
            return S3BucketMetaPage(self.bucket_name)
        else:
            return super().alt()

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("s3")
        if self.path == "":
            prefix = ""
        else:
            prefix = self.path + "/"
        ls = client.list_objects_v2(
            Bucket = self.bucket_name,
            Delimiter = "/",
            Prefix = prefix,
        )
        items = []
        len_prefix = len(prefix)
        if "CommonPrefixes" in ls:
            for elem in ls["CommonPrefixes"]:
                name = elem["Prefix"]
                if name.endswith("/"):
                    name = name[0:-1]
                if name.startswith(prefix):
                    name = name[len_prefix : ]
                items.append([name, "", "", ""])
        if "Contents" in ls:
            for elem in ls["Contents"]:
                name = elem["Key"]
                if name.startswith(prefix):
                    name = name[len_prefix : ]
                items.append([name, elem["LastModified"], elem["Size"], elem["StorageClass"]])
        return items

    def detailPage(self, item):
        if self.path == "":
            prefix = ""
        else:
            prefix = self.path + "/"
        path = prefix + item[0]
        if item[1] == "":
            return S3DirPage(self.bucket_name, path)
        else:
            return S3ObjectPage(self.bucket_name, path)

class S3ObjectPage(ObjectPage):
    def __init__(self, bucket_name, key):
        self.bucket_name = bucket_name
        self.key = key

    def object(self):
        client = session.client("s3")
        info = client.get_object(
            Bucket = self.bucket_name,
            Key = self.key,
        )
        del(info["ResponseMetadata"])
        del(info["Body"])
        return info

####################################################################################################

