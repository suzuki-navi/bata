
import sys
import json
import re
import boto3
import botocore
from datetime import datetime

session = boto3.session.Session()
args = sys.argv[1:]
region = "ap-northeast-1" # TODO

if len(args) > 1 and args[0] == "--profile":
    session = boto3.session.Session(profile_name = args[1])
    args = args[2:]

####################################################################################################

def json_dump(obj):
    def support_othertype_default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(repr(o) + " is not JSON serializable")
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False, default=support_othertype_default)

def print_dump(obj):
    print(json_dump(obj))

def table_col_to_str(o):
    if isinstance(o, datetime):
        return o.isoformat()
    else:
        return str(o)

def print_table(records):
    record_count = len(records)
    if record_count == 0:
        return
    head_count = record_count
    if head_count > 100:
        head_count = 100
    col_count = len(records[0])
    col_width_list = []
    for j in range(col_count):
        col_width_list.append(0)
    for i in range(head_count):
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

####################################################################################################

class Page:
    def dig(self, arg):
        sys.stderr.write("Unknown object: {}".format(arg))
        sys.exit(1)

    def alt(self):
        return None

    def canonical(self):
        return None

    def view(self):
        pass

    def help(self):
        pass

    def exec(self, args):
        if (len(args) == 0):
            page = self._digs(args)
            page._view()
        elif args[-1] == "--help":
            self.help()
        elif args[-1] == "--alt":
            page = self._digs(args)
            page._view()
        elif args[-1].startswith("-"):
            sys.stderr.write("Unknown option: {}".format(args[-1]))
            sys.exit(1)
        else:
            self._digs(args)._view()

    def _view(self):
        canonical = self.canonical()
        if sys.stdout.isatty():
            if canonical != None:
                print("# canonical: " + (" ".join(canonical)))
            alt_page = self.alt()
            if alt_page != None:
                if isinstance(alt_page, MenuPage):
                    for item in alt_page.items():
                        print("# see-also: ... --alt {}".format(item[0]))
                else:
                    print("# see-also: ... --alt")
        self.view()

    def _digs(self, args):
        page = self
        while len(args) > 0:
            a = args[0]
            if a == "--alt":
                page = page.alt()
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
        sys.stderr.write("Not found: {}".format(arg))
        sys.exit(1)

    def view(self):
        items = self.items()
        print_table(items)

class ObjectPage(Page):
    def canonical(self):
        return None

    def alt(self):
        return super().alt()

    def object(self):
        return None

    def view(self):
        meta = self.object()
        print_dump(meta)

    def dig(self, arg):
        elem = self.object()
        if arg in elem:
            canonical = self.canonical()
            if canonical != None:
                canonical.append(arg)
            return ObjectElementPage(elem[arg], canonical)
        else:
            return None

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

class GlobalPage(MenuPage):
    def items(self):
        return [
            ("code", CodePage),
            ("cloudwatch", CloudWatchPage),
            ("ecr", ECRPage),
            ("glue", GluePage),
            ("iam", IAMPage),
            ("lambda", LambdaPage),
            ("rds", RDSPage),
            ("s3", S3Page),
            ("support", SupportPage),
            ("vpc", VPCPage),
        ]

####################################################################################################

class CodePage(MenuPage):
    def items(self):
        return [
            ("commit", CodeCommitPage),
        ]

class CodeCommitPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("codecommit", region_name = region)
        ls = client.list_repositories(
        )
        items = []
        for elem in ls["repositories"]:
            items.append([elem["repositoryName"], elem["repositoryId"]])
        return items

    #def detailPage(self, item):
    #    return CodeCommitRepositoryPage(item[0], item[1])

####################################################################################################

class CloudWatchPage(MenuPage):
    def items(self):
        return [
            ("events", CloudWatchEventsPage),
            ("logs", CloudWatchLogsPage),
        ]

class CloudWatchEventsPage(MenuPage):
    def items(self):
        return [
            ("rules", CloudWatchEventsRulesPage),
        ]

class CloudWatchEventsRulesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("events", region_name = region)
        ls = client.list_rules(
        )
        items = []
        for elem in ls["Rules"]:
            items.append([elem["Name"], elem["Arn"]])
        return items

    def detailPage(self, item):
        return CloudWatchEventsRulePage(item[0], item[1])

