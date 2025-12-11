import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as path from "path";
import { Construct } from "constructs";

interface RecipehubStackProps extends cdk.StackProps {
  databaseUrl: string;
  secretKey: string;
  openaiApiKey: string;
}

export class RecipehubStack extends cdk.Stack {
  public readonly apiUrl: cdk.CfnOutput;

  constructor(scope: Construct, id: string, props: RecipehubStackProps) {
    super(scope, id, props);

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
          DATABASE_URL: props.databaseUrl,
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
  }
}
