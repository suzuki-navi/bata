
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class RedshiftPage(MenuPage):
    def canonical(self):
        return ["redshift"]

    def items(self):
        return [("clusters", RedshiftClustersPage)]

class RedshiftClustersPage(TablePage):
    def canonical(self):
        return ["redshift", "clusters"]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters()
        items = []
        for elem in ls["Clusters"]:
            if "Endpoint" in elem and "Address" in elem["Endpoint"]:
                endpoint = elem["Endpoint"]["Address"]
            else:
                endpoint = "-"
            # creatingのクラスタは Endpoint の要素がない
            # deletingのクラスタは Endpoint の要素はあるけど Address の要素がない
            items.append([elem["ClusterIdentifier"], endpoint])
        return items

    def detailPage(self, item):
        return RedshiftClusterPage(item[0])

    def dig(self, arg):
        if re.match("\\A[0-9]*\\Z", arg):
            return super().dig(arg)
        return RedshiftClusterPage(arg)

class RedshiftClusterPage(TablePage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier]

    def alt(self):
        return RedshiftClusterAltPage(self.cluster_identifier)

    def see_also(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        info = ls["Clusters"][0]
        if "Endpoint" in info and "Address" in info["Endpoint"]:
            endpoint = info["Endpoint"]["Address"]
            port = str(info["Endpoint"]["Port"])
            user = info["MasterUsername"]
            dbname = info["DBName"]
            cmd = [
                "PGPASSWORD=XXXX",
                "psql",
                "-h", endpoint,
                "-p", port,
                "-U", user,
                "-d", dbname]
            return [cmd]
        else:
            return None

class RedshiftClusterAltPage(MenuPage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt"]

    def items(self):
        return [
            ("info", RedshiftClusterInfoPage),
            ("vpc", ),
            ("roles", RedshiftClusterRolesPage),
        ]

    def detailPage(self, item):
        if item[0] == "vpc":
            client = session.client("redshift", region_name = region)
            ls = client.describe_clusters(
                ClusterIdentifier = self.cluster_identifier,
            )
            info = ls["Clusters"][0]
            vpc_id = info["VpcId"]
            return VPCVPCPage(vpc_id)
        else:
            return item[1](self.cluster_identifier)

class RedshiftClusterInfoPage(ObjectPage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt", "info"]

    def object(self):
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        return ls["Clusters"][0]

class RedshiftClusterRolesPage(TablePage):
    def __init__(self, cluster_identifier):
        self.cluster_identifier = cluster_identifier

    def canonical(self):
        return ["redshift", "clusters", self.cluster_identifier, "--alt", "roles"]

    def items(self):
        client = session.client("sts")
        info = client.get_caller_identity()
        account = info["Account"]
        client = session.client("redshift", region_name = region)
        ls = client.describe_clusters(
            ClusterIdentifier = self.cluster_identifier,
        )
        items = []
        for elem in ls["Clusters"][0]["IamRoles"]:
            arn = elem["IamRoleArn"]
            arn2 = arn.split(":")
            if arn2[4] == account:
                if arn2[5].startswith("role/"):
                    items.append([arn2[5][5:]])
        return items

    def detailPage(self, item):
        return IAMRolePage(item[0])

####################################################################################################

