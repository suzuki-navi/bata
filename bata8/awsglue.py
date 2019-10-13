
import boto3
import botocore

from bata8.lib import *

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