class CloudWatchEventsRulePage(ObjectPage):
    def __init__(self, event_name, event_arn):
        self.event_name = event_name
        self.event_arn = event_arn

    def object(self):
        client = session.client("events", region_name = region)
        meta = client.describe_rule(
            Name = self.event_name,
        )
        del(meta["ResponseMetadata"])
        return meta

class CloudWatchLogsPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("logs", region_name = region)
        ls = client.describe_log_groups(
        )
        items = []
        for elem in ls["logGroups"]:
            items.append([elem["logGroupName"]])
        return items

    def detailPage(self, item):
        return CloudWatchLogGroupPage(item[0])

class CloudWatchLogGroupPage(TablePage):
    def __init__(self, log_group_name):
        self.log_group_name = log_group_name

    def items(self):
        client = session.client("logs", region_name = region)
        ls = client.describe_log_streams(
            logGroupName = self.log_group_name,
            orderBy = 'LastEventTime',
            descending = True,
        )
        items = []
        for elem in ls["logStreams"]:
            items.append([elem["logStreamName"], elem["firstEventTimestamp"], elem["lastIngestionTime"]])
        return items

    def detailPage(self, item):
        return CloudWatchLogStreamEventsPage(self.log_group_name, item[0])

class CloudWatchLogStreamEventsPage(TablePage):
    def __init__(self, log_group_name, log_stream_name):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name

    def items(self):
        client = session.client("logs", region_name = region)
        ls = client.get_log_events(
            logGroupName = self.log_group_name,
            logStreamName = self.log_stream_name,
        )
        items = []
        for elem in ls["events"]:
            items.append([elem["timestamp"], elem["ingestionTime"], elem["message"]])
        return items

    #def detailPage(self, item):
    #    return CloudWatchLogStreamsPage(item[0])

#class CloundWatchLogTextPage(Page):
#    def __init__(self, log_group_name, log_stream_name):
#        self.log_group_name = log_group_name
#        self.log_stream_name = log_stream_name


####################################################################################################

class ECRPage(MenuPage):
    def items(self):
        return [
            ("repositories", ECRRepositoriesPage),
        ]

class ECRRepositoriesPage(TablePage):
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

class ECRRepositoryImagesPage(TablePage):
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
    def canonical(self):
        return ["glue"]

    def items(self):
        return [
            ("databases", GlueDatabasesPage),
            ("connections", GlueConnectionsPage),
            ("crawlers", GlueCrawlersPage),
            ("jobs", GlueJobsPage),
        ]

class GlueDatabasesPage(TablePage):
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

class GlueDatabasePage(TablePage):
    def __init__(self, database_name):
        self.database_name = database_name

    def alt(self):
        return GlueDatabaseMetaPage(self.database_name)

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

class GlueDatabaseMetaPage(ObjectPage):
    def __init__(self, database_name):
        self.database_name = database_name

    def object(self):
        client = session.client("glue", region_name = region)
        info = client.get_database(
            Name = self.database_name,
        )
        return info["Database"]

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

