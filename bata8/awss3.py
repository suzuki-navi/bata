
import boto3
import botocore

from bata8.lib import *

from bata8.awscloudwatch import *

####################################################################################################

class S3Page(MenuPage):
    def canonical(self):
        return ["s3"]

    def see_also(self):
        cmd = ["bata8", "s3", "s3://.../..."]
        return [cmd]

    def items(self):
        return [("buckets", S3BucketsPage)]

    @classmethod
    def page_from_uri(cls, path):
        match = re.match("\\As3://([^/]+)\\Z", path)
        if match:
            return S3KeyPage(match.group(1), "")
        match = re.match("\\As3://([^/]+)/(.*)\\Z", path)
        if match:
            bucket_name = match.group(1)
            key = match.group(2)
            if key.endswith("/"):
                key = key[0:-1]
            try:
                return S3KeyPage(bucket_name, key)
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "AccessDenied":
                    pass
                else:
                    raise e
        return None

class S3BucketsPage(TablePage):
    def canonical(self):
        return ["s3", "buckets"]

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
        return S3KeyPage(item[0], "")

class S3BucketAltPage(MenuPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def canonical(self):
        return ["s3", "buckets", self.bucket_name, "--alt"]

    def items(self):
        return [
            ("versioning", S3BucketVersioningPage),
            ("policy", S3BucketPolicyPage),
            ("metrics", S3BucketMetricsPage),
        ]

    def detailPage(self, item):
        return item[1](self.bucket_name)

class S3BucketVersioningPage(ObjectPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def canonical(self):
        return ["s3", "buckets", self.bucket_name, "--alt", "versioning"]

    def object(self):
        client = session.client("s3")
        meta = client.get_bucket_versioning(
            Bucket = self.bucket_name,
        )
        del(meta["ResponseMetadata"])
        return meta

class S3BucketPolicyPage(ObjectPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def canonical(self):
        return ["s3", "buckets", self.bucket_name, "--alt", "policy"]

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

class S3BucketMetricsPage(MenuPage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def canonical(self):
        return ["s3", "buckets", self.bucket_name, "--alt", "metrics"]

    def items(self):
        return [
            ("size", "BucketSizeBytes", "StandardStorage"),
            ("count", "NumberOfObjects", "AllStorageTypes"),
        ]

    def detailPage(self, item):
        metric_name = item[1]
        storage_type = item[2]
        dimensions = "StorageType:{},BucketName:{}".format(storage_type, self.bucket_name)
        return CloudWatchMetricsNamespaceMetricDimensionPage("AWS/S3", metric_name, dimensions)

class S3KeyPage(ObjectPage):
    def __init__(self, bucket_name, key):
        self.bucket_name = bucket_name
        self.key = key
        self.info  = self._fetch_info()
        self.items = self._fetch_items()

    def _fetch_info(self):
        if self.key == "":
            return None
        try:
            client = session.client("s3")
            info = client.get_object(
                Bucket = self.bucket_name,
                Key = self.key,
            )
            del(info["ResponseMetadata"])
            del(info["Body"])
            return info
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            else:
                raise e

    def _fetch_items(self):
        client = session.client("s3")
        prefix = self._prefix()
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

    def _prefix(self):
        if self.key == "":
            prefix = ""
        else:
            prefix = self.key + "/"
        return prefix

    def s3path(self):
        return "s3://{}/{}".format(self.bucket_name, self.key)

    def canonical(self):
        if len(self.key) == 0:
            paths = []
        else:
            paths = self.key.split("/")
        canonical1 = ["s3", "buckets", self.bucket_name] + paths
        canonical2 = [self.s3path()]
        return [canonical1, canonical2]

    def arn(self):
        if len(self.key) == 0:
            return "arn:aws:s3:::{}".format(self.bucket_name)
        else:
            return "arn:aws:s3:::{}/{}".format(self.bucket_name, self.key)

    def alt(self):
        if self.key == "":
            return S3BucketAltPage(self.bucket_name)
        return super().alt()

    def see_also(self):
        if len(self.items) == 0:
            cmd = aws_cmd + ["s3", "cp", self.s3path(), "-"]
        else:
            if len(self.key) == 0:
                cmd = aws_cmd + ["s3", "ls", self.s3path()]
            else:
                cmd = aws_cmd + ["s3", "ls", self.s3path() + "/"]
        return [cmd]

    def nameColIdx(self):
        return 0

    def object(self):
        if len(self.items) == 0:
            return self.info
        else:
            return self.items

    def detailPage(self, item):
        key = self._prefix() + item[0]
        return S3KeyPage(self.bucket_name, key)

    @classmethod
    def page_from_arn(cls, arn, account_id, region):
        match = re.match("\\Aarn:aws:s3:::(.+?)/(.*)\\Z", arn)
        if match:
            return S3KeyPage(match.group(1), match.group(2))

        match = re.match("\\Aarn:aws:s3:::(.+?)\\Z", arn)
        if match:
            return S3KeyPage(match.group(1), "")

####################################################################################################

