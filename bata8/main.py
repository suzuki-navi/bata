
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

        page = CloudWatchEventsRulePage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        page = ECSClusterPage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        page = GlueDatabasePage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        page = GlueTablePage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        page = LambdaFunctionPage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        page = S3KeyPage.page_from_arn(arn, account_id, region)
        if page != None:
            return page

        return None

####################################################################################################

def main():
    GlobalPage().exec(args)

if __name__ == "__main__":
    main()

####################################################################################################
