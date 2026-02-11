import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as rds from "aws-cdk-lib/aws-rds";
import * as path from "path";
import { Construct } from "constructs";

interface RecipehubStackProps extends cdk.StackProps {
  secretKey: string;
  openaiApiKey: string;
}

export class RecipehubStack extends cdk.Stack {
  public readonly apiUrl: cdk.CfnOutput;
  public readonly dbEndpoint: cdk.CfnOutput;

  constructor(scope: Construct, id: string, props: RecipehubStackProps) {
    super(scope, id, props);

    // Create VPC for RDS (using default free-tier friendly config)
    const vpc = new ec2.Vpc(this, "RecipehubVpc", {
      maxAzs: 2,
      natGateways: 0, // No NAT Gateway to stay free
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: "public",
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
    });

    // Security group for RDS - allows public access (secured by password + SSL)
    const dbSecurityGroup = new ec2.SecurityGroup(this, "DbSecurityGroup", {
      vpc,
      description: "Security group for RecipeHub RDS",
      allowAllOutbound: true,
    });

    // Allow PostgreSQL access from anywhere (secured by credentials)
    dbSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(5432),
      "Allow PostgreSQL access"
    );

    // Create RDS PostgreSQL instance (Free Tier eligible)
    const database = new rds.DatabaseInstance(this, "RecipehubDatabase", {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MICRO
      ),
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      securityGroups: [dbSecurityGroup],
      databaseName: "recipehub",
      credentials: rds.Credentials.fromGeneratedSecret("postgres", {
        secretName: "recipehub-db-credentials",
      }),
      allocatedStorage: 20,
      maxAllocatedStorage: 20, // Prevent auto-scaling to stay free
      publiclyAccessible: true,
      deletionProtection: false,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For dev - change for prod
      backupRetention: cdk.Duration.days(0), // Disable backups for free tier
    });

    // Build DATABASE_URL from RDS instance
    const dbUrl = `postgresql://postgres:${database.secret?.secretValueFromJson("password").unsafeUnwrap()}@${database.instanceEndpoint.hostname}:5432/recipehub`;

    // Create Lambda function from Docker image
    const backendFunction = new lambda.DockerImageFunction(
      this,
      "RecipehubBackendFunction",
      {
        functionName: "recipehub-backend",
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, "../..") // Points to recipe-maker-backend folder
        ),
        memorySize: 512,
        timeout: cdk.Duration.seconds(30),
        environment: {
          DATABASE_URL: dbUrl,
          SECRET_KEY: props.secretKey,
          OPENAI_API_KEY: props.openaiApiKey,
        },
        architecture: lambda.Architecture.X86_64,
      }
    );

    // Add Function URL for public HTTP access
    const functionUrl = backendFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
        allowCredentials: true,
      },
    });

    // Output the API URL
    this.apiUrl = new cdk.CfnOutput(this, "ApiUrl", {
      value: functionUrl.url,
      description: "RecipeHub Backend API URL",
      exportName: "RecipehubApiUrl",
    });

    // Output the RDS endpoint for migrations
    this.dbEndpoint = new cdk.CfnOutput(this, "DbEndpoint", {
      value: database.instanceEndpoint.hostname,
      description: "RDS PostgreSQL Endpoint",
      exportName: "RecipehubDbEndpoint",
    });

    // Output secret ARN for retrieving credentials
    new cdk.CfnOutput(this, "DbSecretArn", {
      value: database.secret?.secretArn || "",
      description: "ARN of the database credentials secret",
      exportName: "RecipehubDbSecretArn",
    });
  }
}
