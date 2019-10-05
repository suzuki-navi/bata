
import sys
import json
import boto3
import botocore
from datetime import datetime

session = boto3.session.Session()
args = sys.argv[1:]
region = "ap-northeast-1" # TODO

if len(args) > 1 and args[0] == "--profile":
    session = boto3.session.Session(profile_name = args[1])
    args = args[2:]

def json_dump(obj):
    def support_othertype_default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(repr(o) + " is not JSON serializable")
    return json.dumps(obj, sort_keys=True, indent=4, default=support_othertype_default)

def print_dump(obj):
    print(json_dump(obj))

####################################################################################################

class Page:
    def dig(self, arg):
        sys.stderr.write("Unknown object: {}".format(arg))
        sys.exit(1)

    def meta(self):
        return None

    def view(self):
        pass

    def help(self):
        pass

    def exec(self, args):
        if (len(args) == 0):
            self.digs(args).view()
        elif args[-1] == "--help":
            self.help()
        elif args[-1] == "--meta":
            self.digs(args).view()
        #elif args[-1] == "--create":
        #    self.digs(args[0:-1]).create()
        #elif args[-1] == "--update":
        #    self.digs(args[0:-1]).update()
        #elif args[-1] == "--delete":
        #    self.digs(args[0:-1]).delete()
        elif args[-1].startswith("-"):
            sys.stderr.write("Unknown option: {}".format(args[-1]))
            sys.exit(1)
        else:
            self.digs(args).view()

    def digs(self, args):
        page = self
        while len(args) > 0:
            a = args[0]
            if a == "--meta":
                page = page.meta()
                if page == None:
                    sys.stderr.write("Meta page not found")
                    sys.exit(1)
            elif a.startswith("-"):
                sys.stderr.write("Unknown option: {}".format(args[-1]))
                sys.exit(1)
            else:
                page = page.dig(a)
                if page == None:
                    sys.stderr.write("Page not found: {}".format(a))
                    sys.exit(1)
            args = args[1:]
        return page

class NonePage(Page):
    pass

####################################################################################################

class MenuPage(Page):
    def items(self):
        return []

    def detailPage(self, item):
        return item[1]()

    def dig(self, arg):
        items = self.items()
        for item in items:
            if item[0] == arg:
                return self.detailPage(item)
        sys.stderr.write("Not found: {}".format(arg))
        sys.exit(1)

    def view(self):
        items = self.items()
        for item in items:
            print(item[0])

class ItemsPage(Page):
    def meta(self):
        return super().meta()

    def nameColIdx(self):
        return 0

    def items(self):
        return []

    def detailPage(self, item):
        return None

    def dig(self, arg):
        items = self.items()
        nameColIdx = self.nameColIdx()
        for item in items:
            if item[nameColIdx] == arg:
                return self.detailPage(item)
        sys.stderr.write("Not found: {}".format(arg))
        sys.exit(1)

    def view(self):
        items = self.items()
        for item in items:
            print(item)

class ObjectPage(Page):
    def meta(self):
        return super().meta()

    def object(self):
        return None

    def view(self):
        if sys.stdout.isatty():
            if self.meta() != None:
                print("# --meta exists.")
        meta = self.object()
        print_dump(meta)

####################################################################################################

class GlobalPage(MenuPage):
    def items(self):
        return [
            ("ecr", ECRPage),
            ("glue", GluePage),
            ("lambda", LambdaPage),
            ("s3", S3Page),
        ]

####################################################################################################

class ECRPage(MenuPage):
    def items(self):
        return [
            ("repositories", ECRRepositoriesPage),
        ]

