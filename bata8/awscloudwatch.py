
import boto3
import botocore

from bata8.lib import *

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
            items.append([elem["Name"], elem["ScheduleExpression"]])
        return items

    def detailPage(self, item):
        return CloudWatchEventsRulePage(item[0])

class CloudWatchEventsRulePage(MenuPage):
    def __init__(self, event_name):
        self.event_name = event_name

    def items(self):
        return [
            ("info", CloudWatchEventsRuleInfoPage),
            ("targets", CloudWatchEventsRuleTargetsPage),
        ]

    def detailPage(self, item):
        return item[1](self.event_name)

class CloudWatchEventsRuleInfoPage(ObjectPage):
    def __init__(self, event_name):
        self.event_name = event_name

    def object(self):
        client = session.client("events", region_name = region)
        meta = client.describe_rule(
            Name = self.event_name,
        )
        del(meta["ResponseMetadata"])
        return meta

class CloudWatchEventsRuleTargetsPage(TablePage):
    def __init__(self, event_name):
        self.event_name = event_name

    def items(self):
        client = session.client("events", region_name = region)
        ls = client.list_targets_by_rule(
            Rule = self.event_name,
        )
        items = []
        for elem in ls["Targets"]:
            items.append([elem["Id"], elem["Arn"]])
        return items

    def detailPage(self, item):
        return CloudWatchEventsRuleTargetPage(self.event_name, item[0])

class CloudWatchEventsRuleTargetPage(ObjectPage):
    def __init__(self, event_name, target_id):
        self.event_name = event_name
        self.target_id = target_id

    def object(self):
        client = session.client("events", region_name = region)
        ls = client.list_targets_by_rule(
            Rule = self.event_name,
        )
        items = []
        for elem in ls["Targets"]:
            if elem["Id"] == self.target_id:
                return elem

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

