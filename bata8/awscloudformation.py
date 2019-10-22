
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
    def canonical(self):
        return ["cloudformation", "stacks"]

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

class CloudFormationStackPage(MenuPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name]

    def items(self):
        return [
            ("info", CloudFormationStackInfoPage),
            ("template", CloudFormationStackTemplatePage),
        ]

    def detailPage(self, item):
        return item[1](self.stack_name)

class CloudFormationStackInfoPage(ObjectPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name, "info"]

    def object(self):
        client = session.client("cloudformation", region_name = region)
        info = client.describe_stacks(
            StackName = self.stack_name,
        )
        return info["Stacks"][0]

class CloudFormationStackTemplatePage(ObjectPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name, "template"]

    def alt(self):
        return CloudFormationStackTemplateAltPage(self.stack_name)

    def object(self):
        client = session.client("cloudformation", region_name = region)
        info = client.get_template(
            StackName = self.stack_name,
        )
        return info["TemplateBody"]

class CloudFormationStackTemplateAltPage(MenuPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name, "template", "--alt"]

    def items(self):
        return [
            ("summary", CloudFormationStackTemplateSummaryPage),
            ("stages", CloudFormationStackTemplateStagesPage),
        ]

    def detailPage(self, item):
        return item[1](self.stack_name)

class CloudFormationStackTemplateSummaryPage(ObjectPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name, "template", "--alt", "summary"]

    def object(self):
        client = session.client("cloudformation", region_name = region)
        info = client.get_template_summary(
            StackName = self.stack_name,
        )
        del(info["ResponseMetadata"])
        return info

class CloudFormationStackTemplateStagesPage(ObjectPage):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def canonical(self):
        return ["cloudformation", "stacks", self.stack_name, "template", "--alt", "stages"]

    def object(self):
        client = session.client("cloudformation", region_name = region)
        info = client.get_template(
            StackName = self.stack_name,
        )
        return " ".join(info["StagesAvailable"])

####################################################################################################

