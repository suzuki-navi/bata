
import boto3
import botocore

from bata8.lib import *

####################################################################################################

class IAMPage(MenuPage):
    def items(self):
        return [
            ("groups", IAMGroupsPage),
            ("users", IAMUsersPage),
            ("roles", IAMRolesPage),
            ("policies", IAMPoliciesPage),
        ]

class IAMGroupsPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_groups(
        )
        items = []
        for elem in ls["Groups"]:
            items.append([elem["GroupName"], elem["GroupId"]])
        return items

    def detailPage(self, item):
        return IAMGroupPage(item[0])

class IAMGroupPage(MenuPage):
    def __init__(self, group_name):
        self.group_name = group_name

    def items(self):
        return [
            ("info", IAMGroupInfoPage),
            ("users", IAMGroupUsersPage),
            ("policies", IAMGroupPoliciesPage),
        ]

    def detailPage(self, item):
        return item[1](self.group_name)

class IAMGroupInfoPage(ObjectPage):
    def __init__(self, group_name):
        self.group_name = group_name

    def object(self):
        client = session.client("iam")
        info = client.get_group(
            GroupName = self.group_name,
        )
        return info["Group"]

class IAMGroupUsersPage(TablePage):
    def __init__(self, group_name):
        self.group_name = group_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.get_group(
            GroupName = self.group_name,
        )
        items = []
        for elem in ls["Users"]:
            items.append([elem["UserName"]])
        return items

    def detailPage(self, item):
        return IAMUserPage(item[0])

class IAMGroupPoliciesPage(TablePage):
    def __init__(self, group_name):
        self.group_name = group_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        items = []
        ls = client.list_group_policies(
            GroupName = self.group_name,
        )
        for elem in ls["PolicyNames"]:
            items.append([elem, "-"])
        ls = client.list_attached_group_policies(
            GroupName = self.group_name,
        )
        for elem in ls["AttachedPolicies"]:
            items.append([elem["PolicyName"], elem["PolicyArn"]])
        return items

    def detailPage(self, item):
        if item[1] == "-":
            return None
        return IAMPolicyPage(item[0], item[1])

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

class IAMUserPage(MenuPage):
    def __init__(self, user_name):
        self.user_name = user_name

    def items(self):
        return [
            ("info", IAMUserInfoPage),
            ("policies", IAMUserPoliciesPage),
        ]

    def detailPage(self, item):
        return item[1](self.user_name)

class IAMUserInfoPage(ObjectPage):
    def __init__(self, user_name):
        self.user_name = user_name

    def object(self):
        client = session.client("iam")
        info = client.get_user(
            UserName = self.user_name,
        )
        return info["User"]

class IAMUserPoliciesPage(TablePage):
    def __init__(self, user_name):
        self.user_name = user_name

    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        items = []
        ls = client.list_user_policies(
            UserName = self.user_name,
        )
        for elem in ls["PolicyNames"]:
            items.append([elem, "-"])
        ls = client.list_attached_user_policies(
            UserName = self.user_name,
        )
        for elem in ls["AttachedPolicies"]:
            items.append([elem["PolicyName"], elem["PolicyArn"]])
        return items

    def detailPage(self, item):
        if item[1] == "-":
            return None
        return IAMPolicyPage(item[0], item[1])

class IAMRolesPage(TablePage):
    def nameColIdx(self):
        return 0

    def items(self):
        client = session.client("iam")
        ls = client.list_roles(
            MaxItems = 1000,
        )
        items = []
        for elem in ls["Roles"]:
            items.append([elem["RoleName"], elem["Path"]])
        items.sort()
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

# これをIAMRolePageにしたほうがいいのかな?
class IAMRoleInfoPage(ObjectPage):
    def __init__(self, role_name):
        self.role_name = role_name
        self._info = None

    def _fetch_info(self):
        client = session.client("iam")
        info = client.get_role(
            RoleName = self.role_name,
        )
        return info["Role"]

    def info(self):
        if self._info == None:
            self._info = self._fetch_info();
        return self._info

    def arn(self):
        info = self.info()
        path = info["Path"]
        return "arn:aws:iam::{}:role{}{}".format(fetch_account_id(), path, self.role_name)

    def object(self):
        return self.info()

    @classmethod
    def page_from_arn(cls, arn, account_id, region):
        match = re.match(f"\\Aarn:aws:iam::{account_id}:role/(.+/)?([^/]+)\\Z", arn)
        if match:
            return IAMRoleInfoPage(match.group(2))

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

class IAMPolicyPage(MenuPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def items(self):
        return [
            ("info", IAMPolicyInfoPage),
            ("statement", IAMPolicyStatementPage),
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

class IAMPolicyStatementPage(ObjectPage):
    def __init__(self, policy_name, policy_arn):
        self.policy_name = policy_name
        self.policy_arn = policy_arn

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
        return version_meta["PolicyVersion"]["Document"]["Statement"]

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

