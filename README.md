# awsboto

自作aws cliツール

## 対応しているメニュー

    cloudwatch                                                                  -> Menu
    cloudwatch events                                                           -> Menu
    cloudwatch events rules                                                     -> Table
    cloudwatch events rules <RULE_NAME>                                         -> Object
    cloudwatch logs                                                             -> Table
    cloudwatch logs <LOG_GROUP_NAME>                                            -> Table
    cloudwatch logs <LOG_GROUP_NAME> <LOG_STREAM_NAME>                          -> Table
    cloudwatch logs <LOG_GROUP_NAME> --put                                      -> Table <- None
    ecr                                                                         -> Menu
    ecr repositories                                                            -> Table
    ecr repositories <REPOSITORY_NAME>                                          -> Table
    ecr repositories <REPOSITORY_NAME> <IMAGE_ID>                               -> Object
    glue                                                                        -> Menu
    glue databases                                                              -> Table
    glue databases <DATABASE_NAME>                                              -> Table
    glue databases <DATABASE_NAME> <TABLE_NAME>                                 -> Object
    glue databases <DATABASE_NAME> --meta                                       -> Object
    glue crawlers                                                               -> Table
    glue crawlers <CRAWLER_NAME>                                                -> Object
    glue jobs                                                                   -> Table
    glue jobs <JOB_NAME>                                                        -> Menu
    glue jobs <JOB_NAME> info                                                   -> Object
    glue jobs <JOB_NAME> history                                                -> Table
    glue jobs <JOB_NAME> history <RUN_ID>                                       -> Object
    iam                                                                         -> Menu
    iam users                                                                   -> Table
    iam users <USER_NAME>                                                       -> Object
    iam roles                                                                   -> Table
    iam roles <ROLE_NAME>                                                       -> Table
    iam roles <ROLE_NAME> <POLICY_NAME>                                         -> Not implemented
    iam roles <ROLE_NAME> --meta                                                -> Menu
    iam roles <ROLE_NAME> --meta info                                           -> Object
    iam policies                                                                -> Table
    iam policies <POLICY_NAME>                                                  -> Object
    iam policies <POLICY_NAME> --meta                                           -> Menu
    iam policies <POLICY_NAME> --meta info                                      -> Object
    iam policies <POLICY_NAME> --meta versions                                  -> Table
    iam policies <POLICY_NAME> --meta versions <VERSION_ID>                     -> Object
    lambda                                                                      -> Menu
    lambda functions                                                            -> Table
    lambda functions <FUNCTION_NAME>                                            -> Menu
    lambda functions <FUNCTION_NAME> code                                       -> Object
    lambda functions <FUNCTION_NAME> configuration                              -> Object
    lambda functions <FUNCTION_NAME> aliases                                    -> Not implemented
    rds                                                                         -> Menu
    rds databases                                                               -> Table
    rds databases <DATABASE_INSTANCE_IDENTIFIER>                                -> Not implemented
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --meta                         -> Menu
    rds databases <DATABASE_INSTANCE_IDENTIFIER> --meta info                    -> Object
    s3                                                                          -> Table
    s3 buckets                                                                  -> Table
    s3 buckets <BUCKET_NAME>                                                    -> Table
    s3 buckets <BUCKET_NAME> <PREFIX> ...                                       -> Table
    s3 buckets <BUCKET_NAME> <PREFIX> ... <KEY_NAME>                            -> Not implemented
    s3 buckets <BUCKET_NAME> --meta                                             -> Menu
    s3 buckets <BUCKET_NAME> --meta versioning                                  -> Object
    s3 buckets <BUCKET_NAME> --meta policy                                      -> Object


