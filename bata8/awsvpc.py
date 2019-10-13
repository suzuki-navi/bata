
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class VPCPage(MenuPage):
    def canonical(self):
        return ["vpc"]

    def items(self):
        return [
            ("vpcs", VPCVPCsPage),
            ("subnets", ),
        ]

    def detailPage(self, item):
        if item[0] == "subnets":
            return VPCSubnetsPage(None)
        else:
            return item[1]()

class VPCVPCsPage(TablePage):
    def canonical(self):
        return ["vpc", "vpcs"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_vpcs()
        items = []
        for elem in ls["Vpcs"]:
            items.append([elem["VpcId"]])
        return items

    def detailPage(self, item):
        return VPCVPCPage(item[0])

class VPCVPCPage(ObjectPage):
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        return ["vpc", "vpcs", self.vpc_id]

    def alt(self):
        return VPCVPCAltPage(self.vpc_id)

    def object(self):
        client = session.client("ec2", region_name = region)
        info = client.describe_vpcs(
            VpcIds = [self.vpc_id],
        )
        return info["Vpcs"][0]

class VPCVPCAltPage(MenuPage):
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        return ["vpc", "vpcs", self.vpc_id, "--alt"]

    def items(self):
        return [
            ("subnets", VPCSubnetsPage),
        ]

    def detailPage(self, item):
        return item[1](self.vpc_id)

class VPCSubnetsPage(TablePage):
    # vpc_id はNone可
    def __init__(self, vpc_id):
        self.vpc_id = vpc_id

    def canonical(self):
        if self.vpc_id == None:
            return ["vpc", "subnets"]
        else:
            return ["vpc", "vpcs", self.vpc_id, "--alt", "subnets"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("ec2", region_name = region)
        if self.vpc_id == None:
            ls = client.describe_subnets(
            )
        else:
            ls = client.describe_subnets(
                Filters = [
                    { "Name": "vpc-id", "Values": [self.vpc_id] },
                ],
            )
        items = []
        for elem in ls["Subnets"]:
            if self.vpc_id == None:
                items.append([elem["SubnetId"], elem["VpcId"], elem["AvailabilityZone"], elem["CidrBlock"]])
            else:
                items.append([elem["SubnetId"], elem["AvailabilityZone"], elem["CidrBlock"]])
        return items

    def detailPage(self, item):
        return VPCSubnetPage(item[0])

class VPCSubnetPage(ObjectPage):
    def __init__(self, subnet_id):
        self.subnet_id = subnet_id

    def canonical(self):
        return ["vpc", "subnets", self.subnet_id]

    def object(self):
        client = session.client("ec2", region_name = region)
        ls = client.describe_subnets(
            Filters = [
                { "Name": "subnet-id", "Values": [self.subnet_id] },
            ],
        )
        return ls["Subnets"][0]

####################################################################################################

