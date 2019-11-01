
import datetime
import json
import re
import sys

import boto3

####################################################################################################

session = boto3.session.Session()
region = "ap-northeast-1" # TODO
#region = "us-west-2" # TODO

opt_quiet = False

args = sys.argv[1:]

bata8_cmd = ["bata8"]
aws_cmd = ["aws"]

while True:
    if len(args) > 1 and args[0] == "--profile":
        bata8_cmd = bata8_cmd + ["--profile", args[1]]
        aws_cmd   = aws_cmd   + ["--profile", args[1]]
        session = boto3.session.Session(profile_name = args[1])
        args = args[2:]
    elif len(args) > 1 and args[0] == "--region":
        bata8_cmd = bata8_cmd + ["--region", args[1]]
        aws_cmd   = aws_cmd   + ["--region", args[1]]
        region = args[1]
        args = args[2:]
    elif len(args) > 0 and (args[0] == "-q" or args[0] == "--quiet"):
        opt_quiet = True
        args = args[1:]
    else:
        break

####################################################################################################

def json_dump(obj):
    def support_othertype_default(o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        raise TypeError(repr(o) + " is not JSON serializable")
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False, default=support_othertype_default)

def print_dump(obj):
    print(json_dump(obj))

def table_col_to_str(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    else:
        return str(o)

def print_table(records):
    record_count = len(records)
    if record_count == 0:
        return
    col_count = len(records[0])
    col_width_list = []
    for j in range(col_count):
        col_width_list.append(0)
    for i in range(record_count):
        record = records[i]
        for j in range(col_count):
            s = table_col_to_str(record[j])
            if col_width_list[j] < len(s):
                col_width_list[j] = len(s)
    for record in records:
        pad1 = ""
        for j in range(col_count):
            elem = record[j]
            s = table_col_to_str(elem)
            pad = col_width_list[j] - len(s)
            if pad > 0:
                s = s + (" " * pad)
            s = pad1 + s
            sys.stdout.write(s)
            pad1 = " "
        sys.stdout.write("\n")

def normalize_command_args(args):
    ret = []
    for elem in args:
        if re.match("\\A[-_=/.,:A-Za-z0-9]+\\Z", elem):
            ret.append(elem)
        else:
            ret.append("'" + elem + "'") # TODO escape
    return " ".join(ret)

def tagsToLtsv(tags):
    s = ""
    for elem in tags:
        key   = elem["Key"]
        value = elem["Value"]
        key   = re.sub('[:\s]+', ' ', key)
        value = re.sub('\s+', ' ', value)
        if s != "":
            s = s + "\t"
        s = s + "{}:{}".format(key, value)
    return s

def tagsToLtsvLike(tags):
    s = ""
    for elem in tags:
        key   = elem["Key"]
        value = elem["Value"]
        key   = re.sub('[:\s]+', '_', key)
        value = re.sub('\s+', '_', value)
        if s != "":
            s = s + ","
        s = s + "{}:{}".format(key, value)
    return s

####################################################################################################

class Page:
    def dig(self, arg):
        sys.stderr.write("Unknown object: {}".format(arg))
        sys.exit(1)

    def canonical(self):
        return None

    def alt(self):
        return None

    def see_also(self):
        return None

    def help(self):
        return None

    def arn(self):
        return None

    def view(self):
        pass

    def exec(self, args):
        if (len(args) == 0):
            page = self._digs(args)
            page._view()
        else:
            self._digs(args)._view()

    def _view(self):
        canonical = self.canonical()
        if not opt_quiet and sys.stdout.isatty():
            f = False
            if canonical != None:
                if isinstance(canonical, list) and len(canonical) > 0 and isinstance(canonical[0], list):
                    for elem in canonical:
                        print("# canonical: " + normalize_command_args(bata8_cmd + elem))
                        f = True
                else:
                    print("# canonical: " + normalize_command_args(bata8_cmd + canonical))
                    f = True
            arn = self.arn()
            if arn != None:
                print("# canonical: " + normalize_command_args(bata8_cmd + [arn]))
                f = True
            alt_page = self.alt()
            if alt_page != None:
                if isinstance(alt_page, MenuPage):
                    for item in alt_page.items():
                        print("# see-also:  ... --alt {}".format(item[0]))
                        f = True
                else:
                    print("# see-also:  ... --alt")
                    f = True
            help_page = self.help()
            if help_page != None:
                if isinstance(help_page, MenuPage):
                    for item in help_page.items():
                        print("# see-also:  ... --help {}".format(item[0]))
                        f = True
                else:
                    print("# see-also:  ... --help")
                    f = True
            see_also_list = self.see_also()
            if see_also_list != None:
                for see_also in see_also_list:
                    print("# see-also:  " + normalize_command_args(see_also))
                    f = True
            if f:
                print("")
        self.view()

    def _digs(self, args):
        page = self
        while len(args) > 0:
            a = args[0]
            if a == "--alt":
                page = page.alt()
                if page == None:
                    sys.stderr.write("Alt page not found")
                    sys.exit(1)
            elif a == "--help":
                page = page.help()
                if page == None:
                    sys.stderr.write("Help page not found")
                    sys.exit(1)
            elif a.startswith("-"):
                sys.stderr.write("Unknown option: {}".format(a))
                sys.exit(1)
            else:
                page = page.dig(a)
                if page == None:
                    sys.stderr.write("Page not found: {}".format(a))
                    sys.exit(1)
            args = args[1:]
        return page

class NotImplementedPage(Page):
    def view(self):
        print("Not implemented page")

####################################################################################################

class MenuPage(Page):
    def canonical(self):
        return None

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

class TablePage(Page):
    def canonical(self):
        return None

    def alt(self):
        return super().alt()

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
        if re.match("\\A[0-9]*\\Z", arg):
            idx = int(arg)
            if idx >= 0 and idx < len(items):
                return self.detailPage(items[idx])
        sys.stderr.write("Page not found: {}".format(arg))
        sys.exit(1)

    def view(self):
        items = self.items()
        print_table(items)

class ObjectPage(Page):
    def canonical(self):
        return None

    def alt(self):
        return super().alt()

    def nameColIdx(self):
        return 0

    def object(self):
        return None

    def detailPage(self, item):
        return None

    def view(self):
        info = self.object()
        if isinstance(info, str):
            print(info)
        elif self._is_table(info):
            print_table(info)
        else:
            print_dump(info)

    def dig(self, arg):
        info = self.object()
        if not self._is_table(info):
            return ObjectElementPage(info, []).dig(arg)
        items = info
        nameColIdx = self.nameColIdx()
        for item in items:
            if item[nameColIdx] == arg:
                return self.detailPage(item)
        if re.match("\\A[0-9]*\\Z", arg):
            idx = int(arg)
            if idx >= 0 and idx < len(items):
                return self.detailPage(items[idx])
        sys.stderr.write("Page not found: {}".format(arg))
        sys.exit(1)

    def _is_table(self, info):
        if isinstance(info, list):
            if len(info) == 0:
                return True
            if isinstance(info[0], list):
                return True
        return False

class ObjectElementPage(Page):
    def __init__(self, elem, canonical):
        self.elem = elem
        self._canonical = canonical

    def canonical(self):
        return self._canonical

    def view(self):
        elem = self.elem
        if isinstance(elem, str):
            print(elem)
        else:
            print_dump(elem)

    def dig(self, arg):
        elem = self.elem
        if arg in elem:
            canonical = self._canonical
            if canonical != None:
                canonical.append(arg)
            return ObjectElementPage(elem[arg], canonical)
        elif re.match("\\A([0-9]*)\\Z", arg) and isinstance(elem, list):
            idx = int(arg)
            if idx < 0 or idx >= len(elem):
                return None
            canonical = self._canonical
            if canonical != None:
                canonical.append(arg)
            return ObjectElementPage(elem[idx], canonical)
        else:
            return None

####################################################################################################

def fetch_account_id():
    sts_client = session.client("sts")
    info = sts_client.get_caller_identity()
    account = info["Account"]
    return account

####################################################################################################

