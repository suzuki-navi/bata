
from bata8.lib import *

from bata8.awscloudwatch import *
from bata8.awscode import *
from bata8.awsecr import *
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
            ("cloudwatch", CloudWatchPage),
            ("ecr", ECRPage),
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

####################################################################################################

def main():
    GlobalPage().exec(args)

if __name__ == "__main__":
    main()

####################################################################################################
