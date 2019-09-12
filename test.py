
import sys
import json
import boto3
from datetime import datetime

session = boto3.session.Session()
args = sys.argv[1:]

if len(args) > 1 and args[0] == "--profile":
    session = boto3.session.Session(profile_name = args[1])
    args = args[2:]

class Page:
    def exec(self, args):
        if (len(args) == 0):
            self.view(args)
        elif args[0] == "--help":
            self.help()
        elif len(args) > 1 and args[1] == "--completion":
            self.completion(args[0])
        else:
            self.view(args)

    def view(self, args):
        pass

    def help(self):
        pass

    def completion(self, arg):
        pass


def json_dump(obj):
    def support_othertype_default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(repr(o) + " is not JSON serializable")
    return json.dumps(obj, sort_keys=True, indent=4, default=support_othertype_default)

def print_dump(obj):
    print(json_dump(obj))

class GlobalPage(Page):
    def view(self, args):
        if len(args) > 0:
            if args[0] == "s3":
                S3Page().exec(args[1:])
            elif args[0] == "glue":
                GluePage().exec(args[1:])
            elif args[0] == "lambda":
                LambdaPage().exec(args[1:])
            else:
                pass
        else:
            print("s3")
            print("glue")
            print("lambda")

class S3Page(Page):
    def view(self, args):
        if len(args) > 0:
            pass
        else:
            client = session.client("s3")
            ls = client.list_buckets()
            for elem in ls["Buckets"]:
                print(elem["Name"])

class GluePage(Page):
    def view(self, args):
        if len(args) > 0:
            if args[0] == "databases":
                GlueDatabasesPage().exec(args[1:])
            else:
                pass
        else:
            print("databases")

class GlueDatabasesPage(Page):
    def view(self, args):
        if len(args) > 0:
            GlueDatabasePage(args[0]).exec(args[1:])
        else:
            client = session.client("glue")
            ls = client.get_databases()
            for elem in ls["DatabaseList"]:
                print(elem["Name"])

class GlueDatabasePage(Page):
    def __init__(self, name):
        self.name = name

    def view(self, args):
        if len(args) > 0:
            GlueTablePage(self.name, args[0]).exec(args[1:])
        else:
            client = session.client("glue")
            ls = client.get_tables(DatabaseName = self.name)
            for elem in ls["TableList"]:
                print(elem["Name"])

class GlueTablePage(Page):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name
    def view(self, args):
        if len(args) > 0:
            if args[0] == "meta":
                GlueTableMetaPage(self.database_name, self.table_name).exec(args[1:])
            else:
                pass
        else:
            print("meta")

class GlueTableMetaPage(Page):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name
    def view(self, args):
        if len(args) > 0:
            pass
        else:
            client = session.client("glue")
            ls = client.get_table(DatabaseName = self.database_name, Name = self.table_name)
            print_dump(ls["Table"])

class LambdaPage(Page):
    def view(self, args):
        if len(args) > 0:
            if args[0] == "functions":
                LambdaFunctionsPage().exec(args[1:])
            else:
                pass
        else:
            print("functions")

class LambdaFunctionsPage(Page):
    def view(self, args):
        if len(args) > 0:
            LambdaFunctionPage(args[0]).exec(args[1:])
        else:
            client = session.client("lambda")
            ls = client.list_functions()
            for elem in ls["Functions"]:
                print(elem["FunctionName"])

class LambdaFunctionPage(Page):
    def __init__(self, name):
        self.name = name
    def view(self, args):
        if len(args) > 0:
            if args[0] == "meta":
                LambdaFunctionMetaPage(self.name).exec(args[1:])
            else:
                pass
        else:
            print("meta")

class LambdaFunctionMetaPage(Page):
    def __init__(self, name):
        self.name = name
    def view(self, args):
        if len(args) > 0:
            pass
        else:
            client = session.client("lambda")
            result = {}
            meta = client.get_function(FunctionName = self.name)
            result["Code"] = meta["Code"]
            result["Configuration"] = meta["Configuration"]
            aliases = client.list_aliases(FunctionName = self.name)
            result["Aliases"] = aliases["Aliases"]
            print_dump(result)


pass

#client = session.client("lambda")
#print_dump(client.list_functions()["Functions"])


GlobalPage().exec(args)

