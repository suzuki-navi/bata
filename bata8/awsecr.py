
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

