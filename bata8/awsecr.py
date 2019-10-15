
import boto3
import botocore

from bata8.lib import *

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
        return ECRRepositoryPage(item[0])

class ECRRepositoryPage(ObjectPage):
    def __init__(self, repository_name):
        self.repository_name = repository_name

    def alt(self):
        return ECRRepositoryAltPage(self.repository_name)

    def object(self):
        client = session.client("ecr", region_name = region)
        ls = client.describe_repositories(
            repositoryNames = [ self.repository_name ],
        )
        return ls["repositories"][0]

class ECRRepositoryAltPage(MenuPage):
    def __init__(self, repository_name):
        self.repository_name = repository_name

    def items(self):
        return [
            ("images", ECRRepositoryImagesPage),
        ]

    def detailPage(self, item):
        return item[1](self.repository_name)

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
        info = client.describe_images(
            repositoryName = self.repository_name,
            imageIds = [ { "imageTag": self.image_tag } ],
        )
        return info["imageDetails"][0]

####################################################################################################

