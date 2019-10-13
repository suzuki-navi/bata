
import boto3
import botocore

from bata8.lib import *

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