class ECRRepositoriesPage(ItemsPage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ecr", region_name = region)
        paginator = client.get_paginator("describe_repositories")
        iterator = paginator.paginate(
        )
        items = []
        for ls in iterator:
            for elem in ls["repositories"]:
                items.append([elem["repositoryName"], elem["repositoryUri"]])
        return items

    def detailPage(self, item):
        return ECRRepositoryImagesPage(item[0])

class ECRRepositoryImagesPage(ItemsPage):
    def __init__(self, repository_name):
        self.repository_name = repository_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ecr", region_name = region)
        ls = client.list_images(
            repositoryName = self.repository_name,
        )
        items = []
        for elem in ls["imageIds"]:
            items.append([elem["imageTag"], elem["imageDigest"]])
        return items

    def detailPage(self, item):
        return ECRRepositoryImagePage(self.repository_name, item[0])

class ECRRepositoryImagePage(ObjectPage):
    def __init__(self, repository_name, image_tag):
        self.repository_name = repository_name
        self.image_tag = image_tag

    def object(self):
        client = session.client("ecr", region_name = region)
        meta = client.describe_images(
            repositoryName = self.repository_name,
            imageIds = [ { "imageTag": self.image_tag } ],
        )
        #del(meta["ResponseMetadata"])
        return meta["imageDetails"][0]

####################################################################################################

class GluePage(MenuPage):
    def items(self):
        return [
            ("databases", GlueDatabasesPage),
        ]

class GlueDatabasesPage(ItemsPage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_databases()
        items = []
        for elem in ls["DatabaseList"]:
            items.append([elem["Name"]])
        return items

    def detailPage(self, item):
        return GlueDatabasePage(item[0])

class GlueDatabasePage(ItemsPage):
    def __init__(self, database_name):
        self.database_name = database_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_tables(
            DatabaseName = self.database_name,
        )
        items = []
        for elem in ls["TableList"]:
            items.append([elem["Name"]])
        return items

    def detailPage(self, item):
        return GlueTablePage(self.database_name, item[0])

class GlueTablePage(ObjectPage):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_table(
            DatabaseName = self.database_name,
            Name = self.table_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Table"]

####################################################################################################

class LambdaPage(MenuPage):
    def items(self):
        return [
            ("functions", LambdaFunctionsPage),
        ]

class LambdaFunctionsPage(ItemsPage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("lambda", region_name = region)
        ls = client.list_functions()
        items = []
        for elem in ls["Functions"]:
            items.append([elem["FunctionName"]])
        return items

    def detailPage(self, item):
        return LambdaFunctionPage(item[0])


class LambdaFunctionPage(MenuPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def items(self):
        return [
            ("code", LambdaFunctionCodePage),
            ("configuration", LambdaFunctionConfigurationPage),
            ("aliases", LambdaFunctionAliasesPage),
        ]

    def detailPage(self, item):
        return item[1](self.function_name)

class LambdaFunctionCodePage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def object(self):
        client = session.client("lambda", region_name = region)
        meta = client.get_function(
            FunctionName = self.function_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Code"]

class LambdaFunctionConfigurationPage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def object(self):
        client = session.client("lambda", region_name = region)
        meta = client.get_function(
            FunctionName = self.function_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Configuration"]

class LambdaFunctionAliasesPage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    #def object(self):
    #    client = session.client("lambda", region_name = region)
    #    meta = client.list_aliases(
    #        FunctionName = self.function_name,
    #    )
    #    del(meta["ResponseMetadata"])
    #    return meta

####################################################################################################

class S3Page(MenuPage):
    def items(self):
        return [("buckets", S3BucketsPage)]

class S3BucketsPage(ItemsPage):
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

class S3DirPage(ItemsPage):
    def __init__(self, bucket_name, path):
        self.bucket_name = bucket_name
        self.path = path

    def meta(self):
        if self.path == "":
            return S3BucketMetaPage(self.bucket_name)
        else:
            return super().meta()

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
        if "CommonPrefixes" in ls:
            for elem in ls["CommonPrefixes"]:
                name = elem["Prefix"]
                if name.endswith("/"):
                    name = name[0:-1]
                items.append([name, "", "", ""])
        if "Contents" in ls:
            len_prefix = len(prefix)
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
            return NonePage()
        else:
            return S3DirPage(self.bucket_name, path)

####################################################################################################

GlobalPage().exec(args)

####################################################################################################
