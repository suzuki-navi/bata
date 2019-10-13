
import boto3
import botocore

from bata8.lib import *

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

