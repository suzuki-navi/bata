
import sys
import json
import re
import boto3
import botocore
import datetime

session = boto3.session.Session()
args = sys.argv[1:]
region = "ap-northeast-1" # TODO

if len(args) > 1 and args[0] == "--profile":
    session = boto3.session.Session(profile_name = args[1])
    args = args[2:]

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
                print("# canonical: bata8 " + normalize_command_args(canonical))
            alt_page = self.alt()
            if alt_page != None:
                if isinstance(alt_page, MenuPage):
                    for item in alt_page.items():
                        print("# see-also: ... --alt {}".format(item[0]))
                else:
                    print("# see-also: ... --alt")
            see_also_list = self.see_also()
            if see_also_list != None:
                for see_also in see_also_list:
                    print("# see-also: " + normalize_command_args(see_also))
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
            ("redshift", RedshiftPage),
            ("s3", S3Page),
            ("sts", STSPage),
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
    def canonical(self):
        return ["cloudwatch"]

    def items(self):
        return [
            ("events", CloudWatchEventsPage),
            ("logs", CloudWatchLogsPage),
            ("metrics", CloudWatchMetricsPage),
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

class CloudWatchMetricsPage(TablePage):
    def canonical(self):
        return ["cloudwatch", "metrics"]

    def alt(self):
        return CloudWatchMetricsAltPage()

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("cloudwatch", region_name = region)
        ls = client.list_metrics(
        )
        namespaces = []
        for elem in ls["Metrics"]:
            namespaces.append(elem["Namespace"])
        namespaces = list(set(namespaces))
        items = []
        for elem in namespaces:
            items.append([elem])
        items.sort()
        return items

    def detailPage(self, item):
        return CloudWatchMetricsNamespacePage(item[0])

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return CloudWatchMetricsNamespacePage(arg)

class CloudWatchMetricsAltPage(MenuPage):
    def items(self):
        return [
            ("all", CloudWatchMetricsAllPage),
        ]

    def detailPage(self, item):
        if item[0] == "all":
            return item[1](None, None)
        else:
            return item[1]()

class CloudWatchMetricsNamespacePage(TablePage):
    def __init__(self, namespace):
        self.namespace = namespace

    def canonical(self):
        return ["cloudwatch", "metrics", self.namespace]

    def alt(self):
        return CloudWatchMetricsNamespaceAltPage(self.namespace)

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("cloudwatch", region_name = region)
        ls = client.list_metrics(
            Namespace = self.namespace,
        )
        metricNames = []
        for elem in ls["Metrics"]:
            metricNames.append(elem["MetricName"])
        metricNames = list(set(metricNames))
        items = []
        for elem in metricNames:
            items.append([elem])
        items.sort()
        return items

    def detailPage(self, item):
        return CloudWatchMetricsAllPage(self.namespace, item[0])

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return CloudWatchMetricsAllPage(self.namespace, arg)

class CloudWatchMetricsNamespaceAltPage(MenuPage):
    def __init__(self, namespace):
        self.namespace = namespace

    def items(self):
        return [
            ("all", CloudWatchMetricsAllPage),
        ]

    def detailPage(self, item):
        if item[0] == "all":
            return item[1](self.namespace, None)
        else:
            return item[1](self.namespace)

class CloudWatchMetricsAllPage(TablePage):
    # namespace, metric_name はNone可
    def __init__(self, namespace, metric_name):
        self.namespace = namespace
        self.metric_name = metric_name

    def canonical(self):
        if self.namespace == None:
            return ["cloudwatch", "metrics", "--alt", "all"]
        elif self.metric_name == None:
            return ["cloudwatch", "metrics", self.namespace, "--alt", "all"]
        else:
            return ["cloudwatch", "metrics", self.namespace, self.metric_name]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("cloudwatch", region_name = region)
        if self.namespace == None:
            ls = client.list_metrics(
            )
        elif self.metric_name == None:
            ls = client.list_metrics(
                Namespace = self.namespace,
            )
        else:
            ls = client.list_metrics(
                Namespace = self.namespace,
                MetricName = self.metric_name,
            )
        items = []
        for elem in ls["Metrics"]:
            dims = ""
            for dim in elem["Dimensions"]:
                if dims != "":
                    dims += ","
                dims += "{}:{}".format(dim["Name"], dim["Value"])
            if self.namespace == None:
                items.append([elem["Namespace"], elem["MetricName"], dims])
            elif self.metric_name == None:
                items.append([elem["MetricName"], dims])
            else:
                items.append([dims])
        items.sort()
        return items
        #items2 = []
        #for i in range(len(items)):
        #    items2.append([str(i)] + items[i])
        #return items2

    def detailPage(self, item):
        if self.namespace == None:
            return CloudWatchMetricsNamespaceMetricDimensionPage(item[0], item[1], item[2])
        elif self.metric_name == None:
            return CloudWatchMetricsNamespaceMetricDimensionPage(self.namespace, item[0], item[1])
        else:
            return CloudWatchMetricsNamespaceMetricDimensionPage(self.namespace, self.metric_name, item[0])

    #def dig(self, arg):
    #    if re.match("\\A[0-9]*\\Z", arg):
    #        return super().dig(arg)
    #    return CloudWatchMetricsNamespaceMetricDimensionPage(arg)

class CloudWatchMetricsNamespaceMetricDimensionPage(TablePage):
    def __init__(self, namespace, metric_name, dimension):
        self.namespace = namespace
        self.metric_name = metric_name
        self.dimension = dimension

    def _now(self):
        now = datetime.datetime.now()
        now = now - datetime.timedelta(seconds = now.second)
        now = now - datetime.timedelta(microseconds = now.microsecond)
        return now

    def canonical(self):
        return ["cloudwatch", "metrics", self.namespace, self.metric_name, self.dimension]

    def see_also(self):
        now = self._now()
        dimensions = []
        if self.dimension != "":
            dimensions.append("--dimensions")
            for elem in self.dimension.split(","):
                [k, v] = elem.split(":", 1)
                dimensions.append("Name={},Value={}".format(k, v))
        cmd = [
                "aws", "cloudwatch", "get-metric-statistics",
                "--namespace", self.namespace,
                "--metric-name", self.metric_name,
            ] + dimensions + [
                "--start-time", (now - datetime.timedelta(days = 1)).isoformat(),
                "--end-time", now.isoformat(),
                "--period", "60",
                "--statistics", "Average",
                "--output", "text",
            ]
        return [cmd]

    def nameColIdx(self):
        return 0

    def items(self):
        now = self._now()
        dimensions = []
        if self.dimension != "":
            for elem in self.dimension.split(","):
                [k, v] = elem.split(":", 1)
                dimensions.append({"Name": k, "Value": v})
        client = session.client("cloudwatch", region_name = region)
        ls = client.get_metric_statistics(
            Namespace = self.namespace,
            MetricName = self.metric_name,
            Dimensions = dimensions,
            Statistics = ["Average"],
            StartTime = now - datetime.timedelta(days = 1),
            EndTime = now,
            Period = 60,
        )
        items = []
        for elem in ls["Datapoints"]:
            items.append([
                elem["Timestamp"],
                elem["Average"],
                elem["Unit"],
            ])
        items.sort()
        return items

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

    def alt(self):
        return GlueTableAltPage(self.database_name, self.table_name)

    def object(self):
        client = session.client("glue", region_name = region)
        meta = client.get_table(
            DatabaseName = self.database_name,
            Name = self.table_name,
        )
        #del(meta["ResponseMetadata"])
        return meta["Table"]

class GlueTableAltPage(MenuPage):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name

    def items(self):
        return [
            ("partitions", GlueTableAltPartitionsPage),
        ]

    def detailPage(self, item):
        return item[1](self.database_name, self.table_name)

class GlueTableAltPartitionsPage(TablePage):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("glue", region_name = region)
        ls = client.get_partitions(
            DatabaseName = self.database_name,
            TableName = self.table_name,
        )
        items = []
        for elem in ls["Partitions"]:
            values = "/".join(elem["Values"])
            items.append([values])
        return items

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
            ("role", ),
        ]

    def detailPage(self, item):
        if item[0] == "role":
            client = session.client("glue", region_name = region)
            info = client.get_job(
                JobName = self.job_name,
            )
            role_name = info["Job"]["Role"]
            return IAMRolePage(role_name)
        else:
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

    def canonical(self):
        return ["iam", "roles", self.role_name]

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
    def canonical(self):
        return ["lambda"]

    def items(self):
        return [
            ("functions", LambdaFunctionsPage),
        ]