class GlueConnectionsPage(TablePage):
    def canonical(self):
        return ["glue", "connections"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_connections()
        items = []
        for elem in ls["ConnectionList"]:
            items.append([elem["Name"]])
        return items

    def detailPage(self, item):
        return GlueConnectionPage(item[0])

class GlueConnectionPage(ObjectPage):
    def __init__(self, connection_name):
        self.connection_name = connection_name

    def canonical(self):
        return ["glue", "connections", self.connection_name]

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_connection(
            Name = self.connection_name,
        )
        return meta["Connection"]

class GlueCrawlersPage(TablePage):
    def canonical(self):
        return ["glue", "crawlers"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.list_crawlers()
        items = []
        for elem in ls["CrawlerNames"]:
            items.append([elem])
        return items

    def detailPage(self, item):
        return GlueCrawlerPage(item[0])

class GlueCrawlerPage(ObjectPage):
    def __init__(self, crawler_name):
        self.crawler_name = crawler_name

    def canonical(self):
        return ["glue", "crawlers", self.crawler_name]

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_crawler(
            Name = self.crawler_name,
        )
        return meta["Crawler"]

class GlueJobsPage(TablePage):
    def canonical(self):
        return ["glue", "jobs"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_jobs()
        items = []
        for elem in ls["Jobs"]:
            items.append([elem["Name"]])
        return items

    def detailPage(self, item):
        return GlueJobPage(item[0])

class GlueJobPage(MenuPage):
    def __init__(self, job_name):
        self.job_name = job_name

    def canonical(self):
        return ["glue", "jobs", self.job_name]

    def items(self):
        return [
            ("info", GlueJobInfoPage),
            ("bookmark", GlueJobBookmarkPage),
            ("history", GlueJobHistoryPage),
        ]

    def detailPage(self, item):
        return item[1](self.job_name)

class GlueJobInfoPage(ObjectPage):
    def __init__(self, job_name):
        self.job_name = job_name

    def canonical(self):
        return ["glue", "jobs", self.job_name, "info"]

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_job(
            JobName = self.job_name,
        )
        return meta["Job"]

class GlueJobBookmarkPage(ObjectPage):
    def __init__(self, job_name):
        self.job_name = job_name

    def canonical(self):
        return ["glue", "jobs", self.job_name, "bookmark"]

    def object(self):
        client = session.client("glue", region_name = region)
        try:
            meta = client.get_job_bookmark(
                JobName = self.job_name,
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "EntityNotFoundException":
                return None
            else:
                raise e
        return meta["JobBookmarkEntry"]

class GlueJobHistoryPage(TablePage):
    def __init__(self, job_name):
        self.job_name = job_name

    def canonical(self):
        return ["glue", "jobs", self.job_name, "history"]

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_job_runs(
            JobName = self.job_name,
        )
        items = []
        for elem in ls["JobRuns"]:
            err = ""
            if "ErrorMessage" in elem:
                err = elem["ErrorMessage"]
            items.append([elem["Id"], elem["StartedOn"], elem["JobRunState"], elem["ExecutionTime"], err])
        return items

    def detailPage(self, item):
        return GlueJobRunPage(self.job_name, item[0])

class GlueJobRunPage(ObjectPage):
    def __init__(self, job_name, run_id):
        self.job_name = job_name
        self.run_id = run_id

    def canonical(self):
        return ["glue", "jobs", self.job_name, "history", self.run_id]

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_job_run(
            JobName = self.job_name,
            RunId = self.run_id,
        )
        return meta["JobRun"]

####################################################################################################

class IAMPage(MenuPage):
    def items(self):
        return [
            ("users", IAMUsersPage),
            ("roles", IAMRolesPage),
            ("policies", IAMPoliciesPage),
        ]

class IAMUsersPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_users(
        )
        items = []
        for elem in ls["Users"]:
            items.append([elem["UserName"]])
        return items

    def detailPage(self, item):
        return IAMUserPage(item[0])

class IAMUserPage(ObjectPage):
    def __init__(self, user_name):
        self.user_name = user_name

    def object(self):
        client = session.client("iam")
        meta = client.get_user(
            UserName = self.user_name,
        )
        return meta["User"]

class IAMRolesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_roles(
        )
        items = []
        for elem in ls["Roles"]:
            items.append([elem["RoleName"]])
        return items

    def detailPage(self, item):
        return IAMRolePage(item[0])

class IAMRolePage(TablePage):
    def __init__(self, role_name):
        self.role_name = role_name

    def alt(self):
        return IAMRoleMetaPage(self.role_name)

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        items = []
        ls = client.list_role_policies(
            RoleName = self.role_name,
        )
        for elem in ls["PolicyNames"]:
            items.append([elem, "inline"])
        ls = client.list_attached_role_policies(
            RoleName = self.role_name,
        )
        for elem in ls["AttachedPolicies"]:
            items.append([elem["PolicyName"], "attached"])
        return items

class IAMRoleMetaPage(MenuPage):
    def __init__(self, role_name):
        self.role_name = role_name

    def items(self):
        return [
            ("info", IAMRoleInfoPage),
        ]

    def detailPage(self, item):
        return item[1](self.role_name)

class IAMRoleInfoPage(ObjectPage):
    def __init__(self, role_name):
        self.role_name = role_name

    def object(self):
        client = session.client("iam")
        meta = client.get_role(
            RoleName = self.role_name,
        )
        return meta["Role"]

class IAMPoliciesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_policies(
            Scope = "All",
            OnlyAttached = False,
            MaxItems = 1000,
        )
        items = []
        for elem in ls["Policies"]:
            items.append([elem["PolicyName"], elem["Arn"]])
        return items

    def detailPage(self, item):
        return IAMPolicyPage(item[0], item[1])

class IAMPolicyPage(ObjectPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def alt(self):
        return IAMPolicyMetaPage(self.policy_name, self.policy_arn)

    def object(self):
        client = session.client("iam")
        policy_meta = client.get_policy(
            PolicyArn = self.policy_arn,
        )
        version_id = policy_meta["Policy"]["DefaultVersionId"]
        version_meta = client.get_policy_version(
            PolicyArn = self.policy_arn,
            VersionId = version_id,
        )
        return version_meta["PolicyVersion"]["Document"]

class IAMPolicyMetaPage(MenuPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def items(self):
        return [
            ("info", IAMPolicyInfoPage),
            ("versions", IAMPolicyVersionsPage),
        ]

    def detailPage(self, item):
        return item[1](self.policy_name, self.policy_arn)

class IAMPolicyInfoPage(ObjectPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def object(self):
        client = session.client("iam")
        meta = client.get_policy(
            PolicyArn = self.policy_arn,
        )
        return meta["Policy"]

class IAMPolicyVersionsPage(TablePage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_policy_versions(
            PolicyArn = self.policy_arn,
        )
        items = []
        for elem in ls["Versions"]:
            items.append([elem["VersionId"], elem["IsDefaultVersion"]])
        return items

    def detailPage(self, item):
        return IAMPolicyVersionPage(self.policy_name, self.policy_arn, item[0])

class IAMPolicyVersionPage(ObjectPage):
    def __init__(self, policy_name, policy_arn, policy_version_id):
        self.policy_name = policy_name
        self.policy_arn = policy_arn
        self.policy_version_id = policy_version_id

    def object(self):
        client = session.client("iam")
        meta = client.get_policy_version(
            PolicyArn = self.policy_arn,
            VersionId = self.policy_version_id,
        )
        return meta["PolicyVersion"]

####################################################################################################

class LambdaPage(MenuPage):
    def items(self):
        return [
            ("functions", LambdaFunctionsPage),
        ]

class LambdaFunctionsPage(TablePage):
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

class RDSPage(MenuPage):
    def canonical(self):
        return ["rds"]

    def items(self):
        return [("databases", RDSDatabasesPage)]

class RDSDatabasesPage(TablePage):
    def canonical(self):
        return ["rds", "databases"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_instances()
        items = []
        for elem in ls["DBInstances"]:
            items.append([elem["DBInstanceIdentifier"], elem["Endpoint"]["Address"]])
        return items

    def detailPage(self, item):
        return RDSDatabasePage(item[0])

class RDSDatabasePage(TablePage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier]

    def alt(self):
        return RDSDatabaseAltPage(self.database_instance_identifier)

class RDSDatabaseAltPage(MenuPage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier, "--alt"]

    def items(self):
        return [
            ("info", RDSDatabaseInfoPage),
        ]

    def detailPage(self, item):
        return item[1](self.database_instance_identifier)

class RDSDatabaseInfoPage(ObjectPage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier, "--alt", "info"]

    def object(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_instances(
            DBInstanceIdentifier = self.database_instance_identifier,
        )
        return ls["DBInstances"][0]

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

class SupportPage(MenuPage):
    def canonical(self):
        return ["support"]

    def items(self):
        return [
            ("cases", SupportCasesPage),
        ]

class SupportCasesPage(TablePage):
    def canonical(self):
        return ["support", "cases"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("support")
        ls = client.describe_cases(
            language = "ja", # TODO
        )
        items = []
        for elem in ls["cases"]:
            items.append([elem["caseId"], elem["timeCreated"], elem["language"], elem["subject"]])
        return items

    def detailPage(self, item):
        return SupportCasePage(item[0], item[2])

class SupportCasePage(ObjectPage):
    def __init__(self, case_id, language):
        self.case_id = case_id
        self.language = language

    def canonical(self):
        return ["support", "cases", self.case_id]

    def object(self):
        client = session.client("support")
        info = client.describe_cases(
            caseIdList = [self.case_id],
            language = self.language,
        )
        return info["cases"][0]

####################################################################################################

class VPCPage(MenuPage):
    def canonical(self):
        return ["vpc"]

    def items(self):
        return [("vpcs", VPCVPCsPage)]

class VPCVPCsPage(TablePage):
    def canonical(self):
        return ["vpc", "vpcs"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2")
        ls = client.describe_vpcs()
        items = []
        for elem in ls["Vpcs"]:
            items.append([elem["VpcId"]])
        return items

    #def detailPage(self, item):
    #    return VPCVPCPage(item[0])

####################################################################################################

GlobalPage().exec(args)

####################################################################################################
