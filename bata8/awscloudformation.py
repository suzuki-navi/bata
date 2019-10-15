
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class CloudFormationPage(MenuPage):
    def canonical(self):
        return ["cloudformation"]

    def items(self):
        return [
            ("stacks", CloudFormationStacksPage),
        ]

class CloudFormationStacksPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("cloudformation", region_name = region)
        #ls = client.list_stacks(
        #)
        #items = []
        #for elem in ls["StackSummaries"]:
        #    items.append([elem["StackName"], elem["CreationTime"]])
        ls = client.describe_stacks(
        )
        items = []
        for elem in ls["Stacks"]:
            items.append([elem["StackName"], elem["CreationTime"]])
        return items

    def detailPage(self, item):
        return CloudFormationStackPage(item[0])

class CloudFormationStackPage(ObjectPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def object(self):
        client = session.client("cloudformation", region_name = region)
        info = client.describe_stacks(
            StackName = self.stack_name,
        )
        return info["Stacks"][0]

####################################################################################################