class LambdaFunctionsPage(TablePage):
    def canonical(self):
        return ["lambda", "functions"]

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

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return LambdaFunctionPage(arg)

class LambdaFunctionPage(MenuPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name]

    def items(self):
        return [
            ("code", LambdaFunctionCodePage),
            ("configuration", LambdaFunctionConfigurationPage),
            ("aliases", LambdaFunctionAliasesPage),
            ("metrics", LambdaFunctionMetricsPage),
        ]

    def detailPage(self, item):
        return item[1](self.function_name)

class LambdaFunctionCodePage(ObjectPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "code"]

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

    def canonical(self):
        return ["lambda", "functions", self.function_name, "configuration"]

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

    def canonical(self):
        return ["lambda", "functions", self.function_name, "aliases"]

    #def object(self):
    #    client = session.client("lambda", region_name = region)
    #    meta = client.list_aliases(
    #        FunctionName = self.function_name,
    #    )
    #    del(meta["ResponseMetadata"])
    #    return meta

class LambdaFunctionMetricsPage(MenuPage):
    def __init__(self, function_name):
        self.function_name = function_name

    def canonical(self):
        return ["lambda", "functions", self.function_name, "metrics"]

    def items(self):
        return [
            ("duration", ),
            ("errors", ),
            ("invocations", ),
            ("throttles", ),
        ]

    def detailPage(self, item):
        return CloudWatchMetricsNamespaceMetricDimensionPage("AWS/Lambda", item[0].title(), "FunctionName:{}".format(self.function_name))

