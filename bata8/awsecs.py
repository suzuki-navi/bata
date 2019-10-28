
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class ECSPage(MenuPage):
    def canonical(self):
        return ["ecs"]

    def items(self):
        return [
            ("clusters", ECSClustersPage),
            ("tasks", ECSTasksPage),
        ]

class ECSClustersPage(TablePage):
    def canonical(self):
        return ["ecs", "clusters"]

    def nameColIdx(self):
        return 0

    def items(self):
        account = fetch_account_id()
        client = session.client("ecs", region_name = region)
        ls = client.list_clusters(
        )
        items = []
        for elem in ls["clusterArns"]:
            cols = elem.split(":", 5)
            if cols[0] == "arn" and cols[1] == "aws" and cols[2] == "ecs" and cols[3] == region and cols[4] == account:
                if cols[5].startswith("cluster/"):
                    name = cols[5][8:]
                    items.append([name])
        return items

    def detailPage(self, item):
        return ECSClusterPage(item[0])

class ECSClusterPage(ObjectPage):
    def __init__(self, cluster_name):
        self.cluster_name = cluster_name

    def canonical(self):
        return ["ecs", "clusters", self.cluster_name]

    def arn(self):
        return "arn:aws:ecs:{}:{}:cluster/{}".format(session.region_name, fetch_account_id(), self.cluster_name)

    def alt(self):
        return ECSClusterAltPage(self.cluster_name)

    def object(self):
        client = session.client("ecs", region_name = region)
        info = client.describe_clusters(
            clusters = [ self.cluster_name ],
        )
        return info["clusters"][0]

class ECSClusterAltPage(MenuPage):
    def __init__(self, cluster_name):
        self.cluster_name = cluster_name

    def canonical(self):
        return ["ecs", "clusters", self.cluster_name, "--alt"]

    def items(self):
        return [
        ]

    def detailPage(self, item):
        return item[1](self.cluster_name)


class ECSTasksPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        account = fetch_account_id()
        client = session.client("ecs", region_name = region)
        ls = client.list_task_definitions(
        )
        items = []
        for elem in ls["taskDefinitionArns"]:
            cols = elem.split(":", 5)
            if cols[0] == "arn" and cols[1] == "aws" and cols[2] == "ecs" and cols[3] == region and cols[4] == account:
                if cols[5].startswith("task-definition/"):
                    name = cols[5][16:]
            items.append([elem])
        return items

    #def detailPage(self, item):
    #    return ECSTaskPage(item[0])

####################################################################################################

