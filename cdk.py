from typing import Optional

from aws_cdk import aws_certificatemanager as cert_manager
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_s3 as s3
from aws_cdk import core

BASE_AMI = "ami-0c1d8fd38c915fb8b"
KEY_NAME = "property-dev"


class WebInstance(core.Construct):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc: ec2.Vpc,
        ami_id: str = BASE_AMI,
        instance_type: str = "t3.small",
        key_name: str = KEY_NAME,
        public_subnet_id: Optional[str] = None,
        web_group: Optional[ec2.SecurityGroup] = None,
        eip: Optional[ec2.CfnEIP] = None,
        role: Optional[iam.Role] = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)  # noqa

        self._web_sg = web_group
        self._public_subnet_id = public_subnet_id
        self._eip = eip
        self._security_groups = []

        self.role = role

        if not self.role:
            self.role = iam.Role(self, f"{id}-role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        if not self._eip:
            self._eip = ec2.CfnEIP(self, f"{id}-eip", domain="vpc")

        if not self._public_subnet_id:
            self._public_subnet_id = vpc.public_subnets[0].subnet_id

        if not self._web_sg:
            sg = ec2.SecurityGroup(self, f"{id}-web-sg", vpc=vpc, security_group_name=f"{id}-web")
            sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
            sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))
            sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
            self._web_sg = sg

        self.instance_type = instance_type
        self.key_name = key_name

        self._profile = iam.CfnInstanceProfile(self, f"{id}-profile", roles=[self.role.role_name])

        self._instance = ec2.CfnInstance(
            self,
            f"{id}-ec2",
            image_id=ami_id,
            instance_type=instance_type,
            key_name=self.key_name,
            monitoring=True,
            subnet_id=self._public_subnet_id,
            iam_instance_profile=self._profile.ref,
            security_group_ids=[self._web_sg.security_group_id],
        )

        eip_assoc = ec2.CfnEIPAssociation(  # noqa
            self, f"{id}-eip-assoc", instance_id=self._instance.ref, allocation_id=self._eip.attr_allocation_id
        )

    @property
    def ref(self) -> str:
        return self._instance.ref

    @property
    def public_ip_address(self) -> str:
        return self._eip.ref

    @property
    def security_group(self) -> ec2.SecurityGroup:
        return self._web_sg


class NetworkResources(core.Stack):

    ZONE_ID = "Z1HSX0WTG7HRXZ"
    ZONE_DOMAIN = "property_app.dev."
    WILDCARD_CERT_ARN = "arn:aws:acm:us-east-1:663370156182:certificate/53d897b9-3f17-4b96-b6bf-7bc2a8d188a2"

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            f"{id}-vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(name=f"{id}-public", subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name=f"{id}-isolated", subnet_type=ec2.SubnetType.ISOLATED),
            ],
        )

        self.zone = route53.HostedZone.from_hosted_zone_attributes(
            self, f"{id}-zone", hosted_zone_id=self.ZONE_ID, zone_name=self.ZONE_DOMAIN
        )

        self.wildcard_cert = cert_manager.Certificate.from_certificate_arn(
            self, f"{id}-wildcard-cert", self.WILDCARD_CERT_ARN
        )

        sg = ec2.SecurityGroup(self, f"{id}-web-sg", vpc=self.vpc, security_group_name=f"{id}-web")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        self.web_sg = sg


class DBResources(core.Stack):
    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, zone: route53.HostedZone, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc
        self.zone = zone

        self.secret = rds.DatabaseSecret(self, f"{id}-db-secret", username="app")

        self.db = rds.DatabaseInstance(
            self,
            f"{id}-db",
            master_username=self.secret.secret_value_from_json("username").to_string(),
            master_user_password=self.secret.secret_value_from_json("password"),
            storage_encrypted=False,
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            allocated_storage=100,
            allow_major_version_upgrade=False,
            database_name="app",
            engine_version="11.4",
            instance_class=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=self.vpc,
            auto_minor_version_upgrade=True,
            delete_automated_backups=True,
            iam_authentication=True,
            instance_identifier=f"{id}",
            multi_az=False,
            vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
        )

        self.secret.add_target_attachment(f"{id}-db-secret-attach", target=self.db)


class AppAssets(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.ecr_proxy = ecr.Repository(self, f"{id}-proxy", repository_name=f"{id}-proxy")
        self.ecr_app = ecr.Repository(self, f"{id}-app", repository_name=f"{id}-app")

        self.data_bucket = s3.Bucket(
            self, f"{id}-data-bucket", bucket_name="almostprod-property_app-data", encryption=s3.BucketEncryption.S3_MANAGED
        )


class AppResources(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc: ec2.Vpc,
        zone: route53.HostedZone,
        db: rds.DatabaseInstance,
        db_secret: rds.DatabaseSecret,
        web_group: ec2.SecurityGroup,
        assets: core.Stack,
        data_bucket: s3.Bucket,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc
        self.zone = zone
        self.db = db
        self.db_secret = db_secret
        self.data_bucket = data_bucket

        self.ecr_proxy = assets.ecr_proxy
        self.ecr_app = assets.ecr_app

        self.instance = WebInstance(self, f"{id}-app-web", self.vpc, web_group=web_group)

        self.ecr_proxy.grant_pull_push(self.instance.role)
        self.ecr_app.grant_pull_push(self.instance.role)

        self.root_record = route53.ARecord(
            self,
            f"{id}-root-record",
            target=route53.RecordTarget.from_ip_addresses(self.instance.public_ip_address),
            zone=self.zone,
            ttl=core.Duration.minutes(1),
        )

        self.db.connections.allow_default_port_from(web_group)
        self.db_secret.grant_read(self.instance.role)
        self.data_bucket.grant_read_write(self.instance.role)


app = core.App()

network = NetworkResources(app, "prod-bb-dev-net")
db = DBResources(app, "prod-bb-dev-db", network.vpc, network.zone)
assets = AppAssets(app, "prod-bb-dev-assets")
app_core = AppResources(
    app, "prod-bb-dev-app", network.vpc, network.zone, db.db, db.secret, network.web_sg, assets, assets.data_bucket
)

app.synth()
