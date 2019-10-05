
import sys
import json
import boto3
from datetime import datetime

session = boto3.session.Session()
args = sys.argv[1:]

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

class Page:
    def dig(self, arg):
        return NonePage()

    def meta(self):
        pass

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
            self.meta()
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
            page = page.dig(args[0])
            args = args[1:]
        return page

class NonePage(Page):
    def get(self, args):
        pass

class MenuPage(Page):
    def items(self):
        return []

    def dig(self, arg):
        items = self.items()
        for item in items:
            if item[0] == arg:
                return item[1]()
        sys.stderr.write("Not found: {}".format(arg))
        sys.exit(1)

    def view(self):
        items = self.items()
        for item in items:
            print(item[0])

class ItemsPage(Page):
    def nameColIdx(self):
        return 0

    def items(self):
        return []

    def detailPage(self, item):
        return

    def dig(self, arg):
        items = self.items()
        nameColIdx = self.nameColIdx()
        for item in items:
            if item[nameColIdx] == args[0]:
                return self.detailPage(item)
        sys.stderr.write("Not found: {}".format(args[0]))
        sys.exit(1)

    def view(self):
        items = self.items()
        for item in items:
            print(item)

class GlobalPage(MenuPage):
    def items(self):
        return [("s3", S3Page)]

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
        return NonePage()



GlobalPage().exec(args)

