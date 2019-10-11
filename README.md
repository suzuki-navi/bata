# bata

自作aws cliツール

## 利用方法

dockerがインストールされていれば

    $ ./bin/bata PARAMETERS ...

dockerなしの環境で動かすには Dockerfile 参照。


## 対応しているメニュー

    code                                                                        -> Menu
    code commit                                                                 -> Table
    cloudwatch                                                                  -> Menu
    cloudwatch events                                                           -> Menu
    cloudwatch events rules                                                     -> Table
    cloudwatch events rules <RULE_NAME>                                         -> Object
    cloudwatch logs                                                             -> Table
    cloudwatch logs <LOG_GROUP_NAME>                                            -> Table
    cloudwatch logs <LOG_GROUP_NAME> <LOG_STREAM_NAME>                          -> Table
    cloudwatch metrics                                                          -> Table
    cloudwatch metrics --alt                                                    -> Menu
    cloudwatch metrics --alt all                                                -> Table
    cloudwatch metrics <NAMESPACE>                                              -> Table
    cloudwatch metrics <NAMESPACE> --alt                                        -> Menu
    cloudwatch metrics <NAMESPACE> --alt all                                    -> Table
    cloudwatch metrics <NAMESPACE> <METRIC_NAME>                                -> Table
    cloudwatch metrics <NAMESPACE> <METRIC_NAME> <DIMENSIONS>                   -> Table
    ecr                                                                         -> Menu
    ecr repositories                                                            -> Table
    ecr repositories <REPOSITORY_NAME>                                          -> Table
    ecr repositories <REPOSITORY_NAME> <IMAGE_ID>                               -> Object
    glue                                                                        -> Menu
    glue databases                                                              -> Table
    glue databases <DATABASE_NAME>                                              -> Table
    glue databases <DATABASE_NAME> --alt                                        -> Object
    glue databases <DATABASE_NAME> <TABLE_NAME>                                 -> Object
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt                           -> Menu
    glue databases <DATABASE_NAME> <TABLE_NAME> --alt partitions                -> Table
    glue connections                                                            -> Table
    glue connections <CONNECTION_NAME>                                          -> Menu
    glue crawlers                                                               -> Table
    glue crawlers <CRAWLER_NAME>                                                -> Object
    glue jobs                                                                   -> Table
    glue jobs <JOB_NAME>                                                        -> Menu
    glue jobs <JOB_NAME> info                                                   -> Object
    glue jobs <JOB_NAME> bookmark                                               -> Object
    glue jobs <JOB_NAME> history                                                -> Table
    glue jobs <JOB_NAME> history <RUN_ID>                                       -> Object
    iam                                                                         -> Menu
    iam users                                                                   -> Table
    iam users <USER_NAME>                                                       -> Object
    iam roles                                                                   -> Table
    iam roles <ROLE_NAME>                                                       -> Table
    iam roles <ROLE_NAME> --alt                                                 -> Menu
    iam roles <ROLE_NAME> --alt info                                            -> Object
    iam roles <ROLE_NAME> <POLICY_NAME>                                         -> Not implemented
    iam policies                                                                -> Table
    iam policies <POLICY_NAME>                                                  -> Object
    iam policies <POLICY_NAME> --alt                                            -> Menu
    iam policies <POLICY_NAME> --alt info                                       -> Object
    iam policies <POLICY_NAME> --alt versions                                   -> Table
    iam policies <POLICY_NAME> --alt versions <VERSION_ID>                      -> Object
    lambda                                                                      -> Menu
    lambda functions                                                            -> Table
    lambda functions <FUNCTION_NAME>                                            -> Menu
    lambda functions <FUNCTION_NAME> code                                       -> Object
    lambda functions <FUNCTION_NAME> configuration                              -> Object
    lambda functions <FUNCTION_NAME> aliases                                    -> Not implemented
    lambda functions <FUNCTION_NAME> metrics                                    -> Menu
    rds                                                                         -> Menu
    rds databases                                                               -> Table
    rds databases <DATABASE_INSTANCE_IDENTIFIER>                                -> Not implemented
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt                          -> Menu
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --alt info                     -> Object
    redshift                                                                    -> Menu
    redshift clusters                                                           -> Table
    redshift clusters <CLUSTER_IDENTIFIER>                                      -> Not implemented
    redshift clusters <CLUSTER_IDENTIFIER> --alt                                -> Menu
    redshift clusters <CLUSTER_IDENTIFIER> --alt info                           -> Object
    redshift clusters <CLUSTER_IDENTIFIER> --alt vpc                            -> Object
    redshift clusters <CLUSTER_IDENTIFIER> --alt roles                          -> Table
    redshift clusters <CLUSTER_IDENTIFIER> --alt roles <ROLE_NAME>              -> Table
    s3                                                                          -> Table
    s3 buckets                                                                  -> Table
    s3 buckets <BUCKET_NAME>                                                    -> Table
    s3 buckets <BUCKET_NAME> --alt                                              -> Menu
    s3 buckets <BUCKET_NAME> --alt versioning                                   -> Object
    s3 buckets <BUCKET_NAME> --alt policy                                       -> Object
    s3 buckets <BUCKET_NAME> <PREFIX> ...                                       -> Table
    s3 buckets <BUCKET_NAME> <PREFIX> ... <KEY_NAME>                            -> Object
    sts                                                                         -> Menu
    sts caller                                                                  -> Object
    support                                                                     -> Menu
    support cases                                                               -> Table
    support cases <CASE_ID>                                                     -> Object
    vpc                                                                         -> Menu
    vpc vpcs                                                                    -> Table
    vpc vpcs <VPC_ID>                                                           -> Object
    vpc vpcs <VPC_ID> --alt                                                     -> Menu
    vpc vpcs <VPC_ID> --alt subnets                                             -> Table
    vpc vpcs <VPC_ID> --alt subnets <SUBNET_ID>                                 -> Object
    vpc subnets                                                                 -> Table
    vpc subnets <SUBNET_ID>                                                     -> Object


