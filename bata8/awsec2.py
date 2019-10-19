
import boto3
import botocore

from bata8.lib import *

from bata8.awsvpc import *

####################################################################################################

class EC2Page(MenuPage):
    def items(self):
        return [
            ("instances", EC2InstancesPage),
        ]

class EC2InstancesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_instances(
        )
        items = []
        for elem1 in ls["Reservations"]:
            for elem in elem1["Instances"]:
                pri_ip = "-"
                if "PrivateIpAddress" in elem:
                    pri_ip = elem["PrivateIpAddress"]
                pub_ip = "-"
                if "PublicIpAddress" in elem:
                    pub_ip = elem["PublicIpAddress"]
                tags = tagsToLtsvLike(elem["Tags"])
                items.append([elem["InstanceId"], elem["InstanceType"], pri_ip, pub_ip, tags])
        return items

    def detailPage(self, item):
        return EC2InstancePage(item[0])

class EC2InstancePage(ObjectPage):
    def __init__(self, instance_id):
        self.instance_id = instance_id

    def alt(self):
        return EC2InstanceAltPage(self.instance_id)

    def object(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_instances(
            InstanceIds = [ self.instance_id ],
        )
        return ls["Reservations"][0]["Instances"][0]

class EC2InstanceAltPage(MenuPage):
    def __init__(self, instance_id):
        self.instance_id = instance_id

    def items(self):
        return [
            ("vpc", ),
        ]

    def detailPage(self, item):
        if item[0] == "vpc":
            client = session.client("ec2", region_name = region)
            ls = client.describe_instances(
                InstanceIds = [ self.instance_id ],
            )
            vpc_id = ls["Reservations"][0]["Instances"][0]["VpcId"]
            return VPCVPCPage(vpc_id)
        else:
            return item[1](self.instance_id)

####################################################################################################