####################################################################################################

class RDSPage(MenuPage):
    def canonical(self):
        return ["rds"]

    def items(self):
        return [
            ("databases", RDSDatabasesPage),
            ("snapshots", ),
        ]

    def detailPage(self, item):
        if item[0] == "snapshots":
            return RDSSnapshotsPage(None)
        else:
            return item[1]()

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
            ("vpc", ),
            ("snapshots", ),
        ]

    def detailPage(self, item):
        if item[0] == "vpc":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_instances(
                DBInstanceIdentifier = self.database_instance_identifier,
            )
            info = ls["DBInstances"][0]
            vpc_id = info["DBSubnetGroup"]["VpcId"]
            return VPCVPCPage(vpc_id)
        elif item[0] == "snapshots":
            return RDSSnapshotsPage(self.database_instance_identifier)
        else:
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

class RDSSnapshotsPage(TablePage):
    # database_instance_identifier はNone可
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        if self.database_instance_identifier == None:
            return ["rds", "snapshots"]
        else:
            return ["rds", "databases", self.database_instance_identifier, "--alt", "snapshots"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("rds", region_name = region)
        if self.database_instance_identifier == None:
            ls = client.describe_db_snapshots(
            )
        else:
            ls = client.describe_db_snapshots(
                DBInstanceIdentifier = self.database_instance_identifier,
            )
        items = []
        for elem in ls["DBSnapshots"]:
            if "SnapshotCreateTime" in elem:
                create_time = elem["SnapshotCreateTime"]
            else:
                create_time = "-" # creating では SnapshotCreateTime の要素がない
            if self.database_instance_identifier == None:
                items.append([elem["DBSnapshotIdentifier"], elem["DBInstanceIdentifier"], create_time])
            else:
                items.append([elem["DBSnapshotIdentifier"], create_time])
        return items

    def detailPage(self, item):
        return RDSSnapshotPage(item[0])

class RDSSnapshotPage(ObjectPage):
    def __init__(self, snapshot_identifier):
        self.snapshot_identifier = snapshot_identifier

    def canonical(self):
        return ["rds", "snapshots", self.snapshot_identifier]

    def alt(self):
        return RDSSnapshotAltPage(self.snapshot_identifier)

    def object(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_snapshots(
            DBSnapshotIdentifier = self.snapshot_identifier,
        )
        return ls["DBSnapshots"][0]

class RDSSnapshotAltPage(MenuPage):
    def __init__(self, snapshot_identifier):
        self.snapshot_identifier = snapshot_identifier

    def canonical(self):
        return ["rds", "snapshots", self.snapshot_identifier, "--alt"]

    def items(self):
        return [
            ("database", ),
            ("vpc", ),
        ]

    def detailPage(self, item):
        if item[0] == "database":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_snapshots(
                DBSnapshotIdentifier = self.snapshot_identifier,
            )
            info = ls["DBSnapshots"][0]
            database_instance_identifier = info["DBInstanceIdentifier"]
            return RDSDatabasePage(database_instance_identifier)
        elif item[0] == "vpc":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_snapshots(
                DBSnapshotIdentifier = self.snapshot_identifier,
            )
            info = ls["DBSnapshots"][0]
            vpc_id = info["VpcId"]
            return VPCVPCPage(vpc_id)
        else:
            return item[1](self.snapshot_identifier)

####################################################################################################

class RedshiftPage(MenuPage):
    def canonical(self):
        return ["redshift"]

    def items(self):
        return [("clusters", RedshiftClustersPage)]

class RedshiftClustersPage(TablePage):
    def canonical(self):
        return ["redshift", "clusters"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters()
        items = []
        for elem in ls["Clusters"]:
            if "Endpoint" in elem and "Address" in elem["Endpoint"]:
                endpoint = elem["Endpoint"]["Address"]
            else:
                endpoint = "-"
            # creatingのクラスタは Endpoint の要素がない
            # deletingのクラスタは Endpoint の要素はあるけど Address の要素がない
            items.append([elem["ClusterIdentifier"], endpoint])
        return items

    def detailPage(self, item):
        return RedshiftClusterPage(item[0])

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return RedshiftClusterPage(arg)

class RedshiftClusterPage(TablePage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier]

    def alt(self):
        return RedshiftClusterAltPage(self.cluster_identifier)

    def see_also(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        info = ls["Clusters"][0]
        if "Endpoint" in info and "Address" in info["Endpoint"]:
            endpoint = info["Endpoint"]["Address"]
            port = str(info["Endpoint"]["Port"])
            user = info["MasterUsername"]
            dbname = info["DBName"]
            cmd = [
                "PGPASSWORD=XXXX",
                "psql",
                "-h", endpoint,
                "-p", port,
                "-U", user,
                "-d", dbname]
            return [cmd]
        else:
            return None

class RedshiftClusterAltPage(MenuPage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt"]

    def items(self):
        return [
            ("info", RedshiftClusterInfoPage),
            ("vpc", ),
            ("roles", RedshiftClusterRolesPage),
        ]

    def detailPage(self, item):
        if item[0] == "vpc":
            client = session.client("redshift", region_name = region)
            ls = client.describe_clusters(
                ClusterIdentifier = self.cluster_identifier,
            )
            info = ls["Clusters"][0]
            vpc_id = info["VpcId"]
            return VPCVPCPage(vpc_id)
        else:
            return item[1](self.cluster_identifier)

class RedshiftClusterInfoPage(ObjectPage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt", "info"]

    def object(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        return ls["Clusters"][0]

class RedshiftClusterRolesPage(TablePage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt", "roles"]

    def items(self):
        client = session.client("sts")
        info = client.get_caller_identity()
        account = info["Account"]
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        items = []
        for elem in ls["Clusters"][0]["IamRoles"]:
            arn = elem["IamRoleArn"]
            arn2 = arn.split(":")
            if arn2[4] == account:
                if arn2[5].startswith("role/"):
                    items.append([arn2[5][5:]])
        return items

    def detailPage(self, item):
        return IAMRolePage(item[0])

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

class STSPage(MenuPage):
    def canonical(self):
        return ["sts"]

    def items(self):
        return [("caller", STSCallerPage)]

class STSCallerPage(ObjectPage):
    def canonical(self):
        return ["sts", "caller"]

    def object(self):
        client = session.client("sts")
        info = client.get_caller_identity()
        del(info["ResponseMetadata"])
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
        return [
            ("vpcs", VPCVPCsPage),
            ("subnets", ),
        ]

    def detailPage(self, item):
        if item[0] == "subnets":
            return VPCSubnetsPage(None)
        else:
            return item[1]()

class VPCVPCsPage(TablePage):
    def canonical(self):
        return ["vpc", "vpcs"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_vpcs()
        items = []
        for elem in ls["Vpcs"]:
            items.append([elem["VpcId"]])
        return items

    def detailPage(self, item):
        return VPCVPCPage(item[0])

class VPCVPCPage(ObjectPage):
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        return ["vpc", "vpcs", self.vpc_id]

    def alt(self):
        return VPCVPCAltPage(self.vpc_id)

    def object(self):
        client = session.client("ec2", region_name = region)
        info = client.describe_vpcs(
            VpcIds = [self.vpc_id],
        )
        return info["Vpcs"][0]

class VPCVPCAltPage(MenuPage):
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        return ["vpc", "vpcs", self.vpc_id, "--alt"]

    def items(self):
        return [
            ("subnets", VPCSubnetsPage),
        ]

    def detailPage(self, item):
        return item[1](self.vpc_id)

class VPCSubnetsPage(TablePage):
    # vpc_id はNone可
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        if self.vpc_id == None:
            return ["vpc", "subnets"]
        else:
            return ["vpc", "vpcs", self.vpc_id, "--alt", "subnets"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2", region_name = region)
        if self.vpc_id == None:
            ls = client.describe_subnets(
            )
        else:
            ls = client.describe_subnets(
                Filters = [
                    { "Name": "vpc-id", "Values": [self.vpc_id] },
                ],
            )
        items = []
        for elem in ls["Subnets"]:
            if self.vpc_id == None:
                items.append([elem["SubnetId"], elem["VpcId"], elem["AvailabilityZone"], elem["CidrBlock"]])
            else:
                items.append([elem["SubnetId"], elem["AvailabilityZone"], elem["CidrBlock"]])
        return items

    def detailPage(self, item):
        return VPCSubnetPage(item[0])

class VPCSubnetPage(ObjectPage):
    def __init__(self, subnet_id):
        self.subnet_id = subnet_id

    def canonical(self):
        return ["vpc", "subnets", self.subnet_id]

    def object(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_subnets(
            Filters = [
                { "Name": "subnet-id", "Values": [self.subnet_id] },
            ],
        )
        return ls["Subnets"][0]

####################################################################################################

GlobalPage().exec(args)

####################################################################################################
