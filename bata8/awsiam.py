
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class IAMPage(MenuPage):
    def items(self):
        return [
            ("users", IAMUsersPage),
            ("roles", IAMRolesPage),
            ("policies", IAMPoliciesPage),
        ]

class IAMUsersPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_users(
        )
        items = []
        for elem in ls["Users"]:
            items.append([elem["UserName"]])
        return items

    def detailPage(self, item):
        return IAMUserPage(item[0])

class IAMUserPage(ObjectPage):
    def __init__(self, user_name):
        self.user_name = user_name

    def object(self):
        client = session.client("iam")
        meta = client.get_user(
            UserName = self.user_name,
        )
        return meta["User"]

class IAMRolesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_roles(
        )
        items = []
        for elem in ls["Roles"]:
            items.append([elem["RoleName"]])
        return items

    def detailPage(self, item):
        return IAMRolePage(item[0])

class IAMRolePage(TablePage):
    def __init__(self, role_name):
        self.role_name = role_name

    def alt(self):
        return IAMRoleAltPage(self.role_name)

    def canonical(self):
        return ["iam", "roles", self.role_name]

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        items = []
        ls = client.list_role_policies(
            RoleName = self.role_name,
        )
        for elem in ls["PolicyNames"]:
            items.append([elem, "inline"])
        ls = client.list_attached_role_policies(
            RoleName = self.role_name,
        )
        for elem in ls["AttachedPolicies"]:
            items.append([elem["PolicyName"], "attached"])
        return items

class IAMRoleAltPage(MenuPage):
    def __init__(self, role_name):
        self.role_name = role_name

    def items(self):
        return [
            ("info", IAMRoleInfoPage),
        ]

    def detailPage(self, item):
        return item[1](self.role_name)

class IAMRoleInfoPage(ObjectPage):
    def __init__(self, role_name):
        self.role_name = role_name

    def object(self):
        client = session.client("iam")
        meta = client.get_role(
            RoleName = self.role_name,
        )
        return meta["Role"]

class IAMPoliciesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_policies(
            Scope = "All",
            OnlyAttached = False,
            MaxItems = 1000,
        )
        items = []
        for elem in ls["Policies"]:
            items.append([elem["PolicyName"], elem["Arn"]])
        return items

    def detailPage(self, item):
        return IAMPolicyPage(item[0], item[1])

class IAMPolicyPage(ObjectPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def alt(self):
        return IAMPolicyAltPage(self.policy_name, self.policy_arn)

    def object(self):
        client = session.client("iam")
        policy_meta = client.get_policy(
            PolicyArn = self.policy_arn,
        )
        version_id = policy_meta["Policy"]["DefaultVersionId"]
        version_meta = client.get_policy_version(
            PolicyArn = self.policy_arn,
            VersionId = version_id,
        )
        return version_meta["PolicyVersion"]["Document"]

class IAMPolicyAltPage(MenuPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def items(self):
        return [
            ("info", IAMPolicyInfoPage),
            ("versions", IAMPolicyVersionsPage),
        ]

    def detailPage(self, item):
        return item[1](self.policy_name, self.policy_arn)

class IAMPolicyInfoPage(ObjectPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def object(self):
        client = session.client("iam")
        meta = client.get_policy(
            PolicyArn = self.policy_arn,
        )
        return meta["Policy"]

class IAMPolicyVersionsPage(TablePage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_policy_versions(
            PolicyArn = self.policy_arn,
        )
        items = []
        for elem in ls["Versions"]:
            items.append([elem["VersionId"], elem["IsDefaultVersion"]])
        return items

    def detailPage(self, item):
        return IAMPolicyVersionPage(self.policy_name, self.policy_arn, item[0])

class IAMPolicyVersionPage(ObjectPage):
    def __init__(self, policy_name, policy_arn, policy_version_id):
        self.policy_name = policy_name
        self.policy_arn = policy_arn
        self.policy_version_id = policy_version_id

    def object(self):
        client = session.client("iam")
        meta = client.get_policy_version(
            PolicyArn = self.policy_arn,
            VersionId = self.policy_version_id,
        )
        return meta["PolicyVersion"]

####################################################################################################

class STSPage(MenuPage):
    def canonical(self):
        return ["sts"]

    def items(self):
        return [("caller", STSCallerPage)]

class STSCallerPage(ObjectPage):
    def canonical(self):
        return ["sts", "caller"]

    def object(self):
        client = session.client("sts")
        info = client.get_caller_identity()
        del(info["ResponseMetadata"])
        return info

####################################################################################################

