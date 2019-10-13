
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class RDSPage(MenuPage):
    def canonical(self):
        return ["rds"]

    def items(self):
        return [
            ("databases", RDSDatabasesPage),
            ("snapshots", ),
        ]

    def detailPage(self, item):
        if item[0] == "snapshots":
            return RDSSnapshotsPage(None)
        else:
            return item[1]()

class RDSDatabasesPage(TablePage):
    def canonical(self):
        return ["rds", "databases"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_instances()
        items = []
        for elem in ls["DBInstances"]:
            items.append([elem["DBInstanceIdentifier"], elem["Endpoint"]["Address"]])
        return items

    def detailPage(self, item):
        return RDSDatabasePage(item[0])

class RDSDatabasePage(TablePage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier]

    def alt(self):
        return RDSDatabaseAltPage(self.database_instance_identifier)

class RDSDatabaseAltPage(MenuPage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier, "--alt"]

    def items(self):
        return [
            ("info", RDSDatabaseInfoPage),
            ("vpc", ),
            ("snapshots", ),
        ]

    def detailPage(self, item):
        if item[0] == "vpc":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_instances(
                DBInstanceIdentifier = self.database_instance_identifier,
            )
            info = ls["DBInstances"][0]
            vpc_id = info["DBSubnetGroup"]["VpcId"]
            return VPCVPCPage(vpc_id)
        elif item[0] == "snapshots":
            return RDSSnapshotsPage(self.database_instance_identifier)
        else:
            return item[1](self.database_instance_identifier)

class RDSDatabaseInfoPage(ObjectPage):
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        return ["rds", "databases", self.database_instance_identifier, "--alt", "info"]

    def object(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_instances(
            DBInstanceIdentifier = self.database_instance_identifier,
        )
        return ls["DBInstances"][0]

class RDSSnapshotsPage(TablePage):
    # database_instance_identifier はNone可
    def __init__(self, database_instance_identifier):
        self.database_instance_identifier = database_instance_identifier

    def canonical(self):
        if self.database_instance_identifier == None:
            return ["rds", "snapshots"]
        else:
            return ["rds", "databases", self.database_instance_identifier, "--alt", "snapshots"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("rds", region_name = region)
        if self.database_instance_identifier == None:
            ls = client.describe_db_snapshots(
            )
        else:
            ls = client.describe_db_snapshots(
                DBInstanceIdentifier = self.database_instance_identifier,
            )
        items = []
        for elem in ls["DBSnapshots"]:
            if "SnapshotCreateTime" in elem:
                create_time = elem["SnapshotCreateTime"]
            else:
                create_time = "-" # creating では SnapshotCreateTime の要素がない
            if self.database_instance_identifier == None:
                items.append([elem["DBSnapshotIdentifier"], elem["DBInstanceIdentifier"], create_time])
            else:
                items.append([elem["DBSnapshotIdentifier"], create_time])
        return items

    def detailPage(self, item):
        return RDSSnapshotPage(item[0])

class RDSSnapshotPage(ObjectPage):
    def __init__(self, snapshot_identifier):
        self.snapshot_identifier = snapshot_identifier

    def canonical(self):
        return ["rds", "snapshots", self.snapshot_identifier]

    def alt(self):
        return RDSSnapshotAltPage(self.snapshot_identifier)

    def object(self):
        client = session.client("rds", region_name = region)
        ls = client.describe_db_snapshots(
            DBSnapshotIdentifier = self.snapshot_identifier,
        )
        return ls["DBSnapshots"][0]

class RDSSnapshotAltPage(MenuPage):
    def __init__(self, snapshot_identifier):
        self.snapshot_identifier = snapshot_identifier

    def canonical(self):
        return ["rds", "snapshots", self.snapshot_identifier, "--alt"]

    def items(self):
        return [
            ("database", ),
            ("vpc", ),
        ]

    def detailPage(self, item):
        if item[0] == "database":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_snapshots(
                DBSnapshotIdentifier = self.snapshot_identifier,
            )
            info = ls["DBSnapshots"][0]
            database_instance_identifier = info["DBInstanceIdentifier"]
            return RDSDatabasePage(database_instance_identifier)
        elif item[0] == "vpc":
            client = session.client("rds", region_name = region)
            ls = client.describe_db_snapshots(
                DBSnapshotIdentifier = self.snapshot_identifier,
            )
            info = ls["DBSnapshots"][0]
            vpc_id = info["VpcId"]
            return VPCVPCPage(vpc_id)
        else:
            return item[1](self.snapshot_identifier)

####################################################################################################

