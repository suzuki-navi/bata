
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class SageMakerPage(MenuPage):
    def canonical(self):
        return ["sagemaker"]

    def items(self):
        return [
            ("notebook", SageMakerNotebookPage),
            ("training", SageMakerTrainingPage),
            ("models", SageMakerModelsPage),
        ]

class SageMakerNotebookPage(MenuPage):
    def canonical(self):
        return ["sagemaker", "notebook"]

    def items(self):
        return [
            ("instances", SageMakerNotebookInstancesPage),
        ]

class SageMakerNotebookInstancesPage(TablePage):
    def canonical(self):
        return ["sagemaker", "notebook", "instances"]

    def items(self):
        client = session.client("sagemaker", region_name = region)
        ls = client.list_notebook_instances(
        )
        items = []
        for elem in ls["NotebookInstances"]:
            items.append([elem["NotebookInstanceName"]])
        return items

    def detailPage(self, item):
        return SageMakerNotebookInstancePage(item[0])

class SageMakerNotebookInstancePage(ObjectPage):
    def __init__(self, instance_name):
        self.instance_name = instance_name

    def canonical(self):
        return ["sagemaker", "notebook", "instances", self.instance_name]

    def arn(self):
        return "arn:aws:sagemaker:{}:{}:notebook-instance/{}".format(session.region_name, fetch_account_id(), self.instance_name)

    def object(self):
        client = session.client("sagemaker", region_name = region)
        info = client.describe_notebook_instance(
            NotebookInstanceName = self.instance_name,
        )
        del(info["ResponseMetadata"])
        return info

    @classmethod
    def page_from_arn(cls, arn, account_id, region):
        match = re.match(f"\\Aarn:aws:sagemaker:{region}:{account_id}:notebook-instance/(.+)\\Z", arn)
        if match:
            return SageMakerNotebookInstancePage(match.group(1))

class SageMakerTrainingPage(MenuPage):
    def canonical(self):
        return ["sagemaker", "training"]

    def items(self):
        return [
            ("jobs", SageMakerTrainingJobsPage),
        ]

class SageMakerTrainingJobsPage(TablePage):
    def canonical(self):
        return ["sagemaker", "training", "jobs"]

    def items(self):
        client = session.client("sagemaker", region_name = region)
        ls = client.list_training_jobs(
        )
        items = []
        for elem in ls["TrainingJobSummaries"]:
            items.append([elem["TrainingJobName"], elem["CreationTime"]])
        return items

    def detailPage(self, item):
        return SageMakerTrainingJobPage(item[0])

class SageMakerTrainingJobPage(ObjectPage):
    def __init__(self, job_name):
        self.job_name = job_name

    def canonical(self):
        return ["sagemaker", "training", "jobs", self.job_name]

    def object(self):
        client = session.client("sagemaker", region_name = region)
        info = client.describe_training_job(
            TrainingJobName = self.job_name,
        )
        del(info["ResponseMetadata"])
        return info

class SageMakerModelsPage(TablePage):
    def canonical(self):
        return ["sagemaker", "models"]

    def items(self):
        client = session.client("sagemaker", region_name = region)
        ls = client.list_models(
        )
        items = []
        for elem in ls["Models"]:
            items.append([elem["ModelName"]])
        return items

    def detailPage(self, item):
        return SageMakerModelPage(item[0])

class SageMakerModelPage(ObjectPage):
    def __init__(self, model_name):
        self.model_name = model_name

    def canonical(self):
        return ["sagemaker", "models", self.model_name]

    def arn(self):
        return "arn:aws:sagemaker:{}:{}:model/{}".format(session.region_name, fetch_account_id(), self.model_name)

    def object(self):
        client = session.client("sagemaker", region_name = region)
        info = client.describe_model(
            ModelName = self.model_name,
        )
        del(info["ResponseMetadata"])
        return info

    @classmethod
    def page_from_arn(cls, arn, account_id, region):
        match = re.match(f"\\Aarn:aws:sagemaker:{region}:{account_id}:model/(.+)\\Z", arn)
        if match:
            return SageMakerModelPage(match.group(1))

