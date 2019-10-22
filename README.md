# bata8

AWSリソースを確認するツール


## Install

CentOS 7

    $ sudo yum install -y python3 python3-pip git
    $ git clone https://github.com/suzuki-navi/bata8.git
    $ cd bata8
    $ sudo pip3 install -e .

Ubuntu 19.10

    $ sudo apt update
    $ sudo apt install -y python3 python3-pip git
    $ git clone https://github.com/suzuki-navi/bata8.git
    $ cd bata8
    $ sudo pip3 install -e .


## Usage

    $ bata8
    $ bata8 ec2
    $ bata8 ec2 instances
    $ bata8 ec2 instances 0


## 対応しているメニュー

    parameters                                                                     type   implementing class
    
    code                                                                           Menu   awscode.CodePage
    code commit                                                                    Table  awscode.CodeCommitPage
    cloudformation                                                                 Menu   awscloudformation.CloudFormationPage
    cloudformation stacks                                                          Table  awscloudformation.CloudFormationStacksPage
    cloudformation stacks <STACK_NAME>                                             Object awscloudformation.CloudFormationStackPage
    cloudwatch                                                                     Menu   awscloudwatch.CloudWatchPage
    cloudwatch events                                                              Menu   awscloudwatch.CloudWatchEventsPage
    cloudwatch events rules                                                        Table  awscloudwatch.CloudWatchEventsRulesPage
    cloudwatch events rules <RULE_NAME>                                            Object awscloudwatch.CloudWatchEventsRulePage
    cloudwatch logs                                                                Table  awscloudwatch.CloudWatchLogsPage
    cloudwatch logs <LOG_GROUP_NAME>                                               Table  awscloudwatch.CloudWatchLogGroupPage
    cloudwatch logs <LOG_GROUP_NAME> <LOG_STREAM_NAME>                             Table  awscloudwatch.CloudWatchLogStreamEventsPage
    cloudwatch metrics                                                             Table  awscloudwatch.CloudWatchMetricsPage
    cloudwatch metrics --alt                                                       Menu   awscloudwatch.CloudWatchMetricsAltPage
    cloudwatch metrics --alt all                                                   Table  awscloudwatch.CloudWatchMetricsAllPage
    cloudwatch metrics <NAMESPACE>                                                 Table  awscloudwatch.CloudWatchMetricsNamespacePage
    cloudwatch metrics <NAMESPACE> --alt                                           Menu   awscloudwatch.CloudWatchMetricsNamespaceAltPage
    cloudwatch metrics <NAMESPACE> --alt all                                       Table  awscloudwatch.CloudWatchMetricsAllPage
    cloudwatch metrics <NAMESPACE> <METRIC_NAME>                                   Table  awscloudwatch.CloudWatchMetricsAllPage
    cloudwatch metrics <NAMESPACE> <METRIC_NAME> <DIMENSIONS>                      Table  awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    ec2                                                                            Menu   awsec2.EC2Page
    ec2 instances                                                                  Table  awsec2.EC2InstancesPage
    ec2 instances <INSTANCE_ID>                                                    Object awsec2.EC2InstancePage
    ec2 instances <INSTANCE_ID> --alt                                              Menu   awsec2.EC2InstanceAltPage
    ec2 instances <INSTANCE_ID> --alt vpc                                          Object awsvpc.VPCVPCPage
    ecr                                                                            Menu   awsecr.ECRPage
    ecr repositories                                                               Table  awsecr.ECRRepositoriesPage
    ecr repositories <REPOSITORY_NAME>                                             Object awsecr.ECRRepositoryPage
    ecr repositories <REPOSITORY_NAME> --alt                                       Menu   awsecr.ECRRepositoryAltPage
    ecr repositories <REPOSITORY_NAME> --alt images                                Table  awsecr.ECRRepositoryImagesPage
    ecr repositories <REPOSITORY_NAME> --alt images <IMAGE_ID>                     Object awsecr.ECRRepositoryImagePage
    ecs                                                                            Menu   awsecs.ECSPage
    ecs clusters                                                                   Table  awsecs.ECSClustersPage
    ecs tasks                                                                      Table  awsecs.ECSTasksPage
    glue                                                                           Menu   awsglue.GluePage
    glue databases                                                                 Table  awsglue.GlueDatabasesPage
    glue databases <DATABASE_NAME>                                                 Table  awsglue.GlueDatabasePage
    glue databases <DATABASE_NAME> --alt                                           Object awsglue.GlueDatabaseAltPage
    glue databases <DATABASE_NAME> <TABLE_NAME>                                    Object awsglue.GlueTablePage
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt                              Menu   awsglue.GlueTableAltPage
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt partitions                   Table  awsglue.GlueTablePartitionsPage
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt partitions <PARTITION_VALUE> Object awsglue.GlueTablePartitionPage
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt location                     Table  awss3.S3KeyPage
    glue connections                                                               Table  awsglue.GlueConnectionsPage
    glue connections <CONNECTION_NAME>                                             Menu   awsglue.GlueConnectionPage
    glue crawlers                                                                  Table  awsglue.GlueCrawlersPage
    glue crawlers <CRAWLER_NAME>                                                   Object awsglue.GlueCrawlerPage
    glue jobs                                                                      Table  awsglue.GlueJobsPage
    glue jobs <JOB_NAME>                                                           Menu   awsglue.GlueJobPage
    glue jobs <JOB_NAME> info                                                      Object awsglue.GlueJobInfoPage
    glue jobs <JOB_NAME> bookmark                                                  Object awsglue.GlueJobBookmarkPage
    glue jobs <JOB_NAME> history                                                   Table  awsglue.GlueJobHistoryPage
    glue jobs <JOB_NAME> history <RUN_ID>                                          Object awsglue.GlueJobRunPage
    glue jobs <JOB_NAME> role                                                      Table  awsiam.IAMRolePage
    iam                                                                            Menu   awsiam.IAMPage
    iam users                                                                      Table  awsiam.IAMUsersPage
    iam users <USER_NAME>                                                          Menu   awsiam.IAMUserPage
    iam users <USER_NAME> info                                                     Object awsiam.IAMUserInfoPage
    iam users <USER_NAME> policies                                                 Table  awsiam.IAMUserPoliciesPage
    iam users <USER_NAME> policies <POLICY_NAME>                                   Menu   awsiam.IAMPolicyPage
    iam roles                                                                      Table  awsiam.IAMRolesPage
    iam roles <ROLE_NAME>                                                          Table  awsiam.IAMRolePage
    iam roles <ROLE_NAME> --alt                                                    Menu   awsiam.IAMRoleAltPage
    iam roles <ROLE_NAME> --alt info                                               Object awsiam.IAMRoleInfoPage
    iam roles <ROLE_NAME> <POLICY_NAME>                                            Not implemented
    iam policies                                                                   Table  awsiam.IAMPoliciesPage
    iam policies <POLICY_NAME>                                                     Menu   awsiam.IAMPolicyPage
    iam policies <POLICY_NAME> info                                                Object awsiam.IAMPolicyInfoPage
    iam policies <POLICY_NAME> statement                                           Object awsiam.IAMPolicyStatementPage
    iam policies <POLICY_NAME> versions                                            Table  awsiam.IAMPolicyVersionsPage
    iam policies <POLICY_NAME> versions <VERSION_ID>                               Object awsiam.IAMPolicyVersionPage
    lambda                                                                         Menu   awslambda.LambdaPage
    lambda functions                                                               Table  awslambda.LambdaFunctionsPage
    lambda functions <FUNCTION_NAME>                                               Menu   awslambda.LambdaFunctionPage
    lambda functions <FUNCTION_NAME> code                                          Object awslambda.LambdaFunctionCodePage
    lambda functions <FUNCTION_NAME> configuration                                 Object awslambda.LambdaFunctionConfigurationPage
    lambda functions <FUNCTION_NAME> aliases                                       Not implemented
    lambda functions <FUNCTION_NAME> metrics                                       Menu   awslambda.LambdaFunctionMetricsPage
    lambda functions <FUNCTION_NAME> metrics duration                              Menu   awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    lambda functions <FUNCTION_NAME> metrics errors                                Menu   awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    lambda functions <FUNCTION_NAME> metrics invocations                           Menu   awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    lambda functions <FUNCTION_NAME> metrics throttles                             Menu   awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    rds                                                                            Menu   awsrds.RDSPage
    rds databases                                                                  Table  awsrds.RDSDatabasesPage
    rds databases <DATABASE_INSTANCE_IDENTIFIER>                                   Not implemented awsrds.RDSDatabasePage
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt                             Menu   awsrds.RDSDatabaseAltPage
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt info                        Object awsrds.RDSDatabaseInfoPage
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt vpc                         Object awsvpc.VPCVPCPage
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt snapshots                   Table  awsrds.RDSSnapshotsPage
    rds snapshots                                                                  Table  awsrds.RDSSnapshotsPage
    rds snapshots <SNAPSHOT_IDENTIFIER>                                            Object awsrds.RDSSnapshotPage
    rds snapshots <SNAPSHOT_IDENTIFIER> --alt                                      Menu   awsrds.RDSSnapshotAltPage
    rds snapshots <SNAPSHOT_IDENTIFIER> --alt database                             Not implemented awsrds.RDSDatabasePage
    rds snapshots <SNAPSHOT_IDENTIFIER> --alt vpc                                  Object awsvpc.VPCVPCPage
    redshift                                                                       Menu   awsredshift.RedshiftPage
    redshift clusters                                                              Table  awsredshift.RedshiftClustersPage
    redshift clusters <CLUSTER_IDENTIFIER>                                         Not implemented awsredshift.RedshiftClusterPage
    redshift clusters <CLUSTER_IDENTIFIER> --alt                                   Menu   awsredshift.RedshiftClusterAltPage
    redshift clusters <CLUSTER_IDENTIFIER> --alt info                              Object awsredshift.RedshiftClusterInfoPage
    redshift clusters <CLUSTER_IDENTIFIER> --alt vpc                               Object awsvpc.VPCVPCPage
    redshift clusters <CLUSTER_IDENTIFIER> --alt roles                             Table  awsredshift.RedshiftClusterRolesPage
    redshift clusters <CLUSTER_IDENTIFIER> --alt roles <ROLE_NAME>                 Table  awsiam.IAMRolePage
    s3                                                                             Table  awss3.S3Page
    s3 buckets                                                                     Table  awss3.S3BucketsPage
    s3 buckets <BUCKET_NAME>                                                       Table  awss3.S3KeyPage
    s3 buckets <BUCKET_NAME> --alt                                                 Menu   awss3.S3BucketMetaPage
    s3 buckets <BUCKET_NAME> --alt versioning                                      Object awss3.S3BucketMetaVersioningPage
    s3 buckets <BUCKET_NAME> --alt policy                                          Object awss3.S3BucketMetaPolicyPage
    s3 buckets <BUCKET_NAME> --alt metrics                                         Menu   awss3.S3BucketMetaMetricsPage
    s3 buckets <BUCKET_NAME> --alt metrics size                                    Table  awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    s3 buckets <BUCKET_NAME> --alt metrics count                                   Table  awscloudwatch.CloudWatchMetricsNamespaceMetricDimensionPage
    s3 buckets <BUCKET_NAME> <PREFIX> ...                                          Table  awss3.S3KeyPage
    s3 buckets <BUCKET_NAME> <PREFIX> ... <KEY_NAME>                               Object awss3.S3KeyPage
    sts                                                                            Menu   awsiam.STSPage
    sts caller                                                                     Object awsiam.STSCallerPage
    support                                                                        Menu   awssupport.SupportPage
    support cases                                                                  Table  awssupport.SupportCasesPage
    support cases <CASE_ID>                                                        Object awssupport.SupportCasePage
    vpc                                                                            Menu   awsvpc.VPCPage
    vpc vpcs                                                                       Table  awsvpc.VPCVPCsPage
    vpc vpcs <VPC_ID>                                                              Object awsvpc.VPCVPCPage
    vpc vpcs <VPC_ID> --alt                                                        Menu   awsvpc.VPCVPCAltPage
    vpc vpcs <VPC_ID> --alt subnets                                                Table  awsvpc.VPCSubnetsPage
    vpc vpcs <VPC_ID> --alt subnets <SUBNET_ID>                                    Object awsvpc.VPCSubnetPage
    vpc subnets                                                                    Table  awsvpc.VPCSubnetsPage
    vpc subnets <SUBNET_ID>                                                        Object awsvpc.VPCSubnetPage


