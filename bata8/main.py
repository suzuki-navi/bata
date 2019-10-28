
import re

from bata8.lib import *

from bata8.awscloudformation import *
from bata8.awscloudwatch import *
from bata8.awscode import *
from bata8.awsec2 import *
from bata8.awsecr import *
from bata8.awsecs import *
from bata8.awsglue import *
from bata8.awsiam import *
from bata8.awslambda import *
from bata8.awsrds import *
from bata8.awsredshift import *
from bata8.awss3 import *
from bata8.awssupport import *
from bata8.awsvpc import *

####################################################################################################

class GlobalPage(MenuPage):
    def items(self):
        return [
            ("code", CodePage),
            ("cloudformation", CloudFormationPage),
            ("cloudwatch", CloudWatchPage),
            ("ec2", EC2Page),
            ("ecr", ECRPage),
            ("ecs", ECSPage),
            ("glue", GluePage),
            ("iam", IAMPage),
            ("lambda", LambdaPage),
            ("rds", RDSPage),
            ("redshift", RedshiftPage),
            ("s3", S3Page),
            ("sts", STSPage),
            ("support", SupportPage),
            ("vpc", VPCPage),
        ]

    def dig(self, arg):
        if re.match("\\Aarn:.+", arg):
            return GlobalPage.page_from_arn(arg)
        if re.match("\\As3://", arg):
            return S3Page.page_from_uri(arg)
        return super().dig(arg)

    @classmethod
    def page_from_arn(cls, arn):
        account_id = fetch_account_id()
        match = re.match(f"\\Aarn:aws:ecs:{region}:{account_id}:cluster/(.*)\\Z", arn)
        if match:
            return ECSClusterPage(match.group(1))
        match = re.match("\\Aarn:aws:s3:::(.+?)/(.*)\\Z", arn)
        if match:
            return S3KeyPage(match.group(1), match.group(2))
        match = re.match("\\Aarn:aws:s3:::(.+?)\\Z", arn)
        if match:
            return S3KeyPage(match.group(1), "")
        return None

####################################################################################################

def main():
    GlobalPage().exec(args)

if __name__ == "__main__":
    main()

####################################################################################################
