from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "PortfolioBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        cloudfront.Distribution(
            self,
            "myDist",
            default_behavior=cloudfront.BehaviorOptions(
            origin=origins.S3BucketOrigin.with_origin_access_control(bucket)
            )   
        )
        table = dynamodb.TableV2(
            self,
            "PortFolioTable",
            partition_key=dynamodb.Attribute(
            name="pk",
            type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )