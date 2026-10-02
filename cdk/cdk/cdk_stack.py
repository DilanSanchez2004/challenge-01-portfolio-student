from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_dynamodb as dynamodb,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    aws_iam as iam


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

        distribucion = cloudfront.Distribution(
            self,
            "myDist",
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_200,
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

        s3deploy.BucketDeployment(
            self,
            "DeployPortfolio",
            sources=[s3deploy.Source.asset("../application")],
            destination_bucket=bucket,
            distribution=distribucion, # Invalida el caché en CloudFront al actualizar los archivos
        )

        # 1. Rol con permiso de solo lectura para DynamoDB
        dynamo_reader_role = iam.Role(
            self,
            "DynamoDBReaderRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Rol con acceso de solo lectura a la tabla de portafolios"
        )
        # Aplicamos el principio de mínimo privilegio otorgando solo lectura sobre la tabla
        table.grant_read_data(dynamo_reader_role)

        # 2. Rol con permiso de carga/escritura para S3
        s3_uploader_role = iam.Role(
            self,
            "S3UploaderRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Rol con permiso de escritura para subir archivos al bucket"
        )
        # Aplicamos el principio de mínimo privilegio otorgando solo escritura en el bucket
        bucket.grant_write(s3_uploader_role)

        CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{distribucion.distribution_domain_name}"
        )